import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'data/local/hive_setup.dart';
import 'features/ladder/dashboard_screen.dart';
import 'features/onboarding/baseline_screen.dart';
import 'features/onboarding/child_profile_screen.dart';
import 'features/onboarding/environment_screen.dart';
import 'features/onboarding/phone_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/task/custom_task_detail_screen.dart';
import 'features/task/task_detail_screen.dart';

final _router = GoRouter(
  initialLocation: "/phone",
  redirect: (context, state) {
    final hasProfile = HiveSetup.childBox.isNotEmpty;
    final onboardingPath = state.matchedLocation.startsWith("/onboarding") ||
        state.matchedLocation == "/phone";
    // Allow onboarding routes when explicitly adding a second child.
    final addingChild = state.uri.queryParameters['adding'] == 'true';
    if (hasProfile && onboardingPath && !addingChild) return "/dashboard";
    if (!hasProfile && !onboardingPath) return "/phone";
    return null;
  },
  routes: [
    GoRoute(path: "/phone", builder: (_, __) => const PhoneScreen()),
    GoRoute(
      path: "/onboarding/child",
      builder: (_, state) => ChildProfileScreen(
        adding: state.uri.queryParameters['adding'] == 'true',
      ),
    ),
    GoRoute(
      path: "/onboarding/environment",
      builder: (_, state) => EnvironmentScreen(
        childId: state.uri.queryParameters["childId"]!,
        adding: state.uri.queryParameters['adding'] == 'true',
      ),
    ),
    GoRoute(
      path: "/onboarding/baseline",
      builder: (_, state) => BaselineScreen(
        childId: state.uri.queryParameters["childId"]!,
        adding: state.uri.queryParameters['adding'] == 'true',
      ),
    ),
    GoRoute(path: "/dashboard", builder: (_, __) => const DashboardScreen()),
    GoRoute(
      path: "/task/:slug",
      builder: (_, state) =>
          TaskDetailScreen(taskSlug: state.pathParameters["slug"]!),
    ),
    GoRoute(path: "/profile", builder: (_, __) => const ProfileScreen()),
    GoRoute(
      path: "/custom-task/:id",
      builder: (_, state) =>
          CustomTaskDetailScreen(taskId: state.pathParameters["id"]!),
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
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B6CA8),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: false,
          elevation: 0,
          scrolledUnderElevation: 1,
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: Colors.grey.shade200),
          ),
          margin: EdgeInsets.zero,
        ),
        listTileTheme: const ListTileThemeData(
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        ),
      ),
      routerConfig: _router,
    );
  }
}
