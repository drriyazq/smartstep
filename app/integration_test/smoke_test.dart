import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:smartstep_app/features/onboarding/signin_screen.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets("boots to sign-in screen", (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: SignInScreen()),
      ),
    );
    expect(find.text("Welcome to SmartStep"), findsOneWidget);
    expect(find.text("Continue with Google"), findsOneWidget);
  });
}
