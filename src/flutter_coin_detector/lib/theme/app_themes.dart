import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_palette.dart';

class AppThemes {
  static ThemeData get darkTheme {
    final baseTextTheme = GoogleFonts.spaceGroteskTextTheme();
    final textTheme = baseTextTheme.copyWith(
      titleLarge: baseTextTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
      titleMedium: baseTextTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
      titleSmall: baseTextTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
    );
    const scheme = ColorScheme.dark(
      primary: Color(0xFFD7B060),
      secondary: Color(0xFF72BDE9),
      surface: Color(0xFF1A2942),
      onPrimary: Color(0xFF211602),
      onSecondary: Colors.white,
      onSurface: Color(0xFFEAF3FF),
      error: Color(0xFFFFA9CD),
      onError: Color(0xFF351124),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      textTheme: textTheme,
      scaffoldBackgroundColor: const Color(0xFF0D0A1E),
      colorScheme: scheme,
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF17263D),
        foregroundColor: Color(0xFFEAF3FF),
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        scrolledUnderElevation: 0,
        shape: Border(
          bottom: BorderSide(color: Color(0xFF2D405E), width: 1.2),
        ),
      ),
      cardTheme: const CardThemeData(
        color: Color(0xFF16243A),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
          side: BorderSide(color: Color(0xFF2D405E), width: 1.2),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: scheme.primary,
          foregroundColor: scheme.onPrimary,
          elevation: 1.5,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: scheme.onSurface,
          side: BorderSide(color: scheme.secondary.withValues(alpha: 0.55)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: scheme.onSurface),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return scheme.primary;
          }
          return const Color(0xFFBCCCE3);
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return scheme.primary.withValues(alpha: 0.45);
          }
          return const Color(0xFF3A4E6C);
        }),
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        textStyle: TextStyle(color: scheme.onSurface),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: const Color(0xFF1B1640),
      ),
      scrollbarTheme: const ScrollbarThemeData(
        thumbColor: WidgetStatePropertyAll(Color(0xAA72BDE9)),
        trackColor: WidgetStatePropertyAll(Colors.transparent),
        trackBorderColor: WidgetStatePropertyAll(Colors.transparent),
        radius: Radius.circular(10),
        thickness: WidgetStatePropertyAll(6),
        mainAxisMargin: 6,
        crossAxisMargin: 4,
      ),
      extensions: const <ThemeExtension<dynamic>>[
        AppPalette.dark,
      ],
    );
  }

  static ThemeData get lightTheme {
    final baseTextTheme = GoogleFonts.spaceGroteskTextTheme();
    final textTheme = baseTextTheme.copyWith(
      titleLarge: baseTextTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
      titleMedium: baseTextTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
      titleSmall: baseTextTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
    );
    const scheme = ColorScheme.light(
      primary: Color(0xFFB55B7D),
      secondary: Color(0xFF8B4DCC),
      surface: Color(0xFFFFFAFE),
      onPrimary: Color(0xFFFFFFFF),
      onSecondary: Color(0xFFFFFFFF),
      onSurface: Color(0xFF3C2A4D),
      error: Color(0xFFC74E73),
      onError: Color(0xFFFFF4EC),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      textTheme: textTheme,
      scaffoldBackgroundColor: const Color(0xFFFFFBFF),
      colorScheme: scheme,
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFFFFEAF6),
        foregroundColor: Color(0xFF3C2A4D),
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        scrolledUnderElevation: 0,
        shape: Border(
          bottom: BorderSide(color: Color(0xFFC88BEA), width: 1.2),
        ),
      ),
      cardTheme: const CardThemeData(
        color: Color(0xFFF1DDF8),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
          side: BorderSide(color: Color(0xFFC88BEA), width: 1.2),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: scheme.primary,
          foregroundColor: scheme.onPrimary,
          elevation: 1.0,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: scheme.onSurface,
          side: BorderSide(color: const Color(0xFFD6B2EE)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: scheme.onSurface),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return scheme.primary;
          }
          return const Color(0xFFD7BDE9);
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return scheme.primary.withValues(alpha: 0.4);
          }
          return const Color(0xFFEEDCFB);
        }),
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        textStyle: TextStyle(color: scheme.onSurface),
      ),
      dialogTheme: const DialogThemeData(
        backgroundColor: Color(0xFFFFFAFE),
      ),
      scrollbarTheme: const ScrollbarThemeData(
        thumbColor: WidgetStatePropertyAll(Color(0xB39A62CC)),
        trackColor: WidgetStatePropertyAll(Colors.transparent),
        trackBorderColor: WidgetStatePropertyAll(Colors.transparent),
        radius: Radius.circular(10),
        thickness: WidgetStatePropertyAll(6),
        mainAxisMargin: 6,
        crossAxisMargin: 4,
      ),
      extensions: const <ThemeExtension<dynamic>>[
        AppPalette.light,
      ],
    );
  }
}
