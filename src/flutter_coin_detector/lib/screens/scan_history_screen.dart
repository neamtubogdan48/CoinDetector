import 'package:flutter/material.dart';

import '../data/scan_history_db.dart';
import '../models/scan_record.dart';
import '../utils/currency_formatting.dart';

class ScanHistoryScreen extends StatefulWidget {
  const ScanHistoryScreen({super.key});

  @override
  State<ScanHistoryScreen> createState() => _ScanHistoryScreenState();
}

class _ScanHistoryScreenState extends State<ScanHistoryScreen> {
  late Future<List<ScanRecord>> _scansFuture;

  @override
  void initState() {
    super.initState();
    _scansFuture = ScanHistoryDb.instance.getAllScans();
  }

  Future<void> _reload() async {
    setState(() {
      _scansFuture = ScanHistoryDb.instance.getAllScans();
    });
  }

  String _formatDate(DateTime dateTime) {
    final dt = dateTime.toLocal();
    String two(int value) => value.toString().padLeft(2, '0');
    return '${dt.year}-${two(dt.month)}-${two(dt.day)} ${two(dt.hour)}:${two(dt.minute)}';
  }

  String _coinLabelForValue(String currencyCode, int value) {
    return CurrencyFormatting.coinLabel(currencyCode, value);
  }

  String _formatAmount(String currencyCode, int amount) {
    return CurrencyFormatting.formatAmount(currencyCode, amount);
  }

  Future<void> _deleteScan(int id) async {
    await ScanHistoryDb.instance.deleteScan(id);
    await _reload();
  }

  Future<void> _clearAll() async {
    await ScanHistoryDb.instance.clearScans();
    await _reload();
  }

  Future<bool> _confirmDialog({required String title, required String message}) async {
    final scheme = Theme.of(context).colorScheme;
    final cardTheme = Theme.of(context).cardTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cancelHoverBackground = isDark
        ? scheme.onSurface.withValues(alpha: 0.18)
        : scheme.onSurface.withValues(alpha: 0.14);
    final cancelPressedBackground = isDark
        ? scheme.onSurface.withValues(alpha: 0.28)
        : scheme.onSurface.withValues(alpha: 0.22);
    final hoverBackground = Color.alphaBlend(
      (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.36 : 0.24),
      scheme.secondary,
    );
    final pressedBackground = Color.alphaBlend(
      (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.5 : 0.35),
      scheme.secondary,
    );

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: cardTheme.color,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: cardTheme.shape is RoundedRectangleBorder
              ? ((cardTheme.shape as RoundedRectangleBorder).side)
              : BorderSide.none,
        ),
        title: Text(
          title,
          style: TextStyle(color: scheme.onSurface, fontWeight: FontWeight.w700),
        ),
        content: Text(
          message,
          style: TextStyle(color: scheme.onSurface),
        ),
        actions: [
          TextButton(
            style: ButtonStyle(
              animationDuration: const Duration(milliseconds: 120),
              foregroundColor: WidgetStatePropertyAll(scheme.onSurface),
              backgroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.pressed)) {
                  return cancelPressedBackground;
                }
                if (states.contains(WidgetState.hovered)) {
                  return cancelHoverBackground;
                }
                return Colors.transparent;
              }),
            ),
            onPressed: () => Navigator.of(context).pop(false),
            child: Text('Cancel', style: TextStyle(color: scheme.onSurface)),
          ),
          FilledButton(
            style: ButtonStyle(
              animationDuration: const Duration(milliseconds: 120),
              foregroundColor: WidgetStatePropertyAll(scheme.onSecondary),
              elevation: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return 4;
                }
                if (states.contains(WidgetState.pressed)) {
                  return 1;
                }
                return 0;
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
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    return result ?? false;
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan History'),
        actions: [
          IconButton(
            tooltip: 'Delete all scans',
            onPressed: () async {
              final confirm = await _confirmDialog(
                title: 'Delete all history?',
                message: 'This action cannot be undone.',
              );
              if (!confirm) return;
              await _clearAll();
            },
            icon: const Icon(Icons.delete_sweep_rounded),
          ),
        ],
      ),
      body: FutureBuilder<List<ScanRecord>>(
        future: _scansFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Loading error: ${snapshot.error}'),
              ),
            );
          }

          final scans = snapshot.data ?? const [];
          if (scans.isEmpty) {
            return Center(
              child: Text(
                'No saved scans.',
                style: TextStyle(color: scheme.onSurface, fontWeight: FontWeight.w600),
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: scans.length,
            separatorBuilder: (context, index) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final scan = scans[index];
              final currencyCode = scan.currencyCode.toUpperCase();
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: DefaultTextStyle.merge(
                    style: TextStyle(color: scheme.onSurface),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                'Scan #${scan.id}',
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  fontSize: 16,
                                  color: scheme.onSurface,
                                ),
                              ),
                            ),
                            IconButton(
                              tooltip: 'Delete scan',
                              onPressed: () async {
                                final confirm = await _confirmDialog(
                                  title: 'Delete scan #${scan.id}?',
                                  message: 'This action cannot be undone.',
                                );
                                if (!confirm) return;
                                await _deleteScan(scan.id);
                              },
                              icon: Icon(
                                Icons.delete_outline_rounded,
                                color: scheme.onSurface,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text('Timestamp: ${_formatDate(scan.timestamp)}'),
                        const SizedBox(height: 4),
                        Text('Currency: $currencyCode'),
                        const SizedBox(height: 4),
                        Text('Total coins: ${scan.totalCount}'),
                        Text('Total value: ${_formatAmount(currencyCode, scan.totalValue)}'),
                        const SizedBox(height: 8),
                        Text(
                          'Summaries',
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: scheme.onSurface,
                          ),
                        ),
                        const SizedBox(height: 6),
                        ...scan.summaries.map(
                          (entry) => Padding(
                            padding: const EdgeInsets.only(bottom: 3),
                            child: Text(
                              '${_coinLabelForValue(currencyCode, entry.coinValue)}  x${entry.count}  = ${_formatAmount(currencyCode, entry.subtotalValue)}',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
