import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../data/scan_history_db.dart';
import '../models/coin_summary.dart';
import '../models/scan_record.dart';
import '../utils/currency_formatting.dart';
import '../widgets/action_button.dart';
import '../widgets/analyze_loading_overlay.dart';
import '../widgets/background_layer.dart';
import '../widgets/calibration_mode_card.dart';
import '../widgets/error_strip.dart';
import '../widgets/result_card.dart';
import '../widgets/small_image_frame.dart';
import '../theme/app_palette.dart';
import 'settings_screen.dart';

class CoinDetectorScreen extends StatefulWidget {
  const CoinDetectorScreen({
    super.key,
    required this.themeMode,
    required this.onThemeChanged,
  });

  final ThemeMode themeMode;
  final ValueChanged<ThemeMode> onThemeChanged;

  @override
  State<CoinDetectorScreen> createState() => _CoinDetectorScreenState();
}

class _CoinDetectorScreenState extends State<CoinDetectorScreen> {
  static const Map<String, List<int>> _currencyDenominations = {
    'RON': [1, 5, 10, 50],
    'EUR': [1, 2, 5, 10, 20, 50, 100, 200],
    'USD': [1, 5, 10, 25, 50, 100],
    'GBP': [1, 2, 5, 10, 20, 50, 100, 200],
  };

  static String _defaultApiBase() {
    // Web and Android emulator need different loopback hosts for local FastAPI.
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }

    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:8000';
      default:
        return 'http://127.0.0.1:8000';
    }
  }

  final ImagePicker _picker = ImagePicker();
  late final String _apiBase = _defaultApiBase();
  static const String _apiKey = String.fromEnvironment('COIN_COUNTER_API_KEY', defaultValue: '');
  static const String _userId = String.fromEnvironment('COIN_COUNTER_USER_ID', defaultValue: 'flutter-local-user');
  final ScrollController _resultScrollController = ScrollController();

  XFile? _inputImage;
  Uint8List? _inputBytes;
  Uint8List? _outputBytes;
  List<CoinSummary> _summaries = const [];
  int _totalValue = 0;
  int _totalCount = 0;
  bool _isLoading = false;
  bool _autoMode = true;
  bool _isAddingMore = false;
  int? _activeScanId;
  String _currencyCode = 'RON';
  String _resultCurrencyCode = 'RON';
  int _coinValue = 50;
  String? _error;

  List<int> get _availableCoinValues => _currencyDenominations[_currencyCode] ?? const [1, 5, 10, 50];

  @override
  void dispose() {
    _resultScrollController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final file = await _picker.pickImage(source: source);
    if (file == null) return;

    final bytes = await file.readAsBytes();
    // Keep previous results when user is in "add more" flow; otherwise start a clean scan.
    final hasExistingResults = _summaries.isNotEmpty;
    setState(() {
      _inputImage = file;
      _inputBytes = bytes;
      _isAddingMore = hasExistingResults;
      if (!hasExistingResults) {
        _outputBytes = null;
        _summaries = const [];
        _totalValue = 0;
        _totalCount = 0;
      }
      _error = null;
    });
  }

  void _resetResult() {
    setState(() {
      _inputImage = null;
      _inputBytes = null;
      _outputBytes = null;
      _summaries = const [];
      _totalCount = 0;
      _totalValue = 0;
      _isAddingMore = false;
      _activeScanId = null;
      _error = null;
    });
  }

  Future<void> _openSettingsScreen() async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => SettingsScreen(
          themeMode: widget.themeMode,
          onThemeChanged: widget.onThemeChanged,
        ),
      ),
    );
  }

  Future<void> _persistCurrentScan({required bool isAddMoreFlow}) async {
    final record = ScanRecord(
      id: _activeScanId ?? 0,
      timestamp: DateTime.now(),
      currencyCode: _resultCurrencyCode,
      totalCount: _totalCount,
      totalValue: _totalValue,
      summaries: _summaries
          .map(
            (summary) => ScanSummaryEntry(
              coinValue: summary.coinValue,
              count: summary.count,
              subtotalValue: summary.subtotalValue,
            ),
          )
          .toList(),
    );

    // Add-more updates the same history record; new analyze creates a new record.
    if (isAddMoreFlow && _activeScanId != null) {
      await ScanHistoryDb.instance.updateScan(_activeScanId!, record);
      return;
    }

    final createdId = await ScanHistoryDb.instance.insertScan(record);
    _activeScanId = createdId;
  }

  void _mergeSummaries(List<CoinSummary> newSummaries, int newTotalCount, int newTotalValue) {
    // Merge by denomination so repeated analyzes accumulate counts instead of duplicating rows
    final Map<int, int> counts = {};
    for (final summary in _summaries) {
      counts[summary.coinValue] = (counts[summary.coinValue] ?? 0) + summary.count;
    }
    for (final summary in newSummaries) {
      counts[summary.coinValue] = (counts[summary.coinValue] ?? 0) + summary.count;
    }

    final merged = counts.entries
        .map((entry) => CoinSummary(coinValue: entry.key, count: entry.value, subtotalValue: entry.key * entry.value))
        .toList()
      ..sort((a, b) => b.coinValue.compareTo(a.coinValue));

    _summaries = merged;
    _totalCount = _totalCount + newTotalCount;
    _totalValue = _totalValue + newTotalValue;
  }

  Future<void> _analyze() async {
    if (_inputImage == null || _inputBytes == null) {
      setState(() {
        _error = 'Select an image from the gallery or take a photo first.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Send one multipart request containing image + calibration/currency/runtime context
      final uri = Uri.parse('$_apiBase/analyze');
      final request = http.MultipartRequest('POST', uri)
        ..fields['auto_mode'] = _autoMode.toString().toLowerCase()
        ..fields['currency_code'] = _currencyCode
        ..fields['user_id'] = _userId;

      if (_apiKey.isNotEmpty) {
        request.headers['X-API-Key'] = _apiKey;
      }

      if (!_autoMode) {
        request.fields['coin_value'] = _coinValue.toString();
      }

      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          _inputBytes!,
          filename: _inputImage!.name,
        ),
      );

      final streamed = await request.send();
      final responseBody = await streamed.stream.bytesToString();
      final jsonMap = json.decode(responseBody) as Map<String, dynamic>;

      if (streamed.statusCode < 200 || streamed.statusCode >= 300) {
        throw Exception(jsonMap['detail'] ?? 'Server error: ${streamed.statusCode}');
      }

      final summariesJson = (jsonMap['coin_summaries'] as List<dynamic>? ?? const []).cast<Map<String, dynamic>>();
      final summaries = summariesJson.map(CoinSummary.fromJson).toList();
      final outputImage = base64Decode(jsonMap['image_base64'] as String);

      final newTotalCount = jsonMap['total_count'] as int? ?? 0;
      final newTotalValue = jsonMap['total_value'] as int? ?? 0;

      final wasAddMore = _isAddingMore;
      setState(() {
        if (wasAddMore) {
          _mergeSummaries(summaries, newTotalCount, newTotalValue);
        } else {
          _summaries = summaries;
          _totalValue = newTotalValue;
          _totalCount = newTotalCount;
        }
        _resultCurrencyCode = _currencyCode;
        _outputBytes = outputImage;
        _isAddingMore = false;
      });

      // Persist after state update so history mirrors what user already sees in UI
      await _persistCurrentScan(isAddMoreFlow: wasAddMore);
    } catch (e) {
      setState(() {
        _error = 'Analysis error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const BackgroundLayer(),
          SafeArea(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 360),
              switchInCurve: Curves.easeOutCubic,
              switchOutCurve: Curves.easeInCubic,
              child: _buildPreAnalysisScreen(),
            ),
          ),
          if (_isLoading) const AnalyzeLoadingOverlay(),
        ],
      ),
    );
  }

  Widget _buildPreAnalysisScreen() {
    return LayoutBuilder(
      key: const ValueKey('pre'),
      builder: (context, constraints) {
        final screenWidth = MediaQuery.sizeOf(context).width;
        final bottomSafeInset = MediaQuery.paddingOf(context).bottom;
        final isPhoneLayout = screenWidth < 700;
        final bottomPadding = isPhoneLayout ? (15 + bottomSafeInset) : 20.0;
        final showInputForAddMore = _isAddingMore && _inputBytes != null;
        // During add-more we keep previewing the new input, otherwise prefer processed output
        final displayImage = showInputForAddMore
            ? _inputBytes
            : ((_summaries.isNotEmpty && _outputBytes != null) ? _outputBytes : _inputBytes);
        final displayTitle = showInputForAddMore
            ? 'Image for analysis (add more)'
            : ((_summaries.isNotEmpty && _outputBytes != null) ? 'Output image' : 'Image for analysis');

        final verticalPadding = 14.0 + bottomPadding;
        final minContentHeight = (constraints.maxHeight - verticalPadding).clamp(0.0, double.infinity).toDouble();

        return ScrollConfiguration(
          behavior: ScrollConfiguration.of(context).copyWith(overscroll: false),
          child: SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            padding: EdgeInsets.fromLTRB(18, 14, 18, bottomPadding),
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: minContentHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Coin Detector',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Align(
                    alignment: Alignment.centerRight,
                    child: OutlinedButton.icon(
                      onPressed: _openSettingsScreen,
                      icon: const Icon(Icons.settings_rounded),
                      label: const Text('Settings'),
                    ),
                  ),
                  const SizedBox(height: 14),
                  SmallImageFrame(
                    imageBytes: displayImage,
                    title: displayTitle,
                  ),
                  const SizedBox(height: 14),
                  if (_summaries.isNotEmpty) ...[
                    _buildAddMoreTextAction(),
                    const SizedBox(height: 10),
                  ],
                  _buildSourceActions(),
                  const SizedBox(height: 12),
                  _buildCurrencySelector(),
                  const SizedBox(height: 12),
                  CalibrationModeCard(
                    autoMode: _autoMode,
                    coinValue: _coinValue,
                    coinValues: _availableCoinValues,
                    coinLabelForValue: (value) => CurrencyFormatting.coinLabel(_currencyCode, value),
                    onAutoSelected: () => setState(() => _autoMode = true),
                    onManualSelected: () => setState(() => _autoMode = false),
                    onCoinValueChanged: (value) => setState(() => _coinValue = value),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 10),
                    ErrorStrip(message: _error!),
                  ],
                  const SizedBox(height: 16),
                  if (_summaries.isNotEmpty) ...[
                    ResultCard(
                      summaries: _summaries,
                      totalCount: _totalCount,
                      totalValue: _totalValue,
                      coinLabelForValue: (value) => CurrencyFormatting.coinLabel(_resultCurrencyCode, value),
                      formatAmount: (amount) => CurrencyFormatting.formatAmount(_resultCurrencyCode, amount),
                      scrollController: _resultScrollController,
                    ),
                    const SizedBox(height: 16),
                  ],
                  _buildAnalyzeButton(),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSourceActions() {
    return Row(
      children: [
        Expanded(
          child: ActionButton(
            icon: Icons.photo_camera_rounded,
            label: 'Take photo',
            onTap: () => _pickImage(ImageSource.camera),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ActionButton(
            icon: Icons.photo_library_rounded,
            label: 'Gallery',
            onTap: () => _pickImage(ImageSource.gallery),
          ),
        ),
      ],
    );
  }

  Widget _buildAddMoreTextAction() {
    final palette = Theme.of(context).extension<AppPalette>()!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
        child: Text(
          'Add more',
          style: TextStyle(
            color: palette.resultStrongText,
            fontWeight: FontWeight.w700,
            fontSize: 16,
          ),
        ),
      ),
    );
  }

  Widget _buildCurrencySelector() {
    final palette = Theme.of(context).extension<AppPalette>()!;
    final textTheme = Theme.of(context).textTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: palette.panelBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: palette.panelBorder),
      ),
      child: Row(
        children: [
          Icon(Icons.public_rounded, color: palette.panelTitle, size: 20),
          const SizedBox(width: 8),
          Text(
            'Currency',
            style: textTheme.titleSmall?.copyWith(
              color: palette.panelTitle,
              fontWeight: FontWeight.w700,
            ),
          ),
          const Spacer(),
          Builder(builder: (context) {
            // Once at least one result exists, keep currency locked for the full scan session
            final currencyEnabled = _summaries.isEmpty;
            return Opacity(
              opacity: currencyEnabled ? 1.0 : 0.5,
              child: DropdownButton<String>(
                value: _currencyCode,
                borderRadius: BorderRadius.circular(12),
                dropdownColor: palette.panelBackground,
                style: TextStyle(color: palette.panelText, fontWeight: FontWeight.w600),
                items: _currencyDenominations.keys
                    .map(
                      (code) => DropdownMenuItem(
                        value: code,
                        child: Text(
                          code,
                          style: TextStyle(color: palette.panelText),
                        ),
                      ),
                    )
                    .toList(),
                onChanged: currencyEnabled
                    ? (value) {
                        if (value == null) return;
                        setState(() {
                          _currencyCode = value;
                          final values = _availableCoinValues;
                          if (!values.contains(_coinValue)) {
                            _coinValue = values.first;
                          }
                        });
                      }
                    : null,
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildAnalyzeButton() {
    final scheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final hoverBackground = Color.alphaBlend(
      (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.32 : 0.24),
      scheme.secondary,
    );
    final pressedBackground = Color.alphaBlend(
      (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.46 : 0.34),
      scheme.secondary,
    );
    // Same button toggles between Analyze and New Scan based on current result state
    final showNewScanAction = _summaries.isNotEmpty && !_isAddingMore;
    return FilledButton.icon(
      style: ButtonStyle(
        animationDuration: const Duration(milliseconds: 120),
        foregroundColor: WidgetStatePropertyAll(scheme.onSecondary),
        padding: const WidgetStatePropertyAll(EdgeInsets.symmetric(vertical: 18)),
        minimumSize: const WidgetStatePropertyAll(Size.fromHeight(56)),
        shape: WidgetStatePropertyAll(
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        elevation: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.pressed)) {
            return 2;
          }
          if (states.contains(WidgetState.hovered)) {
            return 10;
          }
          return 6;
        }),
        backgroundColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.disabled)) {
            return scheme.secondary.withValues(alpha: 0.45);
          }
          if (states.contains(WidgetState.pressed)) {
            return pressedBackground;
          }
          if (states.contains(WidgetState.hovered)) {
            return hoverBackground;
          }
          return scheme.secondary;
        }),
      ),
      onPressed: _isLoading ? null : (showNewScanAction ? _resetResult : _analyze),
      icon: _isLoading
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2.6),
            )
          : Icon(showNewScanAction ? Icons.refresh_rounded : Icons.analytics_rounded, size: 22),
      label: Text(
        _isLoading ? 'Analyzing...' : (showNewScanAction ? 'New Scan' : 'Analyze'),
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
      ),
    );
  }
}
