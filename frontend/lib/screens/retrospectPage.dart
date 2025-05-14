import 'package:flutter/material.dart';
import 'package:reme/screens/challengeList.dart';
import 'package:reme/screens/retrospectList.dart';

class RetroPage extends StatefulWidget {
  final int tabNo;
  const RetroPage({super.key, required this.tabNo});

  @override
  State<RetroPage> createState() => _RetroPageState(this.tabNo);
}

class _RetroPageState extends State<RetroPage>
    with SingleTickerProviderStateMixin {
  ImageProvider? plusIcon;

  final int tapNo;
  _RetroPageState(this.tapNo);

  final List<Widget> _pageOptions = [
    const RetroSpectList(),
    const ChallengeList(),
  ];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
  }

  @override
  void dispose() {
    // TODO: implement dispose
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _pageOptions[widget.tabNo];
  }
}
