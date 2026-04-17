import 'package:dio/dio.dart';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Welcome to SmartStep")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Dev mode: any phone number works. OTP is 000000.",
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _phone,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(labelText: "Phone number"),
              enabled: !_sent,
            ),
            if (_sent) ...[
              const SizedBox(height: 16),
              TextField(
                controller: _otp,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: "6-digit OTP"),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _busy ? null : (_sent ? _verify : _requestOtp),
              child: Text(_sent ? "Verify" : "Send OTP"),
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

  void _requestOtp() {
    if (_phone.text.trim().isEmpty) {
      setState(() => _error = "Enter a phone number.");
      return;
    }
    setState(() {
      _sent = true;
      _error = null;
    });
  }

  Future<void> _verify() async {
    if (_otp.text != "000000") {
      setState(() => _error = "Dev OTP is 000000.");
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final dio = ref.read(dioProvider);
      final resp = await dio.post<Map<String, dynamic>>("/auth/dev-token/");
      await HiveSetup.sessionBox.put("access_token", resp.data!["access"]);
      await HiveSetup.sessionBox.put("refresh_token", resp.data!["refresh"]);
      if (!mounted) return;
      context.go("/onboarding/child");
    } on DioException catch (e) {
      setState(() => _error = "Could not reach the server: ${e.message}");
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
