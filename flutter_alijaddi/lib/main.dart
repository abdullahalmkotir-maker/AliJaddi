import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AliJaddiApp());
}

/// ألوان قريبة من هوية المنصّة (teal).
class AliJaddiApp extends StatelessWidget {
  const AliJaddiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'علي جدّي',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ar'),
      supportedLocales: const [Locale('ar'), Locale('en')],
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0D9488)),
        useMaterial3: true,
      ),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child ?? const SizedBox.shrink(),
        );
      },
      home: const GatewayHomePage(),
    );
  }
}

class GatewayHomePage extends StatefulWidget {
  const GatewayHomePage({super.key});

  @override
  State<GatewayHomePage> createState() => _GatewayHomePageState();
}

class _GatewayHomePageState extends State<GatewayHomePage> {
  final _baseUrl = TextEditingController(
    text: _defaultGatewayUrl(),
  );
  final _routeText = TextEditingController(text: 'bentoml gpu inference serving');
  String _output = '';
  bool _busy = false;

  /// محاكي أندرويد: 10.0.2.2 يوجّه إلى localhost الجهاز المضيف.
  static String _defaultGatewayUrl() {
    return 'http://127.0.0.1:8012';
  }

  Future<void> _getHealth() async {
    await _request(() async {
      final uri = Uri.parse('${_baseUrl.text.trim()}/health');
      final res = await http.get(uri).timeout(const Duration(seconds: 12));
      _output = '${res.statusCode}\n${res.body}';
    });
  }

  Future<void> _postSquadRoute() async {
    await _request(() async {
      final uri = Uri.parse('${_baseUrl.text.trim()}/squad/route');
      final res = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json; charset=utf-8'},
            body: jsonEncode({'text': _routeText.text}),
          )
          .timeout(const Duration(seconds: 12));
      _output = '${res.statusCode}\n${utf8.decode(res.bodyBytes)}';
    });
  }

  Future<void> _request(Future<void> Function() fn) async {
    setState(() {
      _busy = true;
      _output = '…';
    });
    try {
      await fn();
    } catch (e) {
      _output = 'خطأ: $e';
    }
    setState(() => _busy = false);
  }

  @override
  void dispose() {
    _baseUrl.dispose();
    _routeText.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('علي جدّي — اتصال بالبوابة'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'عنوان البوابة (FastAPI stub أو أي خادم)',
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _baseUrl,
            textAlign: TextAlign.left,
            textDirection: TextDirection.ltr,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              hintText: 'http://127.0.0.1:8012',
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'للمحاكي أندرويد استخدم http://10.0.2.2:8012 بدل 127.0.0.1',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _busy ? null : _getHealth,
            icon: const Icon(Icons.health_and_safety_outlined),
            label: const Text('فحص /health'),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _routeText,
            decoration: const InputDecoration(
              labelText: 'نص التوجيه (مساعد السرب)',
              border: OutlineInputBorder(),
            ),
            maxLines: 2,
          ),
          const SizedBox(height: 12),
          FilledButton.tonalIcon(
            onPressed: _busy ? null : _postSquadRoute,
            icon: const Icon(Icons.alt_route),
            label: const Text('POST /squad/route'),
          ),
          const SizedBox(height: 24),
          Text('الاستجابة', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          SelectableText(
            _output.isEmpty ? '—' : _output,
            style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
          ),
        ],
      ),
    );
  }
}
