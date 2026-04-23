import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'data/local/hive_setup.dart';
import 'features/ladder/category_ladder_screen.dart';
import 'features/ladder/dashboard_screen.dart';
import 'features/legal/privacy_policy_screen.dart';
import 'features/legal/terms_screen.dart';
import 'features/onboarding/baseline_screen.dart';
import 'features/onboarding/child_profile_screen.dart';
import 'features/onboarding/consent_screen.dart';
import 'features/onboarding/environment_screen.dart';
import 'features/onboarding/phone_screen.dart';
import 'features/onboarding/religion_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/task/custom_task_detail_screen.dart';
import 'features/task/task_detail_screen.dart';

final _router = GoRouter(
  initialLocation: "/consent",
  redirect: (context, state) {
    final path = state.matchedLocation;

    // Legal screens are always reachable (from onboarding + profile)
    if (path.startsWith('/legal/')) return null;

    final consentGiven = HiveSetup.sessionBox.get('consent_given') == '1';
    final hasProfile = HiveSetup.childBox.isNotEmpty;
    final onConsent = path == '/consent';
    final onboardingPath =
        path.startsWith("/onboarding") || path == "/phone";
    final addingChild = state.uri.queryParameters['adding'] == 'true';

    // No consent yet → only /consent allowed
    if (!consentGiven && !onConsent) return "/consent";
    // Consent given and already has at least one child → skip onboarding
    if (consentGiven && hasProfile && (onConsent || (onboardingPath && !addingChild))) {
      return "/dashboard";
    }
    // Consent given but no child yet → go through onboarding from /phone
    if (consentGiven && !hasProfile && onConsent) return "/phone";
    if (consentGiven && !hasProfile && !onboardingPath) return "/phone";
    return null;
  },
  routes: [
    GoRoute(path: "/consent", builder: (_, __) => const ConsentScreen()),
    GoRoute(path: "/legal/privacy", builder: (_, __) => const PrivacyPolicyScreen()),
    GoRoute(path: "/legal/terms", builder: (_, __) => const TermsScreen()),
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
      path: "/onboarding/religion",
      builder: (_, state) => ReligionScreen(
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
      path: "/category/:cat",
      builder: (_, state) => CategoryLadderScreen(
        category: state.pathParameters["cat"]!,
      ),
    ),
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
