import 'package:flutter/material.dart';

@immutable
class AppPalette extends ThemeExtension<AppPalette> {
  const AppPalette({
    required this.backgroundGradient,
    required this.blobA,
    required this.blobB,
    required this.panelBackground,
    required this.panelBorder,
    required this.panelTitle,
    required this.panelText,
    required this.headerGradient,
    required this.headerTitle,
    required this.headerSubtitle,
    required this.resultGradient,
    required this.resultItemBackground,
    required this.resultStrongText,
    required this.resultMutedText,
    required this.imagePlaceholder,
    required this.imageBackdrop,
    required this.errorBackground,
    required this.errorBorder,
    required this.errorIcon,
    required this.errorText,
    required this.overlayBarrier,
    required this.overlayCard,
    required this.overlayBorder,
    required this.overlayTitle,
    required this.overlaySubtitle,
    required this.settingsSectionTitle,
    required this.loadingPrimary,
    required this.loadingSecondary,
    required this.loadingTrack,
  });

  final List<Color> backgroundGradient;
  final Color blobA;
  final Color blobB;
  final Color panelBackground;
  final Color panelBorder;
  final Color panelTitle;
  final Color panelText;
  final List<Color> headerGradient;
  final Color headerTitle;
  final Color headerSubtitle;
  final List<Color> resultGradient;
  final Color resultItemBackground;
  final Color resultStrongText;
  final Color resultMutedText;
  final Color imagePlaceholder;
  final Color imageBackdrop;
  final Color errorBackground;
  final Color errorBorder;
  final Color errorIcon;
  final Color errorText;
  final Color overlayBarrier;
  final Color overlayCard;
  final Color overlayBorder;
  final Color overlayTitle;
  final Color overlaySubtitle;
  final Color settingsSectionTitle;
  final Color loadingPrimary;
  final Color loadingSecondary;
  final Color loadingTrack;

  static const AppPalette dark = AppPalette(
    backgroundGradient: [Color(0xFF090E1A), Color(0xFF111A2B), Color(0xFF16243A)],
    blobA: Color(0x3DDAAE52),
    blobB: Color(0x335A92D3),
    panelBackground: Color(0xC0142135),
    panelBorder: Color(0xFF2D405E),
    panelTitle: Color(0xFFD7E7FF),
    panelText: Color(0xFFEEF5FF),
    headerGradient: [Color(0xFF152743), Color(0xFF1A365D), Color(0xFF3E6E9E)],
    headerTitle: Color(0xFFF4F8FF),
    headerSubtitle: Color(0xFFBFD1EE),
    resultGradient: [Color(0xFF162238), Color(0xFF111D31)],
    resultItemBackground: Color(0x4D2D4568),
    resultStrongText: Color(0xFFEFF6FF),
    resultMutedText: Color(0xFFA3B7D6),
    imagePlaceholder: Color(0xFF1C2A40),
    imageBackdrop: Color(0xFF101A2B),
    errorBackground: Color(0xFF45243A),
    errorBorder: Color(0xFF8A4B70),
    errorIcon: Color(0xFFFFA8D0),
    errorText: Color(0xFFFFE7F3),
    overlayBarrier: Color(0xB00A1220),
    overlayCard: Color(0xF01A2940),
    overlayBorder: Color(0xFF3E557A),
    overlayTitle: Color(0xFFF5F9FF),
    overlaySubtitle: Color(0xFFB8C9E5),
    settingsSectionTitle: Color(0xFFE7F0FF),
    loadingPrimary: Color(0xFF8BD3FF),
    loadingSecondary: Color(0xFFF0C56A),
    loadingTrack: Color(0xFF425A7C),
  );

  static const AppPalette light = AppPalette(
    backgroundGradient: [Color(0xFFFFFAFF), Color(0xFFFFEEF7), Color(0xFFF7E9FF)],
    blobA: Color(0x52FF9BB8),
    blobB: Color(0x4AB987F5),
    panelBackground: Color(0xFAFFFFFF),
    panelBorder: Color(0xFFD9CCE8),
    panelTitle: Color(0xFF56365F),
    panelText: Color(0xFF3A2948),
    headerGradient: [Color(0xFFFFE2F0), Color(0xFFF4D7FF), Color(0xFFEED4FF)],
    headerTitle: Color(0xFF2F2340),
    headerSubtitle: Color(0xFF5D4A77),
    resultGradient: [Color(0xFFFFF4FB), Color(0xFFF5E7FF)],
    resultItemBackground: Color(0xFFF0D6FA),
    resultStrongText: Color(0xFF36254A),
    resultMutedText: Color(0xFF6B5A88),
    imagePlaceholder: Color(0xFFF2E8FB),
    imageBackdrop: Color(0xFFEBDCFB),
    errorBackground: Color(0xFFFFEEF3),
    errorBorder: Color(0xFFE5A2B9),
    errorIcon: Color(0xFFC95A82),
    errorText: Color(0xFF6E2B45),
    overlayBarrier: Color(0xA8F4E4F3),
    overlayCard: Color(0xFFFFF8FD),
    overlayBorder: Color(0xFFDABFEA),
    overlayTitle: Color(0xFF3A294F),
    overlaySubtitle: Color(0xFF6A5790),
    settingsSectionTitle: Color(0xFF8C4D79),
    loadingPrimary: Color(0xFFB55B7D),
    loadingSecondary: Color(0xFF8B4DCC),
    loadingTrack: Color(0xFFE2D5F2),
  );

  @override
  AppPalette copyWith({
    List<Color>? backgroundGradient,
    Color? blobA,
    Color? blobB,
    Color? panelBackground,
    Color? panelBorder,
    Color? panelTitle,
    Color? panelText,
    List<Color>? headerGradient,
    Color? headerTitle,
    Color? headerSubtitle,
    List<Color>? resultGradient,
    Color? resultItemBackground,
    Color? resultStrongText,
    Color? resultMutedText,
    Color? imagePlaceholder,
    Color? imageBackdrop,
    Color? errorBackground,
    Color? errorBorder,
    Color? errorIcon,
    Color? errorText,
    Color? overlayBarrier,
    Color? overlayCard,
    Color? overlayBorder,
    Color? overlayTitle,
    Color? overlaySubtitle,
    Color? settingsSectionTitle,
    Color? loadingPrimary,
    Color? loadingSecondary,
    Color? loadingTrack,
  }) {
    return AppPalette(
      backgroundGradient: backgroundGradient ?? this.backgroundGradient,
      blobA: blobA ?? this.blobA,
      blobB: blobB ?? this.blobB,
      panelBackground: panelBackground ?? this.panelBackground,
      panelBorder: panelBorder ?? this.panelBorder,
      panelTitle: panelTitle ?? this.panelTitle,
      panelText: panelText ?? this.panelText,
      headerGradient: headerGradient ?? this.headerGradient,
      headerTitle: headerTitle ?? this.headerTitle,
      headerSubtitle: headerSubtitle ?? this.headerSubtitle,
      resultGradient: resultGradient ?? this.resultGradient,
      resultItemBackground: resultItemBackground ?? this.resultItemBackground,
      resultStrongText: resultStrongText ?? this.resultStrongText,
      resultMutedText: resultMutedText ?? this.resultMutedText,
      imagePlaceholder: imagePlaceholder ?? this.imagePlaceholder,
      imageBackdrop: imageBackdrop ?? this.imageBackdrop,
      errorBackground: errorBackground ?? this.errorBackground,
      errorBorder: errorBorder ?? this.errorBorder,
      errorIcon: errorIcon ?? this.errorIcon,
      errorText: errorText ?? this.errorText,
      overlayBarrier: overlayBarrier ?? this.overlayBarrier,
      overlayCard: overlayCard ?? this.overlayCard,
      overlayBorder: overlayBorder ?? this.overlayBorder,
      overlayTitle: overlayTitle ?? this.overlayTitle,
      overlaySubtitle: overlaySubtitle ?? this.overlaySubtitle,
      settingsSectionTitle: settingsSectionTitle ?? this.settingsSectionTitle,
      loadingPrimary: loadingPrimary ?? this.loadingPrimary,
      loadingSecondary: loadingSecondary ?? this.loadingSecondary,
      loadingTrack: loadingTrack ?? this.loadingTrack,
    );
  }

  @override
  ThemeExtension<AppPalette> lerp(ThemeExtension<AppPalette>? other, double t) {
    if (other is! AppPalette) {
      return this;
    }

    return AppPalette(
      backgroundGradient: [
        Color.lerp(backgroundGradient[0], other.backgroundGradient[0], t)!,
        Color.lerp(backgroundGradient[1], other.backgroundGradient[1], t)!,
        Color.lerp(backgroundGradient[2], other.backgroundGradient[2], t)!,
      ],
      blobA: Color.lerp(blobA, other.blobA, t)!,
      blobB: Color.lerp(blobB, other.blobB, t)!,
      panelBackground: Color.lerp(panelBackground, other.panelBackground, t)!,
      panelBorder: Color.lerp(panelBorder, other.panelBorder, t)!,
      panelTitle: Color.lerp(panelTitle, other.panelTitle, t)!,
      panelText: Color.lerp(panelText, other.panelText, t)!,
      headerGradient: [
        Color.lerp(headerGradient[0], other.headerGradient[0], t)!,
        Color.lerp(headerGradient[1], other.headerGradient[1], t)!,
        Color.lerp(headerGradient[2], other.headerGradient[2], t)!,
      ],
      headerTitle: Color.lerp(headerTitle, other.headerTitle, t)!,
      headerSubtitle: Color.lerp(headerSubtitle, other.headerSubtitle, t)!,
      resultGradient: [
        Color.lerp(resultGradient[0], other.resultGradient[0], t)!,
        Color.lerp(resultGradient[1], other.resultGradient[1], t)!,
      ],
      resultItemBackground: Color.lerp(resultItemBackground, other.resultItemBackground, t)!,
      resultStrongText: Color.lerp(resultStrongText, other.resultStrongText, t)!,
      resultMutedText: Color.lerp(resultMutedText, other.resultMutedText, t)!,
      imagePlaceholder: Color.lerp(imagePlaceholder, other.imagePlaceholder, t)!,
      imageBackdrop: Color.lerp(imageBackdrop, other.imageBackdrop, t)!,
      errorBackground: Color.lerp(errorBackground, other.errorBackground, t)!,
      errorBorder: Color.lerp(errorBorder, other.errorBorder, t)!,
      errorIcon: Color.lerp(errorIcon, other.errorIcon, t)!,
      errorText: Color.lerp(errorText, other.errorText, t)!,
      overlayBarrier: Color.lerp(overlayBarrier, other.overlayBarrier, t)!,
      overlayCard: Color.lerp(overlayCard, other.overlayCard, t)!,
      overlayBorder: Color.lerp(overlayBorder, other.overlayBorder, t)!,
      overlayTitle: Color.lerp(overlayTitle, other.overlayTitle, t)!,
      overlaySubtitle: Color.lerp(overlaySubtitle, other.overlaySubtitle, t)!,
      settingsSectionTitle: Color.lerp(settingsSectionTitle, other.settingsSectionTitle, t)!,
      loadingPrimary: Color.lerp(loadingPrimary, other.loadingPrimary, t)!,
      loadingSecondary: Color.lerp(loadingSecondary, other.loadingSecondary, t)!,
      loadingTrack: Color.lerp(loadingTrack, other.loadingTrack, t)!,
    );
  }
}
