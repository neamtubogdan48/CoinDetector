import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_palette.dart';

class ActionButton extends StatelessWidget {
  const ActionButton({
    super.key,
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        hoverColor: (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.08 : 0.14),
        highlightColor: (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.12 : 0.2),
        splashColor: (isDark ? Colors.white : Colors.black).withValues(alpha: isDark ? 0.16 : 0.24),
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
          decoration: BoxDecoration(
            color: palette.panelBackground,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: palette.panelBorder),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 20, color: palette.panelTitle),
              const SizedBox(width: 8),
              Text(
                label,
                style: GoogleFonts.spaceGrotesk(
                  fontWeight: FontWeight.w600,
                  color: palette.panelText,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
