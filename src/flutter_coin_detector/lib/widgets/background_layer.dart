import 'package:flutter/material.dart';

import '../theme/app_palette.dart';

class BackgroundLayer extends StatelessWidget {
  const BackgroundLayer({super.key});

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: palette.backgroundGradient,
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: -70,
            right: -40,
            child: _blob(palette.blobA, 220),
          ),
          Positioned(
            bottom: -60,
            left: -40,
            child: _blob(palette.blobB, 240),
          ),
        ],
      ),
    );
  }

  static Widget _blob(Color color, double size) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
      ),
    );
  }
}
