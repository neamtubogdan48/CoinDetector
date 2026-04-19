import 'package:flutter/material.dart';

import 'scan_history_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({
    super.key,
    required this.themeMode,
    required this.onThemeChanged,
  });

  final ThemeMode themeMode;
  final ValueChanged<ThemeMode> onThemeChanged;

  IconData _themeIcon(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return Icons.light_mode_rounded;
      case ThemeMode.dark:
        return Icons.dark_mode_rounded;
      case ThemeMode.system:
        return Icons.phone_iphone_rounded;
    }
  }

  Future<void> _openHistory(BuildContext context) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => const ScanHistoryScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isLight = Theme.of(context).brightness == Brightness.light;
    final cardTheme = Theme.of(context).cardTheme;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: isLight ? cardTheme.color : null,
        shape: isLight
            ? const Border(
                bottom: BorderSide(color: Color(0xFFC88BEA), width: 1.2),
              )
            : null,
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.history_rounded),
              title: const Text('Scan History'),
              trailing: const Icon(Icons.chevron_right_rounded),
              onTap: () => _openHistory(context),
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _themeIcon(themeMode),
                        color: Theme.of(context).colorScheme.onSurface,
                      ),
                      const SizedBox(width: 10),
                      Text(
                        'Theme',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SegmentedButton<ThemeMode>(
                    segments: const [
                      ButtonSegment<ThemeMode>(
                        value: ThemeMode.light,
                        icon: Icon(Icons.light_mode_rounded),
                        label: Text('Light'),
                      ),
                      ButtonSegment<ThemeMode>(
                        value: ThemeMode.dark,
                        icon: Icon(Icons.dark_mode_rounded),
                        label: Text('Dark'),
                      ),
                      ButtonSegment<ThemeMode>(
                        value: ThemeMode.system,
                        icon: Icon(Icons.phone_android_rounded),
                        label: Text('System'),
                      ),
                    ],
                    selected: <ThemeMode>{themeMode},
                    onSelectionChanged: (selection) {
                      if (selection.isEmpty) return;
                      onThemeChanged(selection.first);
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
