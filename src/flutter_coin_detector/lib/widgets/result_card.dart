import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/coin_summary.dart';
import '../theme/app_palette.dart';

class ResultCard extends StatelessWidget {
  const ResultCard({
    super.key,
    required this.summaries,
    required this.totalCount,
    required this.totalValue,
    required this.coinLabelForValue,
    required this.formatAmount,
    required this.scrollController,
  });

  final List<CoinSummary> summaries;
  final int totalCount;
  final int totalValue;
  final String Function(int value) coinLabelForValue;
  final String Function(int amount) formatAmount;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    final palette = Theme.of(context).extension<AppPalette>()!;
    final borderRadius = BorderRadius.circular(20);
    final maxInnerHeight = MediaQuery.sizeOf(context).width < 700 ? 300.0 : 340.0;

    return ClipRRect(
      clipBehavior: Clip.antiAlias,
      borderRadius: borderRadius,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: palette.resultGradient,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: borderRadius,
          border: Border.all(color: palette.panelBorder),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Detection Result',
              style: GoogleFonts.spaceGrotesk(
                fontWeight: FontWeight.w700,
                fontSize: 18,
                color: palette.resultStrongText,
              ),
            ),
            const SizedBox(height: 10),
            if (summaries.isEmpty)
              Text(
                'Run analysis to see the number of coins and their value.',
                style: TextStyle(color: palette.resultMutedText),
              )
            else
              ConstrainedBox(
                constraints: BoxConstraints(maxHeight: maxInnerHeight),
                child: ClipRRect(
                  clipBehavior: Clip.antiAlias,
                  borderRadius: BorderRadius.circular(14),
                  child: Scrollbar(
                    controller: scrollController,
                    thumbVisibility: true,
                    trackVisibility: false,
                    radius: const Radius.circular(10),
                    thickness: 6,
                    child: SingleChildScrollView(
                      controller: scrollController,
                      primary: false,
                      child: Padding(
                        padding: const EdgeInsets.only(right: 4),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            ...summaries.map(
                              (summary) => Container(
                                margin: const EdgeInsets.only(bottom: 10),
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                decoration: BoxDecoration(
                                  color: palette.resultItemBackground,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        '${coinLabelForValue(summary.coinValue)} : ${summary.count} pieces',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w600,
                                          color: palette.resultStrongText,
                                        ),
                                      ),
                                    ),
                                    Text(
                                      formatAmount(summary.subtotalValue),
                                      style: TextStyle(
                                        fontWeight: FontWeight.w700,
                                        color: palette.resultStrongText,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            Divider(height: 20, color: palette.panelBorder),
                            LayoutBuilder(
                              builder: (context, constraints) {
                                final isNarrow = constraints.maxWidth < 430;
                                if (isNarrow) {
                                  return Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Total coins: $totalCount',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 16,
                                          color: palette.resultStrongText,
                                        ),
                                      ),
                                      const SizedBox(height: 6),
                                      Text(
                                        'Total value: ${formatAmount(totalValue)}',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 16,
                                          color: palette.resultStrongText,
                                        ),
                                      ),
                                    ],
                                  );
                                }

                                return Row(
                                  children: [
                                    Text(
                                      'Total coins: $totalCount',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w700,
                                        fontSize: 16,
                                        color: palette.resultStrongText,
                                      ),
                                    ),
                                    const Spacer(),
                                    Text(
                                      'Total value: ${formatAmount(totalValue)}',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w800,
                                        fontSize: 16,
                                        color: palette.resultStrongText,
                                      ),
                                    ),
                                  ],
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
