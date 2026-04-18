import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/client.dart';
import '../../data/local/hive_setup.dart';

class PhoneScreen extends ConsumerStatefulWidget {
  const PhoneScreen({super.key});

  @override
  ConsumerState<PhoneScreen> createState() => _PhoneScreenState();
}

class _PhoneScreenState extends ConsumerState<PhoneScreen> {
  final _phone = TextEditingController();
  final _otp = TextEditingController();

  bool _sent = false;
  bool _busy = false;
  String? _error;
  String? _verificationId;

  @override
  void dispose() {
    _phone.dispose();
    _otp.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to SmartStep')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 16),
            const Text(
              'Enter your mobile number to get started.',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 24),
            // Phone number field with country code
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('+91', style: TextStyle(fontSize: 16)),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: _phone,
                    keyboardType: TextInputType.phone,
                    enabled: !_sent,
                    maxLength: 10,
                    decoration: const InputDecoration(
                      labelText: 'Phone number',
                      counterText: '',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),
            if (_sent) ...[
              const SizedBox(height: 16),
              TextField(
                controller: _otp,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: const InputDecoration(
                  labelText: '6-digit OTP',
                  counterText: '',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: _busy ? null : _resend,
                child: const Text('Resend OTP'),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _busy ? null : (_sent ? _verifyOtp : _sendOtp),
              child: _busy
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Text(_sent ? 'Verify OTP' : 'Send OTP'),
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
    );
  }

  String get _fullPhone => '+91${_phone.text.trim()}';

  Future<void> _sendOtp() async {
    final phone = _phone.text.trim();
    if (phone.length != 10) {
      setState(() => _error = 'Enter a valid 10-digit mobile number.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });

    await FirebaseAuth.instance.verifyPhoneNumber(
      phoneNumber: _fullPhone,
      timeout: const Duration(seconds: 60),
      verificationCompleted: (PhoneAuthCredential credential) async {
        // Auto-verified on Android (rare) — sign in immediately.
        await _signIn(credential);
      },
      verificationFailed: (FirebaseAuthException e) {
        setState(() {
          _error = e.message ?? 'Verification failed. Try again.';
          _busy = false;
        });
      },
      codeSent: (String verificationId, int? resendToken) {
        setState(() {
          _verificationId = verificationId;
          _sent = true;
          _busy = false;
          _error = null;
        });
      },
      codeAutoRetrievalTimeout: (String verificationId) {
        _verificationId = verificationId;
      },
    );
  }

  Future<void> _resend() async {
    setState(() {
      _sent = false;
      _otp.clear();
      _error = null;
    });
    await _sendOtp();
  }

  Future<void> _verifyOtp() async {
    if (_otp.text.trim().length != 6) {
      setState(() => _error = 'Enter the 6-digit OTP.');
      return;
    }
    if (_verificationId == null) {
      setState(() => _error = 'Something went wrong. Please resend OTP.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final credential = PhoneAuthProvider.credential(
      verificationId: _verificationId!,
      smsCode: _otp.text.trim(),
    );
    await _signIn(credential);
  }

  Future<void> _signIn(PhoneAuthCredential credential) async {
    try {
      final userCredential =
          await FirebaseAuth.instance.signInWithCredential(credential);
      final idToken = await userCredential.user!.getIdToken();

      // Exchange Firebase ID token for Django JWT.
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
      setState(() => _error = e.message ?? 'Invalid OTP. Try again.');
    } on DioException catch (e) {
      setState(() => _error = 'Server error: ${e.message}');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
