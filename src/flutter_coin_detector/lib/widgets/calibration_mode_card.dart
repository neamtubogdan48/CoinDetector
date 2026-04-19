import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_palette.dart';

class CalibrationModeCard extends StatelessWidget {
  const CalibrationModeCard({
    super.key,
    required this.autoMode,
    required this.coinValue,
    required this.coinValues,
    required this.coinLabelForValue,
    required this.onAutoSelected,
    required this.onManualSelected,
    required this.onCoinValueChanged,
  });

  final bool autoMode;
  final int coinValue;
  final List<int> coinValues;
  final String Function(int) coinLabelForValue;
  final VoidCallback onAutoSelected;
  final VoidCallback onManualSelected;
  final ValueChanged<int> onCoinValueChanged;

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    final scheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    ButtonStyle modeButtonStyle({required bool isSelected}) {
      final baseBackground = scheme.surface;
      final hoverBackground = Color.alphaBlend(
        (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.1 : 0.14),
        baseBackground,
      );
      final pressedBackground = Color.alphaBlend(
        (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.16 : 0.22),
        baseBackground,
      );

      return ButtonStyle(
        animationDuration: const Duration(milliseconds: 120),
        foregroundColor: WidgetStatePropertyAll(scheme.onSurface),
        padding: const WidgetStatePropertyAll(EdgeInsets.symmetric(horizontal: 18)),
        elevation: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.hovered)) {
            return 3;
          }
          if (states.contains(WidgetState.pressed)) {
            return 1;
          }
          return 0;
        }),
        backgroundColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.pressed)) {
            return pressedBackground;
          }
          if (states.contains(WidgetState.hovered)) {
            return hoverBackground;
          }
          return baseBackground;
        }),
        shape: WidgetStatePropertyAll(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: isSelected ? scheme.secondary : scheme.surface,
              width: 2,
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: palette.panelBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: palette.panelBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Calibration mode',
            style: GoogleFonts.spaceGrotesk(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: palette.panelTitle,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              SizedBox(
                height: 44,
                child: FilledButton(
                  style: modeButtonStyle(isSelected: autoMode),
                  onPressed: onAutoSelected,
                  child: const Text('Auto', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
              ),
              const SizedBox(width: 10),
              SizedBox(
                height: 44,
                child: FilledButton(
                  style: modeButtonStyle(isSelected: !autoMode),
                  onPressed: onManualSelected,
                  child: const Text('Manual', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
              ),
              const Spacer(),
              if (!autoMode)
                DropdownButton<int>(
                  value: coinValue,
                  borderRadius: BorderRadius.circular(12),
                  dropdownColor: palette.panelBackground,
                  style: TextStyle(color: palette.panelText, fontWeight: FontWeight.w600),
                  items: coinValues
                      .map(
                        (v) => DropdownMenuItem(
                          value: v,
                          child: Text(
                            coinLabelForValue(v),
                            style: TextStyle(color: palette.panelText),
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (v) {
                    if (v != null) onCoinValueChanged(v);
                  },
                ),
            ],
          ),
        ],
      ),
    );
  }
}
