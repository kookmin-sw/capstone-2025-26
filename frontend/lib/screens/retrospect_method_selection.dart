import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

class RetrospectMethodSelection extends StatefulWidget {
  const RetrospectMethodSelection({super.key});

  @override
  State<RetrospectMethodSelection> createState() =>
      _RetrospectMethodSelectionState();
}

class _RetrospectMethodSelectionState extends State<RetrospectMethodSelection> {
  int _selectedMethodIndex = -1;

  // 회고 방법 데이터
  final List<Map<String, dynamic>> _retrospectMethods = [
    {
      'name': 'KPT',
      'description': '요즘 핫한 회고 방법',
      'tags': ['정석', '트렌디'],
    },
    {
      'name': 'CSS',
      'description': '프론트엔드가 아니에요! Continue, Stop, Start',
      'tags': ['직관적', '빠르게'],
    },
    {
      'name': '4L',
      'description': 'Liked, Learned, Lacked, Longed for',
      'tags': ['상세하게', '꼼꼼히'],
    },
    {
      'name': 'KIPET',
      'description': '내가 만든 차세대 회고 기법',
      'tags': [],
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: false,
        title: null,
        leadingWidth: 52,
        leading: GestureDetector(
          onTap: () {
            Navigator.pop(context);
          },
          child: Container(
            margin: const EdgeInsets.only(top: 1, left: 16),
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
            padding: EdgeInsets.fromLTRB(21.0, 27.0, 16.0, 27.0),
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

          // 회고 방법 리스트
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
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
                          style: const TextStyle(
                            color: Color(0xFF3B82F6),
                            fontFamily: 'Pretendard',
                            fontSize: 14,
                          ),
                        ),
                      ),
                    );
                  }
                }

                return Container(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A1A),
                    borderRadius: BorderRadius.circular(16),
                    border: isSelected
                        ? Border.all(color: const Color(0xFF223990), width: 2)
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
                                    fontSize: 20,
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
                              method['description'],
                              style: const TextStyle(
                                color: Colors.white,
                                fontFamily: 'Pretendard',
                                fontSize: 16,
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
              // Navigate to the next step (would be implemented later)
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                      '선택된 회고 방법: ${_retrospectMethods[_selectedMethodIndex]['name']}'),
                  duration: const Duration(seconds: 2),
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
