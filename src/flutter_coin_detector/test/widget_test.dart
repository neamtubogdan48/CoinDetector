import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_coin_detector/app.dart';

void main() {
  testWidgets('renders coin detector home screen', (WidgetTester tester) async {
    await tester.pumpWidget(const CoinDetectorApp());

    expect(find.text('Coin Counter'), findsOneWidget);
    expect(find.text('Analyze'), findsOneWidget);
  });
}
