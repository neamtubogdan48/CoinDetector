class ScanSummaryEntry {
  const ScanSummaryEntry({
    required this.coinValue,
    required this.count,
    required this.subtotalValue,
  });

  final int coinValue;
  final int count;
  final int subtotalValue;

  // Parses a ScanSummaryEntry from a map
  factory ScanSummaryEntry.fromMap(Map<String, dynamic> map) {
    return ScanSummaryEntry(
      coinValue: (map['coinValue'] ?? map['coin_value'] ?? 0) as int,
      count: (map['count'] ?? 0) as int,
      subtotalValue: (map['subtotalValue'] ?? map['subtotal_value'] ?? 0) as int,
    );
  }

  // Converts the ScanSummaryEntry to a map
  Map<String, dynamic> toMap() {
    return {
      'coinValue': coinValue,
      'count': count,
      'subtotalValue': subtotalValue,
    };
  }
}

class ScanRecord {
  const ScanRecord({
    required this.id,
    required this.timestamp,
    required this.currencyCode,
    required this.totalCount,
    required this.totalValue,
    required this.summaries,
  });

  final int id;
  final DateTime timestamp;
  final String currencyCode;
  final int totalCount;
  final int totalValue;
  final List<ScanSummaryEntry> summaries;

  // Parses a ScanRecord from a map
  factory ScanRecord.fromMap(int id, Map<String, dynamic> map) {
    final rawSummaries = (map['summaries'] as List<dynamic>? ?? const []);
    final parsedSummaries = rawSummaries
        .map((item) => ScanSummaryEntry.fromMap((item as Map).cast<String, dynamic>()))
        .toList();

    return ScanRecord(
      id: id,
      timestamp: DateTime.tryParse((map['timestamp'] ?? '').toString()) ?? DateTime.now(),
      currencyCode: (map['currencyCode'] ?? map['currency_code'] ?? 'RON').toString(),
      totalCount: (map['totalCount'] ?? 0) as int,
      totalValue: (map['totalValue'] ?? 0) as int,
      summaries: parsedSummaries,
    );
  }

  // Converts the ScanRecord to a map
  Map<String, dynamic> toMap() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'currencyCode': currencyCode,
      'totalCount': totalCount,
      'totalValue': totalValue,
      'summaries': summaries.map((entry) => entry.toMap()).toList(),
    };
  }
}
