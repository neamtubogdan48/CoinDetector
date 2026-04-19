import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_palette.dart';

class SmallImageFrame extends StatelessWidget {
  const SmallImageFrame({
    super.key,
    required this.imageBytes,
    required this.title,
  });

  final Uint8List? imageBytes;
  final String title;

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final isDesktopLike = screenWidth >= 900;
    final frameWidth = math.max(240.0, math.min(isDesktopLike ? 380.0 : 320.0, screenWidth - 80));
    final frameAspectRatio = isDesktopLike ? (4 / 3) : (3 / 4);

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: palette.panelBackground,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: palette.panelBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.spaceGrotesk(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: palette.panelTitle,
            ),
          ),
          const SizedBox(height: 10),
          Center(
            child: SizedBox(
              width: frameWidth,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(14),
                child: AspectRatio(
                  aspectRatio: frameAspectRatio,
                  child: imageBytes == null
                      ? Container(
                          color: palette.imagePlaceholder,
                          child: Center(
                            child: Text(
                              'No image',
                              style: TextStyle(color: palette.resultMutedText),
                            ),
                          ),
                        )
                      : Container(
                          color: palette.imageBackdrop,
                          child: Image.memory(imageBytes!, fit: BoxFit.contain),
                        ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
