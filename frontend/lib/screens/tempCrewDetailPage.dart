import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

class CrewDetail extends StatefulWidget {
  const CrewDetail({super.key});

  @override
  State<CrewDetail> createState() => _CrewDetailState();
}

class _CrewDetailState extends State<CrewDetail>
    with SingleTickerProviderStateMixin {
  TabController? _tabController;
  final double _expandedHeight = 240.0 + 10.0; // 이미지 높이 조정
  int _selectIndex = 0;
  bool _isCollapsed = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController!.addListener(() => setState(() {
          _selectIndex = _tabController!.index;
        }));
  }

  @override
  void dispose() {
    _tabController!.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    var crewid = ModalRoute.of(context)!.settings.arguments;
    final double statusBar = MediaQuery.of(context).padding.top;

    return Scaffold(
      backgroundColor: background,
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverAppBar(
              expandedHeight: _expandedHeight,
              pinned: true,
              floating: false,
              backgroundColor: _isCollapsed ? background : Colors.transparent,
              scrolledUnderElevation: 0, // 스크롤시 appbar 색상 변경 안되게
              iconTheme: const IconThemeData(color: Colors.white),
              flexibleSpace: LayoutBuilder(
                builder: (context, constraints) {
                  final double currentHeight = constraints.biggest.height;
                  final bool isCollapsed =
                      currentHeight <= kToolbarHeight + statusBar + 5;

                  if (_isCollapsed != isCollapsed) {
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      if (mounted) setState(() => _isCollapsed = isCollapsed);
                    });
                  }

                  // 스크롤 정도에 따른 진행도 계산 (0~1)
                  double progress = 1.0 -
                      ((currentHeight - kToolbarHeight - statusBar) /
                          (_expandedHeight - kToolbarHeight - statusBar));
                  progress = progress.clamp(0.0, 1.0);

                  // 아이콘 크기 계산
                  const double startSize = 56.0;
                  const double endSize = 32.0;
                  final double iconSize =
                      startSize - (startSize - endSize) * progress;

                  // 아이콘 위치 계산
                  const double startLeft = 20.0; // 초기 좌측 위치
                  const double endLeft = 12.0; // 최종 앱바 내 위치
                  final double startTop = _expandedHeight - 180; // 초기 상단 위치
                  final double endTop =
                      statusBar + (kToolbarHeight - endSize) / 2; // 최종 앱바 내 위치

                  final double iconLeft =
                      startLeft + (endLeft - startLeft) * progress;
                  final double iconTop =
                      startTop - (startTop - endTop) * progress;

                  // 텍스트 위치 계산
                  const double textStartLeft = 20.0;
                  const double textEndLeft = 52.0;
                  final double textLeft =
                      textStartLeft + (textEndLeft - textStartLeft) * progress;

                  final double textStartTop = _expandedHeight - 120;
                  final double textEndTop =
                      statusBar + (kToolbarHeight - 16) / 2;
                  final double textTop =
                      textStartTop - (textStartTop - textEndTop) * progress;

                  // 텍스트 크기 계산
                  const double textStartSize = 18.0;
                  const double textEndSize = 16.0;
                  final double textSize =
                      textStartSize - (textStartSize - textEndSize) * progress;

                  return Stack(
                    fit: StackFit.expand,
                    children: [
                      // 1. 배경 이미지
                      Opacity(
                        opacity: 1.0 - progress,
                        child: Image.network(
                          'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
                          fit: BoxFit.cover,
                        ),
                      ),

                      // 2. 어두운 그라데이션 오버레이
                      Positioned(
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: 150,
                        child: Opacity(
                          opacity: 1.0 - progress,
                          child: Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                                colors: [
                                  Colors.transparent,
                                  Colors.black.withOpacity(0.7),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),

                      // 3. 하단 컨테이너
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: 0,
                        child: Opacity(
                          opacity: 1.0 - progress,
                          child: Container(
                            color: boxBackgroundColor,
                            padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // 크루 이미지와 이름 행
                                const Row(
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    // 투명 공간 (이미지는 따로 스택에서 조정)
                                    SizedBox(width: 56),
                                    SizedBox(width: 8),
                                    // 크루명
                                    Expanded(
                                      child: Text(
                                        '저속 노화 따라가기',
                                        style: TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.transparent,
                                        ),
                                      ),
                                    ),
                                    // 12명 텍스트
                                    Text(
                                      '👥 12명',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.white70,
                                      ),
                                    ),
                                    SizedBox(width: 150),
                                    Icon(Icons.more_vert, color: Colors.white),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                // 설명
                                const Text(
                                  '저속 노화 위주의 식사와 규칙적인 생활을 통해 삶을 재정비하고 이다현보다 오래 살기 위해 노력합니다',
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                    color: fontColor,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 16),
                                // 버튼
                                SizedBox(
                                  width: double.infinity,
                                  child: ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: c800,
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 18,
                                        vertical: 12,
                                      ),
                                    ),
                                    onPressed: () {},
                                    child: const Text(
                                      '크루 가입하기',
                                      style: TextStyle(
                                        color: fontColor,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 4),
                              ],
                            ),
                          ),
                        ),
                      ),

                      // 4. 크루 이미지 (스크롤에 따라 위치 변경)
                      Positioned(
                        left: iconLeft,
                        top: iconTop,
                        child: Container(
                          width: iconSize,
                          height: iconSize,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(
                              'https://your-crew-icon-url.com/icon.png',
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) =>
                                  Icon(
                                Icons.group,
                                size: iconSize * 0.7,
                                color: Colors.grey,
                              ),
                            ),
                          ),
                        ),
                      ),

                      // 5. 크루 이름 (스크롤에 따라 위치 변경)
                      Positioned(
                        left: textLeft,
                        top: textTop,
                        child: Text(
                          '저속 노화 따라가기',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: textSize,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),

                      // 6. 크루 멤버 수 (앱바에서만 표시)
                    ],
                  );
                },
              ),
            ),
            // 탭 메뉴
            SliverPersistentHeader(
              delegate: _SliverAppBarDelegate(
                TabBar(
                  tabAlignment: TabAlignment.start,
                  controller: _tabController,
                  labelColor: Colors.white,
                  unselectedLabelColor: Colors.white70,
                  indicatorColor: Colors.transparent,
                  dividerColor: Colors.transparent,
                  isScrollable: true,
                  tabs: [
                    _buildTab('전체', _selectIndex == 0),
                    _buildTab('공지', _selectIndex == 1),
                    _buildTab('회고', _selectIndex == 2),
                    _buildTab('게시판', _selectIndex == 3),
                  ],
                ),
              ),
              pinned: true,
            ),
          ];
        },
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildPostList(),
            _buildPostList(),
            _buildPostList(),
            _buildPostList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTab(String label, bool selected) {
    return Tab(
      child: Container(
        padding: const EdgeInsets.fromLTRB(36, 8, 36, 8),
        decoration: ShapeDecoration(
          color: selected ? c900 : boxBackgroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        child: Text(
          label,
          style: const TextStyle(
              fontSize: 18, fontWeight: FontWeight.w500, color: fontColor),
        ),
      ),
    );
  }

  Widget _buildPostList() {
    return ListView(
      padding: EdgeInsets.zero,
      children: const [
        PostCard(
          nickname: '다욤둥',
          date: '25.04.12 15:32',
          title: '다음주까지 식단 짜서 올려주세요',
          content: '저속 노화 유튜브 영상 보고\n최대한 건강하게 식단 짜서 공유 부탁드립니다\n게시글로 남겨주세요!',
        ),
        PostCard(
          nickname: '롱기스트',
          date: '25.04.10 12:02',
          title: '이다현 보다 오래살기 크루에 오신 것을 환영합니다',
          content: '아무리 일찍 죽어도\n이다현 보다는 늦게 죽어봅시다\n파이팅!',
        ),
        PostCard(
          nickname: '공지사항',
          date: '25.04.10 12:02',
          title: '여기는 이다현보다 오래살기 크루입니다',
          content: '저속 노화 위주의 식사와 규칙적인 생활을 통해 삶을 재정비하고 이다현보다 오래 살기 위해 노력합니다',
        ),
      ],
    );
  }
}

// 탭바를 고정시키기 위한 Delegate
class _SliverAppBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar _tabBar;

  _SliverAppBarDelegate(this._tabBar);

  @override
  double get minExtent => _tabBar.preferredSize.height;

  @override
  double get maxExtent => _tabBar.preferredSize.height;

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: background,
      child: _tabBar,
    );
  }

  @override
  bool shouldRebuild(_SliverAppBarDelegate oldDelegate) {
    return false;
  }
}

// 게시글 카드 위젯
class PostCard extends StatelessWidget {
  final String nickname;
  final String date;
  final String title;
  final String content;
  const PostCard({
    super.key,
    required this.nickname,
    required this.date,
    required this.title,
    required this.content,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: boxBackgroundColor,
      margin: const EdgeInsets.symmetric(horizontal: 0, vertical: 4),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const CircleAvatar(
                  radius: 18,
                  foregroundImage:
                      Svg('assets/img/account_circle.svg', color: Colors.white),
                ),
                const SizedBox(width: 8),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      nickname,
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 15),
                    ),
                    Text(
                      date,
                      style:
                          const TextStyle(color: Colors.white54, fontSize: 12),
                    ),
                  ],
                ),
                const Spacer(),
                const Icon(Icons.more_vert, color: Colors.white60, size: 20),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              title,
              style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 20),
            ),
            const SizedBox(height: 3),
            Text(
              content,
              style: const TextStyle(
                  color: Colors.white70,
                  fontWeight: FontWeight.w400,
                  fontSize: 15),
            ),
            const SizedBox(height: 14),
            const Row(
              children: [
                Icon(TabBarIcon.heart, color: Colors.white, size: 21),
                SizedBox(width: 14),
                Icon(TabBarIcon.comment, color: Colors.white, size: 21),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
