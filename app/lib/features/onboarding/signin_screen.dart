import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../../data/api/client.dart';
import '../../data/local/hive_setup.dart';

class SignInScreen extends ConsumerStatefulWidget {
  const SignInScreen({super.key});

  @override
  ConsumerState<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends ConsumerState<SignInScreen> {
  bool _busy = false;
  String? _error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to SmartStep')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 40),
            const Icon(Icons.stairs_outlined, size: 72, color: Color(0xFF1B6CA8)),
            const SizedBox(height: 24),
            const Text(
              'Sign in to get started',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            Text(
              'Your progress stays on this device. We only use Google to identify you securely.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.grey.shade700, height: 1.4),
            ),
            const SizedBox(height: 48),
            FilledButton.icon(
              onPressed: _busy ? null : _signInWithGoogle,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              icon: _busy
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.account_circle_outlined),
              label: Text(_busy ? 'Signing in…' : 'Continue with Google'),
            ),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.red),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _signInWithGoogle() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final googleUser = await GoogleSignIn().signIn();
      if (googleUser == null) {
        setState(() => _busy = false);
        return;
      }
      final googleAuth = await googleUser.authentication;
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );
      final userCredential =
          await FirebaseAuth.instance.signInWithCredential(credential);
      final idToken = await userCredential.user!.getIdToken();

      final dio = ref.read(dioProvider);
      final resp = await dio.post<Map<String, dynamic>>(
        '/auth/firebase/',
        data: {'id_token': idToken},
      );
      await HiveSetup.sessionBox.put('access_token', resp.data!['access']);
      await HiveSetup.sessionBox.put('refresh_token', resp.data!['refresh']);

      if (!mounted) return;
      context.go('/onboarding/child');
    } on FirebaseAuthException catch (e) {
      setState(() => _error = e.message ?? 'Sign-in failed. Try again.');
    } on DioException catch (e) {
      setState(() => _error = 'Server error: ${e.message}');
    } catch (e) {
      setState(() => _error = 'Sign-in failed: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
