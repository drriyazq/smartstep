import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Incremented any time task progress changes (complete, skip, reset).
/// The dashboard watches this so it rebuilds immediately after any change.
final progressVersionProvider = StateProvider<int>((ref) => 0);
