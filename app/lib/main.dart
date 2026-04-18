import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';
import 'data/local/hive_setup.dart';
import 'firebase_options.dart';

Future<void> main() async {
  // Wrap startup in a zone so any async exceptions route to Crashlytics.
  await runZonedGuarded<Future<void>>(() async {
    WidgetsFlutterBinding.ensureInitialized();

    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );

    // Only collect in release builds so dev crashes don't flood the dashboard.
    await FirebaseCrashlytics.instance
        .setCrashlyticsCollectionEnabled(kReleaseMode);

    // Capture every uncaught Flutter framework error.
    FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

    // Capture platform/async errors outside the framework.
    PlatformDispatcher.instance.onError = (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
      return true;
    };

    await HiveSetup.init();
    runApp(const ProviderScope(child: SmartStepApp()));
  }, (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
  });
}
