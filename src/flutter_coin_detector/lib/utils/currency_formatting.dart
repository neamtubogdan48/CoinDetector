class CurrencyFormatting {
  // Utility class for formatting currency amounts and coin labels
  static const Map<String, Map<int, String>> _coinLabelsByCurrency = {
    'RON': {1: '1 ban', 5: '5 bani', 10: '10 bani', 50: '50 bani'},
    'EUR': {
      1: '1 cent',
      2: '2 cents',
      5: '5 cents',
      10: '10 cents',
      20: '20 cents',
      50: '50 cents',
      100: '1 euro',
      200: '2 euro',
    },
    'USD': {
      1: '1 cent',
      5: '5 cents',
      10: '10 cents',
      25: '25 cents',
      50: '50 cents',
      100: '1 dollar',
    },
    'GBP': {
      1: '1 penny',
      2: '2 pence',
      5: '5 pence',
      10: '10 pence',
      20: '20 pence',
      50: '50 pence',
      100: '1 pound',
      200: '2 pounds',
    },
  };

  static const Map<String, List<String>> _currencyUnits = {
    'RON': ['leu', 'lei', 'ban', 'bani'],
    'EUR': ['euro', 'euro', 'cent', 'cents'],
    'USD': ['dollar', 'dollars', 'cent', 'cents'],
    'GBP': ['pound', 'pounds', 'penny', 'pence'],
  };

  static String coinLabel(String currencyCode, int value) {
    // Returns a label for a coin value based on the currency
    final code = currencyCode.toUpperCase();
    final labels = _coinLabelsByCurrency[code] ?? const {};
    
    return labels[value] ?? '$value';
  }

  static String formatAmount(String currencyCode, int amount) {
    // Formats an amount into a string with major and minor units
    final code = currencyCode.toUpperCase();
    final units = _currencyUnits[code] ?? _currencyUnits['RON']!;
    
    return _formatMajorMinorValue(
      amount: amount,
      majorDivisor: 100,
      majorSingular: units[0],
      majorPlural: units[1],
      minorSingular: units[2],
      minorPlural: units[3],
    );
  }

  static String _formatMajorMinorValue({
    required int amount,
    required int majorDivisor,
    required String majorSingular,
    required String majorPlural,
    required String minorSingular,
    required String minorPlural,
  }) {
    // Helper function to format an amount into major and minor units
    if (amount >= majorDivisor) {
      final major = amount ~/ majorDivisor;
      final minor = amount % majorDivisor;
      final majorWord = major == 1 ? majorSingular : majorPlural;
      
      if (minor == 0) {
        return '$major $majorWord';
      }

      final minorWord = minor == 1 ? minorSingular : minorPlural;
      return '$major $majorWord and $minor $minorWord';
    }

    final minorWord = amount == 1 ? minorSingular : minorPlural;
    return '$amount $minorWord';
  }
}
