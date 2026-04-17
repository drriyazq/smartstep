import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'data/local/hive_setup.dart';
import 'features/ladder/dashboard_screen.dart';
import 'features/onboarding/baseline_screen.dart';
import 'features/onboarding/child_profile_screen.dart';
import 'features/onboarding/environment_screen.dart';
import 'features/onboarding/phone_screen.dart';
import 'features/task/task_detail_screen.dart';

final _router = GoRouter(
  initialLocation: "/phone",
  redirect: (context, state) {
    final hasProfile = HiveSetup.childBox.isNotEmpty;
    final onboardingPath = state.matchedLocation.startsWith("/onboarding") ||
        state.matchedLocation == "/phone";
    if (hasProfile && onboardingPath) return "/dashboard";
    if (!hasProfile && state.matchedLocation == "/dashboard") return "/phone";
    return null;
  },
  routes: [
    GoRoute(path: "/phone", builder: (_, __) => const PhoneScreen()),
    GoRoute(
      path: "/onboarding/child",
      builder: (_, __) => const ChildProfileScreen(),
    ),
    GoRoute(
      path: "/onboarding/environment",
      builder: (_, state) =>
          EnvironmentScreen(childId: state.uri.queryParameters["childId"]!),
    ),
    GoRoute(
      path: "/onboarding/baseline",
      builder: (_, state) =>
          BaselineScreen(childId: state.uri.queryParameters["childId"]!),
    ),
    GoRoute(path: "/dashboard", builder: (_, __) => const DashboardScreen()),
    GoRoute(
      path: "/task/:slug",
      builder: (_, state) => TaskDetailScreen(taskSlug: state.pathParameters["slug"]!),
    ),
  ],
);

class SmartStepApp extends ConsumerWidget {
  const SmartStepApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: "SmartStep",
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2E6FF2)),
        useMaterial3: true,
      ),
      routerConfig: _router,
    );
  }
}
