import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:smartstep_app/features/onboarding/phone_screen.dart';

/// Smoke test: app boots to the phone screen and the heading is visible.
/// Full end-to-end (API → ladder) requires a live backend and is manual for now.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets("boots to phone screen", (tester) async {
    await tester.pumpWidget(const MaterialApp(home: PhoneScreen()));
    expect(find.text("Welcome to SmartStep"), findsOneWidget);
    expect(find.widgetWithText(OutlinedButton, "Send OTP").evaluate().isNotEmpty ||
        find.widgetWithText(FilledButton, "Send OTP").evaluate().isNotEmpty, true);
  });
}
