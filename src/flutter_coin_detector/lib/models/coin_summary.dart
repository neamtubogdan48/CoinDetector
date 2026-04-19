class CoinSummary {
  const CoinSummary({
    required this.coinValue,
    required this.count,
    required this.subtotalValue,
  });

  final int coinValue;
  final int count;
  final int subtotalValue;
  
  // Parses a CoinSummary from a JSON map
  factory CoinSummary.fromJson(Map<String, dynamic> json) {
    return CoinSummary(
      coinValue: json['coin_value'] as int? ?? 0,
      count: json['count'] as int? ?? 0,
      subtotalValue: json['subtotal_value'] as int? ?? 0,
    );
  }

  // Converts the CoinSummary to a JSON map
  Map<String, dynamic> toMap() {
    return {
      'coinValue': coinValue,
      'count': count,
      'subtotalValue': subtotalValue,
    };
  }
}
