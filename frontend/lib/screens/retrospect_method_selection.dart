import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/retrospect_writing_screen.dart';
import 'package:reme/services/retrospect_api.dart';
import 'package:reme/themes/color.dart';

class RetrospectMethodSelection extends StatefulWidget {
  final List<Map<String, dynamic>> selectedChallenges;
  final String retrospectType;

  const RetrospectMethodSelection({
    super.key,
    required this.selectedChallenges,
    required this.retrospectType,
  });

  @override
  State<RetrospectMethodSelection> createState() =>
      _RetrospectMethodSelectionState();
}

class _RetrospectMethodSelectionState extends State<RetrospectMethodSelection> {
  int _selectedMethodIndex = -1;
  bool _isLoaded = false;

  // 회고 방법 데이터
  late final List<Map<String, dynamic>> _retrospectMethods = [];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    getTemplateList().then((value) {
      for (var template in value) {
        if (template['owner_type'] == widget.retrospectType) {
          _retrospectMethods.add(template);
        }
      }
      setState(() {
        _isLoaded = true;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_isLoaded) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        elevation: 0,
        centerTitle: false,
        title: null,
        toolbarHeight: 40,
        leadingWidth: 52,
        leading: GestureDetector(
          onTap: () {
            Navigator.pop(context);
          },
          child: Container(
            margin: const EdgeInsets.only(left: 16),
            child: const Icon(
              TabBarIcon.leftArrow,
              size: 20,
              color: Colors.white,
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // 타이틀 텍스트
          const Padding(
            padding: EdgeInsets.fromLTRB(21.0, 15.0, 16.0, 0),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '어떤 방법으로 회고해 볼까요?',
                style: TextStyle(
                  color: Colors.white,
                  fontFamily: 'Pretendard',
                  fontSize: 27,
                  fontWeight: FontWeight.w800,
                  height: 1.50,
                  letterSpacing: 0.54,
                ),
              ),
            ),
          ),
          Container(
            margin: EdgeInsets.only(right: 21.w),
            alignment: Alignment.centerRight,
            child: IconButton(
              onPressed: () {
                Navigator.pushNamed(context, Routes.addTemplate);
              },
              icon: Icon(
                Icons.add_outlined,
                color: Colors.white,
                size: 30.sp,
              ),
            ),
          ),

          // 회고 방법 리스트
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              itemCount: _retrospectMethods.length,
              itemBuilder: (context, index) {
                final method = _retrospectMethods[index];
                final isSelected = index == _selectedMethodIndex;

                // 태그 리스트
                List<Widget> tagWidgets = [];
                if (method['tags'] != null && method['tags'].isNotEmpty) {
                  for (String tag in method['tags']) {
                    tagWidgets.add(
                      Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: Text(
                          '#$tag',
                          style: TextStyle(
                            color: isSelected
                                ? Colors.white
                                : const Color(0xFF3B82F6),
                            fontFamily: 'Pretendard',
                            fontSize: 15,
                          ),
                        ),
                      ),
                    );
                  }
                }

                return Container(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  padding: const EdgeInsets.symmetric(vertical: 20.0),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFF1C398E)
                        : boxBackgroundColor,
                    borderRadius: BorderRadius.circular(16),
                    border: isSelected
                        ? Border.all(
                            color: const Color.fromARGB(255, 67, 79, 255),
                            width: 1.5)
                        : null,
                  ),
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _selectedMethodIndex = index;
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Method name and tags in same row
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Method name
                              Expanded(
                                child: Text(
                                  method['name'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'Pretendard',
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),

                              // Method tags
                              Row(
                                children: tagWidgets,
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),

                          // Method description
                          Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Text(
                              method['description'] ?? '',
                              style: TextStyle(
                                color: const Color(0xFFC3C3C3),
                                fontFamily: 'Pretendard',
                                fontSize: 15,
                                fontWeight: isSelected
                                    ? FontWeight.w500
                                    : FontWeight.normal,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.fromLTRB(16.0, 0, 16.0, 16.0),
        child: InkWell(
          onTap: () {
            if (_selectedMethodIndex != -1) {
              // Navigate to the retrospect writing screen
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => RetrospectWritingScreen(
                    methodName: _retrospectMethods[_selectedMethodIndex]
                        ['name'],
                    selectedChallenges: widget.selectedChallenges,
                    selectedMethod: _retrospectMethods[_selectedMethodIndex],
                  ),
                ),
              );
            } else {
              // Show error if no method is selected
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('회고 방법을 선택해주세요'),
                  duration: Duration(seconds: 2),
                ),
              );
            }
          },
          child: Container(
            height: 60,
            decoration: BoxDecoration(
              color: const Color(0xFF223990),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: Text(
                '선택완료',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
