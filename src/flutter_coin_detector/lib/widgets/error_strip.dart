import 'package:flutter/material.dart';

import '../theme/app_palette.dart';

class ErrorStrip extends StatelessWidget {
  const ErrorStrip({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: palette.errorBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: palette.errorBorder),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline_rounded, color: palette.errorIcon),
          const SizedBox(width: 8),
          Expanded(child: Text(message, style: TextStyle(color: palette.errorText))),
        ],
      ),
    );
  }
}
