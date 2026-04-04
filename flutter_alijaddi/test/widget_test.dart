import 'package:flutter_test/flutter_test.dart';

import 'package:alijaddi_flutter/main.dart';

void main() {
  testWidgets('App loads', (WidgetTester tester) async {
    await tester.pumpWidget(const AliJaddiApp());
    expect(find.textContaining('علي جدّي'), findsWidgets);
  });
}
