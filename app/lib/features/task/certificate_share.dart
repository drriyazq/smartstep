import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../domain/masteries.dart';
import 'certificate_card.dart';

/// Caption appended to the image when sharing. Focuses on the child's
/// achievement, not the app. Play Store link is subtle.
String _captionForSkill({
  required String childName,
  required String taskTitle,
}) {
  final name = childName.trim().split(RegExp(r'\s+')).first;
  if (name.isEmpty) {
    return '🌟 Another real-world skill mastered.\n\nareafair.in/smartstep';
  }
  return '🌟 $name just mastered "$taskTitle".\n\nareafair.in/smartstep';
}

String _captionForMastery({
  required String childName,
  required Mastery m,
}) {
  final name = childName.trim().split(RegExp(r'\s+')).first;
  final subject = name.isEmpty ? 'They' : name;
  return '★ MASTERY MILESTONE ★\n\n'
      '$subject ${m.celebration.substring(0, 1).toLowerCase()}${m.celebration.substring(1)}\n\n'
      'areafair.in/smartstep';
}

// ─────────────────────────────────────────────── Skill preview ──

class SkillCertificatePreview extends StatelessWidget {
  const SkillCertificatePreview({
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
    return _CertificatePreviewScaffold(
      title: 'Share this win',
      certificate: SkillCertificate(
        childName: childName,
        childAge: childAge,
        taskTitle: taskTitle,
        categorySlug: categorySlug,
        categoryEmoji: categoryEmoji,
        completedAt: completedAt,
      ),
      aspectRatio: 1.0,
      caption: _captionForSkill(childName: childName, taskTitle: taskTitle),
    );
  }
}

// ─────────────────────────────────────────────── Mastery preview ──

class MasteryCertificatePreview extends StatelessWidget {
  const MasteryCertificatePreview({
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
    return _CertificatePreviewScaffold(
      title: '★ Mastery Earned',
      certificate: MasteryCertificate(
        childName: childName,
        childAge: childAge,
        mastery: mastery,
        earnedAt: earnedAt,
      ),
      aspectRatio: 1080 / 1350,
      caption: _captionForMastery(childName: childName, m: mastery),
    );
  }
}

// ─────────────────────────────────────────────── Scaffold ──

class _CertificatePreviewScaffold extends StatefulWidget {
  const _CertificatePreviewScaffold({
    required this.title,
    required this.certificate,
    required this.aspectRatio,
    required this.caption,
  });

  final String title;
  final Widget certificate;
  final double aspectRatio;
  final String caption;

  @override
  State<_CertificatePreviewScaffold> createState() =>
      _CertificatePreviewScaffoldState();
}

class _CertificatePreviewScaffoldState
    extends State<_CertificatePreviewScaffold> {
  final GlobalKey _boundaryKey = GlobalKey();
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Center(
                  child: AspectRatio(
                    aspectRatio: widget.aspectRatio,
                    child: FittedBox(
                      fit: BoxFit.contain,
                      child: RepaintBoundary(
                        key: _boundaryKey,
                        child: widget.certificate,
                      ),
                    ),
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  icon: _busy
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.share_outlined),
                  label: Text(_busy ? 'Preparing…' : 'Share Certificate'),
                  onPressed: _busy ? null : _share,
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _share() async {
    setState(() => _busy = true);
    try {
      final bytes = await _capturePng();
      final file = await _writeTempFile(bytes);
      await Share.shareXFiles(
        [XFile(file.path, mimeType: 'image/png')],
        text: widget.caption,
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not share: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<Uint8List> _capturePng() async {
    final boundary = _boundaryKey.currentContext!.findRenderObject()
        as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 1.0);
    final data = await image.toByteData(format: ui.ImageByteFormat.png);
    return data!.buffer.asUint8List();
  }

  Future<File> _writeTempFile(Uint8List bytes) async {
    final dir = await getTemporaryDirectory();
    final filename =
        'smartstep_cert_${DateTime.now().millisecondsSinceEpoch}.png';
    final file = File('${dir.path}/$filename');
    await file.writeAsBytes(bytes);
    return file;
  }
}
