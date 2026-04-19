import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_palette.dart';

class AnalyzeLoadingOverlay extends StatefulWidget {
  const AnalyzeLoadingOverlay({super.key});

  @override
  State<AnalyzeLoadingOverlay> createState() => _AnalyzeLoadingOverlayState();
}

class _AnalyzeLoadingOverlayState extends State<AnalyzeLoadingOverlay> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    return Positioned.fill(
      child: IgnorePointer(
        ignoring: false,
        child: Container(
          color: palette.overlayBarrier,
          child: Center(
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, _) {
                final t = _controller.value;
                final pulse = 0.94 + 0.08 * math.sin(t * math.pi * 2);
                final progress = (math.sin(t * math.pi * 2 - (math.pi / 2)) + 1) / 2;

                return Transform.scale(
                  scale: pulse,
                  child: Container(
                    width: 292,
                    padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 20),
                    decoration: BoxDecoration(
                      color: palette.overlayCard,
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: palette.overlayBorder),
                      boxShadow: [
                        BoxShadow(
                          color: palette.loadingPrimary.withValues(alpha: 0.16),
                          blurRadius: 28,
                          spreadRadius: 2,
                          offset: const Offset(0, 10),
                        ),
                        BoxShadow(
                          color: palette.panelBorder.withValues(alpha: 0.24),
                          blurRadius: 22,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 72,
                          height: 72,
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              CircularProgressIndicator(
                                strokeWidth: 4,
                                value: progress,
                                valueColor: AlwaysStoppedAnimation<Color>(palette.loadingPrimary),
                                backgroundColor: palette.loadingTrack,
                              ),
                              Transform.rotate(
                                angle: t * math.pi * 2,
                                child: Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: LinearGradient(
                                      colors: [palette.loadingPrimary, palette.loadingSecondary],
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: palette.loadingPrimary.withValues(alpha: 0.24),
                                        blurRadius: 14,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.monetization_on_rounded,
                                    size: 24,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),
                        Text(
                          'Analyzing coins...',
                          style: GoogleFonts.spaceGrotesk(
                            color: palette.overlayTitle,
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.25,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(3, (index) {
                            final shift = (t + index * 0.2) % 1.0;
                            final dotScale = 0.75 + 0.35 * math.sin(shift * math.pi);
                            final opacity = 0.35 + 0.65 * math.sin(shift * math.pi);
                            return Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 4),
                              child: Transform.scale(
                                scale: dotScale,
                                child: Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: palette.loadingSecondary.withValues(alpha: opacity),
                                    shape: BoxShape.circle,
                                  ),
                                ),
                              ),
                            );
                          }),
                        ),
                        const SizedBox(height: 14),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(99),
                          child: LinearProgressIndicator(
                            minHeight: 6,
                            value: progress,
                            valueColor: AlwaysStoppedAnimation<Color>(palette.loadingSecondary),
                            backgroundColor: palette.loadingTrack,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}
