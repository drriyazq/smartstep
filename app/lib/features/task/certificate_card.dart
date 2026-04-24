import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../domain/masteries.dart';

/// Short URL printed on every certificate and encoded in the QR code.
const String kSmartStepShareUrl = 'https://areafair.in/smartstep';

/// Category color theming — matches dashboard categoryMeta().
Color categoryColor(String category) => switch (category) {
      'financial' => const Color(0xFF1565C0),
      'household' => const Color(0xFF2E7D32),
      'digital' => const Color(0xFF6A1B9A),
      'navigation' => const Color(0xFFE65100),
      'cognitive' => const Color(0xFF00695C),
      'social' => const Color(0xFFC62828),
      _ => const Color(0xFF546E7A),
    };

String _firstName(String fullName) {
  final trimmed = fullName.trim();
  if (trimmed.isEmpty) return 'They';
  return trimmed.split(RegExp(r'\s+')).first;
}

String _formatDate(DateTime d) => DateFormat('d MMMM yyyy').format(d);

// ─────────────────────────────────────────────── Skill (single task) ──

/// Simple certificate shown when a single task is completed.
/// 1080x1080 — square, Instagram-friendly.
class SkillCertificate extends StatelessWidget {
  const SkillCertificate({
    super.key,
    required this.childName,
    required this.childAge,
    required this.taskTitle,
    required this.categorySlug,
    required this.categoryEmoji,
    required this.completedAt,
  });

  final String childName;
  final int childAge;
  final String taskTitle;
  final String categorySlug;
  final String categoryEmoji;
  final DateTime completedAt;

  @override
  Widget build(BuildContext context) {
    final color = categoryColor(categorySlug);
    return Container(
      width: 1080,
      height: 1080,
      color: Colors.white,
      child: Stack(
        children: [
          // Top colored band
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            height: 140,
            child: Container(color: color),
          ),
          // Bottom colored strip
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            height: 40,
            child: Container(color: color),
          ),
          // Content
          Padding(
            padding: const EdgeInsets.fromLTRB(60, 180, 60, 80),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  'SmartStep',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w600,
                    color: color,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 80),
                Text(categoryEmoji, style: const TextStyle(fontSize: 120)),
                const SizedBox(height: 30),
                const Text(
                  'SKILL UNLOCKED',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 4,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 40),
                Text(
                  _firstName(childName),
                  style: const TextStyle(
                    fontSize: 72,
                    fontWeight: FontWeight.w800,
                    color: Colors.black,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'age $childAge',
                  style: TextStyle(
                    fontSize: 22,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 40),
                const Text(
                  'just mastered',
                  style: TextStyle(
                    fontSize: 24,
                    color: Colors.black54,
                    fontStyle: FontStyle.italic,
                  ),
                ),
                const SizedBox(height: 20),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 40),
                  child: Text(
                    taskTitle,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 44,
                      fontWeight: FontWeight.w700,
                      color: color,
                      height: 1.2,
                    ),
                  ),
                ),
                const Spacer(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _formatDate(completedAt),
                          style: TextStyle(
                            fontSize: 20,
                            color: Colors.grey.shade700,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Start your own journey:',
                          style: TextStyle(fontSize: 14, color: Colors.black54),
                        ),
                        const Text(
                          'areafair.in/smartstep',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                    QrImageView(
                      data: kSmartStepShareUrl,
                      size: 140,
                      backgroundColor: Colors.white,
                      padding: EdgeInsets.zero,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────── Mastery (compound) ──

/// Premium certificate shown when a mastery capability is earned.
/// 1080x1350 — portrait, works on Instagram Story and WhatsApp status.
class MasteryCertificate extends StatelessWidget {
  const MasteryCertificate({
    super.key,
    required this.childName,
    required this.childAge,
    required this.mastery,
    required this.earnedAt,
  });

  final String childName;
  final int childAge;
  final Mastery mastery;
  final DateTime earnedAt;

  @override
  Widget build(BuildContext context) {
    final base = categoryColor(mastery.category);
    // Darker + lighter endpoints for a gradient
    final dark = Color.alphaBlend(Colors.black.withOpacity(0.25), base);
    final light = Color.alphaBlend(Colors.white.withOpacity(0.85), base);

    return Container(
      width: 1080,
      height: 1350,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [light, Colors.white, Colors.white],
          stops: const [0.0, 0.45, 1.0],
        ),
      ),
      child: Stack(
        children: [
          // Gold-feel outer frame
          Positioned.fill(
            child: Container(
              margin: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFC9A44D), width: 4),
              ),
              child: Container(
                margin: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  border: Border.all(color: const Color(0xFFC9A44D), width: 1),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(80, 80, 80, 70),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  'SmartStep',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w600,
                    color: dark,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  '★ MASTERY MILESTONE ★',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 6,
                    color: Color(0xFFB08A2F),
                  ),
                ),
                const SizedBox(height: 44),
                Text(mastery.emoji, style: const TextStyle(fontSize: 150)),
                const SizedBox(height: 20),
                Text(
                  _firstName(childName),
                  style: const TextStyle(
                    fontSize: 80,
                    fontWeight: FontWeight.w800,
                    color: Colors.black,
                    height: 1.05,
                  ),
                ),
                Text(
                  'age $childAge',
                  style: TextStyle(
                    fontSize: 22,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 36),
                Text(
                  'is now',
                  style: TextStyle(
                    fontSize: 28,
                    color: Colors.grey.shade700,
                    fontStyle: FontStyle.italic,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  mastery.title,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 52,
                    fontWeight: FontWeight.w800,
                    color: dark,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 28),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Text(
                    mastery.celebration,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 24,
                      color: Colors.black87,
                      height: 1.45,
                    ),
                  ),
                ),
                const Spacer(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _formatDate(earnedAt),
                          style: TextStyle(
                            fontSize: 22,
                            color: Colors.grey.shade700,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Start your own journey:',
                          style: TextStyle(fontSize: 14, color: Colors.black54),
                        ),
                        const Text(
                          'areafair.in/smartstep',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                    QrImageView(
                      data: kSmartStepShareUrl,
                      size: 150,
                      backgroundColor: Colors.white,
                      padding: EdgeInsets.zero,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
