import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/client.dart';
import '../../data/local/hive_setup.dart';
import '../../data/sync/remote_sync.dart';

/// Phone-OTP sign-in.
///
/// India (+91) → backend WhatsApp OTP via `/auth/otp/{send,verify}/`.
/// Anywhere else → Firebase Phone Auth (SMS), then `/auth/firebase/` to
/// exchange the Firebase ID token for a SmartStep JWT pair.
class SignInScreen extends ConsumerStatefulWidget {
  const SignInScreen({super.key});

  @override
  ConsumerState<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends ConsumerState<SignInScreen> {
  final _phoneCtrl = TextEditingController(text: '+91');
  final _otpCtrl = TextEditingController();

  bool _otpSent = false;
  bool _busy = false;
  String? _error;
  String? _firebaseVerificationId;

  @override
  void dispose() {
    _phoneCtrl.dispose();
    _otpCtrl.dispose();
    super.dispose();
  }

  bool get _isIndianNumber => _phoneCtrl.text.trim().startsWith('+91');

  String? _validatedPhone() {
    final raw = _phoneCtrl.text.trim();
    if (!raw.startsWith('+')) return null;
    final digits = raw.substring(1);
    if (!RegExp(r'^\d{8,15}$').hasMatch(digits)) return null;
    return raw;
  }

  // ── Send ─────────────────────────────────────────────────────────────────

  Future<void> _sendOtp() async {
    final phone = _validatedPhone();
    if (phone == null) {
      setState(() => _error =
          'Enter a valid phone number with country code (e.g. +919876543210).');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    if (_isIndianNumber) {
      await _sendWhatsappOtp(phone);
    } else {
      await _sendFirebaseOtp(phone);
    }
  }

  Future<void> _sendWhatsappOtp(String phone) async {
    try {
      final dio = ref.read(dioProvider);
      await dio.post('/auth/otp/send/', data: {'phone': phone});
      if (!mounted) return;
      setState(() {
        _busy = false;
        _otpSent = true;
      });
    } on DioException catch (e) {
      final msg = e.response?.data is Map
          ? (e.response!.data['detail']?.toString() ??
              'Could not send OTP. Try again.')
          : 'Could not send OTP. Try again.';
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = msg;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = 'Could not send OTP: $e';
      });
    }
  }

  Future<void> _sendFirebaseOtp(String phone) async {
    try {
      await FirebaseAuth.instance.verifyPhoneNumber(
        phoneNumber: phone,
        timeout: const Duration(seconds: 60),
        verificationCompleted: (credential) async {
          await _signInWithFirebaseCredential(credential);
        },
        verificationFailed: (e) {
          if (!mounted) return;
          setState(() {
            _busy = false;
            _error = 'Verification failed: ${e.message ?? e.code}';
          });
        },
        codeSent: (verificationId, _) {
          if (!mounted) return;
          setState(() {
            _busy = false;
            _otpSent = true;
            _firebaseVerificationId = verificationId;
          });
        },
        codeAutoRetrievalTimeout: (_) {},
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = 'Could not send SMS: $e';
      });
    }
  }

  // ── Verify ───────────────────────────────────────────────────────────────

  Future<void> _verifyOtp() async {
    final code = _otpCtrl.text.trim();
    if (code.length != 6) {
      setState(() => _error = 'Enter the 6-digit code.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    if (_isIndianNumber) {
      await _verifyWhatsappOtp(code);
    } else {
      await _verifyFirebaseOtp(code);
    }
  }

  Future<void> _verifyWhatsappOtp(String code) async {
    final phone = _validatedPhone()!;
    try {
      final dio = ref.read(dioProvider);
      final resp = await dio.post<Map<String, dynamic>>(
        '/auth/otp/verify/',
        data: {'phone': phone, 'code': code},
      );
      await _onJwtPairReceived(resp.data!);
    } on DioException catch (e) {
      final msg = e.response?.data is Map
          ? (e.response!.data['detail']?.toString() ?? 'Verification failed.')
          : 'Verification failed.';
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = msg;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = 'Verification failed: $e';
      });
    }
  }

  Future<void> _verifyFirebaseOtp(String code) async {
    if (_firebaseVerificationId == null) {
      setState(() {
        _busy = false;
        _error = 'Request a code first.';
      });
      return;
    }
    final credential = PhoneAuthProvider.credential(
      verificationId: _firebaseVerificationId!,
      smsCode: code,
    );
    await _signInWithFirebaseCredential(credential);
  }

  Future<void> _signInWithFirebaseCredential(
      PhoneAuthCredential credential) async {
    try {
      final result =
          await FirebaseAuth.instance.signInWithCredential(credential);
      final idToken = await result.user?.getIdToken();
      if (idToken == null) {
        throw Exception('No Firebase ID token returned.');
      }
      final dio = ref.read(dioProvider);
      final resp = await dio.post<Map<String, dynamic>>(
        '/auth/firebase/',
        data: {'id_token': idToken},
      );
      await _onJwtPairReceived(resp.data!);
    } on FirebaseAuthException catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = e.message ?? 'Sign-in failed. Try again.';
      });
    } on DioException catch (e) {
      final msg = e.response?.data is Map
          ? (e.response!.data['detail']?.toString() ?? 'Server error.')
          : 'Server error: ${e.message}';
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = msg;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = 'Sign-in failed: $e';
      });
    }
  }

  Future<void> _onJwtPairReceived(Map<String, dynamic> data) async {
    await HiveSetup.sessionBox.put('access_token', data['access']);
    await HiveSetup.sessionBox.put('refresh_token', data['refresh']);
    if (data['uid'] != null) {
      await HiveSetup.sessionBox.put('auth_uid', data['uid']);
    }
    // Hydrate the local cache from server. If the user already has a
    // profile on another device, they land straight on the dashboard;
    // otherwise we send them through onboarding.
    try {
      await ref.read(remoteSyncProvider).bootstrap();
    } on SyncException catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = e.userMessage;
      });
      return;
    }
    if (!mounted) return;
    final hasProfile = HiveSetup.childBox.isNotEmpty;
    context.go(hasProfile ? '/dashboard' : '/onboarding/child');
  }

  // ── UI ───────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to SmartStep')),
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(
            24,
            24,
            24,
            24 + MediaQuery.of(context).viewInsets.bottom,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.stairs_outlined,
                  size: 64, color: Color(0xFF1B6CA8)),
              const SizedBox(height: 16),
              const Text(
                'Sign in to get started',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              Text(
                _otpSent
                    ? (_isIndianNumber
                        ? 'Enter the 6-digit code we sent to ${_phoneCtrl.text} on WhatsApp.'
                        : 'Enter the 6-digit code we sent to ${_phoneCtrl.text} by SMS.')
                    : 'Indian numbers receive the code on WhatsApp. Other countries get an SMS.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade700,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 32),
              if (!_otpSent)
                TextField(
                  controller: _phoneCtrl,
                  keyboardType: TextInputType.phone,
                  enabled: !_busy,
                  decoration: const InputDecoration(
                    labelText: 'Phone number',
                    hintText: '+919876543210',
                    prefixIcon: Icon(Icons.phone_outlined),
                    border: OutlineInputBorder(),
                  ),
                )
              else ...[
                TextField(
                  controller: _otpCtrl,
                  keyboardType: TextInputType.number,
                  enabled: !_busy,
                  maxLength: 6,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                  ],
                  decoration: const InputDecoration(
                    labelText: '6-digit code',
                    prefixIcon: Icon(Icons.lock_outline),
                    border: OutlineInputBorder(),
                  ),
                ),
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: _busy
                        ? null
                        : () => setState(() {
                              _otpSent = false;
                              _otpCtrl.clear();
                              _firebaseVerificationId = null;
                              _error = null;
                            }),
                    child: const Text('Change number'),
                  ),
                ),
              ],
              if (_error != null) ...[
                const SizedBox(height: 8),
                Text(
                  _error!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              ],
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _busy ? null : (_otpSent ? _verifyOtp : _sendOtp),
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
                    : Icon(_otpSent
                        ? Icons.check_circle_outline
                        : Icons.send_outlined),
                label: Text(_busy
                    ? (_otpSent ? 'Verifying…' : 'Sending…')
                    : (_otpSent ? 'Verify code' : 'Send code')),
              ),
              const SizedBox(height: 12),
              Text(
                'Your progress is saved to your SmartStep account so you can pick up where you left off on any device.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
