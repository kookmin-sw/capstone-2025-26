import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/retrospectList.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/iconToImage.dart';
import 'package:reme/widgets/challengeTypeItem.dart';
import 'package:reme/widgets/crewBox.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';

class RetroPage extends StatefulWidget {
  final int tabNo;
  const RetroPage({super.key, required this.tabNo});

  @override
  State<RetroPage> createState() => _RetroPageState(this.tabNo);
}

class _RetroPageState extends State<RetroPage>
    with SingleTickerProviderStateMixin {
  ImageProvider? plusIcon;
  late TabController _tabController;

  final int tapNo;
  _RetroPageState(this.tapNo);

  final List<Widget> _pageOptions = [
    RetroSpectList(),
    Container(),
  ];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    // TODO: implement dispose
    super.dispose();
    _tabController.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _pageOptions[widget.tabNo];
  }
}
