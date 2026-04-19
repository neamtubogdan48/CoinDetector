import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'screens/coin_detector_screen.dart';
import 'theme/app_themes.dart';

class CoinDetectorApp extends StatefulWidget {
  const CoinDetectorApp({super.key});

  @override
  State<CoinDetectorApp> createState() => _CoinDetectorAppState();
}

class _CoinDetectorAppState extends State<CoinDetectorApp> {
  static const String _themeModeStorageKey = 'theme_mode';
  ThemeMode _themeMode = ThemeMode.light;

  @override
  void initState() {
    super.initState();
    _loadSavedThemeMode();
  }

  // Load saved theme mode on app start
  Future<void> _loadSavedThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    final savedMode = prefs.getString(_themeModeStorageKey);
    final parsedMode = _themeModeFromString(savedMode);
    if (!mounted) return;
    setState(() {
      _themeMode = parsedMode;
    });
  }

  // Helper to parse theme mode from string
  ThemeMode _themeModeFromString(String? mode) {
    switch (mode) {
      case 'dark':
        return ThemeMode.dark;
      case 'system':
        return ThemeMode.system;
      case 'light':
      default:
        return ThemeMode.light;
    }
  }

  Future<void> _setThemeMode(ThemeMode mode) async {
    setState(() {
      _themeMode = mode;
    });

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_themeModeStorageKey, mode.name);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Coin Detector',
      themeMode: _themeMode,
      theme: AppThemes.lightTheme,
      darkTheme: AppThemes.darkTheme,
      home: CoinDetectorScreen(
        themeMode: _themeMode,
        onThemeChanged: _setThemeMode,
      ),
    );
  }
}
