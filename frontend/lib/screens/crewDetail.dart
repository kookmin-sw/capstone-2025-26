import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CrewDetail extends StatefulWidget {
  const CrewDetail({super.key});

  @override
  State<CrewDetail> createState() => _CrewDetailState();
}

class _CrewDetailState extends State<CrewDetail>
    with SingleTickerProviderStateMixin {
  TabController? _tabController;
  ScrollController? _scrollController;
  final double _expandedHeight = 240.h + 178.h;
  int _selectIndex = 0;
  bool _isCollapsed = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController!.addListener(() => setState(() {
          _selectIndex = _tabController!.index;
        }));

    _scrollController = ScrollController();
  }

  @override
  void dispose() {
    _tabController!.dispose();
    _scrollController!.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    var crewid = ModalRoute.of(context)!.settings.arguments;

    return Scaffold(
      backgroundColor: background,
      body: NestedScrollView(
        controller: _scrollController,
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverAppBar(
              toolbarHeight: 84.h,
              primary: false,
              leadingWidth: 52,
              leading: GestureDetector(
                onTap: () {
                  Navigator.pop(context);
                },
                child: Container(
                    margin: const EdgeInsets.only(top: 45),
                    child: const Icon(
                      Icons.arrow_back,
                      size: 18,
                    )),
              ),
              expandedHeight: _expandedHeight,
              pinned: true,
              floating: false,
              backgroundColor: _isCollapsed ? background : Colors.transparent,
              scrolledUnderElevation: 0, // 스크롤시 appbar 색상 변경 안되게
              iconTheme: const IconThemeData(color: Colors.white),
              title: null,
              flexibleSpace: LayoutBuilder(
                builder: (context, constraints) {
                  final double currentHeight = constraints.biggest.height;
                  final double statusBar = MediaQuery.of(context).padding.top;
                  final bool isCollapsed =
                      currentHeight <= kToolbarHeight + statusBar + 5;

                  if (_isCollapsed != isCollapsed) {
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      if (mounted) setState(() => _isCollapsed = isCollapsed);
                    });
                  }

                  double t = 1.0 -
                      ((currentHeight - kToolbarHeight - statusBar) /
                          (_expandedHeight - kToolbarHeight - statusBar));
                  t = t.clamp(0.0, 1.0);

                  const double avatarStartSize = 70;
                  const double avatarEndSize = 32;
                  final double avatarSize =
                      avatarStartSize - (avatarStartSize - avatarEndSize) * t;

                  const double nameStartFont = 18;
                  const double nameEndFont = 16;
                  final double nameFont =
                      nameStartFont - (nameStartFont - nameEndFont) * t;

                  const double leftPaddingStart = 20;
                  const double leftPaddingEnd = 70;
                  final double leftPadding = leftPaddingStart +
                      (leftPaddingEnd - leftPaddingStart) * t;

                  final double topStart = _expandedHeight - (70 * 4);
                  final double topEnd =
                      statusBar + (kToolbarHeight - avatarEndSize) / 2;
                  final double top = topStart - (topStart - topEnd) * t;

                  return Stack(
                    fit: StackFit.expand,
                    children: [
                      // 1. 배경 이미지에 opacity 적용
                      Opacity(
                        opacity: 1 - t,
                        child: Image.network(
                          'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
                          fit: BoxFit.cover,
                        ),
                      ),
                      // 2. flexibleSpace의 크루 정보와 버튼 (함께 사라짐)
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: 0,
                        child: Opacity(
                          opacity: 1 - t,
                          child: Stack(
                            clipBehavior: Clip.none,
                            children: [
                              Container(
                                width: double.maxFinite,
                                height: 178.h,
                                margin: EdgeInsets.only(top: 31.h),
                                color: boxBackgroundColor,
                                padding: EdgeInsets.fromLTRB(21.w, 0, 21.w, 0),
                                child: Stack(children: [
                                  Positioned(
                                    right: -10.w,
                                    top: 18.h,
                                    child: const Icon(Icons.more_vert,
                                        color: Colors.white),
                                  ),
                                  Container(
                                    padding: EdgeInsets.only(top: 26.h),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            Container(
                                              child: Row(
                                                children: [
                                                  Text(
                                                    '저속 노화 따라가기',
                                                    style: TextStyle(
                                                        fontSize: 19.sp,
                                                        fontWeight:
                                                            FontWeight.w800,
                                                        color: Colors.white,
                                                        height: 1.5),
                                                  ),
                                                  SizedBox(width: 13.w),
                                                  const Icon(
                                                    Icons
                                                        .person_outline_outlined,
                                                    color: Color(0xFF898989),
                                                    size: 15,
                                                  ),
                                                  SizedBox(width: 1.w),
                                                  Text(
                                                    '12명',
                                                    style: TextStyle(
                                                        fontSize: 12.sp,
                                                        color: Colors.white70),
                                                  ),
                                                  const Spacer(),
                                                ],
                                              ),
                                            ),
                                            Container(
                                              padding:
                                                  EdgeInsets.only(top: 6.h),
                                              child: Text(
                                                '저속 노화 위주의 식사와 규칙적인 생활을 통해 삶을 재정비하고 이다현보다 오래 살기 위해 노력합니다',
                                                style: TextStyle(
                                                    fontSize: 14.sp,
                                                    fontWeight: FontWeight.w500,
                                                    color: fontColor,
                                                    height: 1.70.h),
                                                maxLines: 2,
                                                overflow: TextOverflow.clip,
                                              ),
                                            ),
                                            Container(
                                              margin:
                                                  EdgeInsets.only(top: 16.h),
                                              height: 41.h,
                                              width: double.maxFinite,
                                              child: ElevatedButton(
                                                style: ElevatedButton.styleFrom(
                                                  backgroundColor: c800,
                                                  shape: RoundedRectangleBorder(
                                                    borderRadius:
                                                        BorderRadius.circular(
                                                            10),
                                                  ),
                                                  padding:
                                                      const EdgeInsets.only(
                                                          top: 8, bottom: 8),
                                                ),
                                                onPressed: () {},
                                                child: Text('크루 가입하기',
                                                    style: TextStyle(
                                                        fontSize: 16.sp,
                                                        color: fontColor,
                                                        fontWeight:
                                                            FontWeight.w700,
                                                        height: 1.5.h)),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ]),
                              ),
                              // 아이콘만 따로 위로 올림
                              Positioned(
                                top: -18.h,
                                left: 21.w,
                                child: Opacity(
                                  opacity: 1 - t,
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(10),
                                    child: Container(
                                      width: 70.w,
                                      height: 70.h,
                                      color: Colors.white,
                                      child: Image.network(
                                        'https://your-crew-icon-url.com/icon.png',
                                        fit: BoxFit.cover,
                                        errorBuilder:
                                            (context, error, stackTrace) =>
                                                const Icon(Icons.group,
                                                    size: 40,
                                                    color: Colors.grey),
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      // 3. AppBar로 이동하는 크루 아이콘+이름
                      Positioned(
                        left: leftPadding,
                        top: top,
                        child: Opacity(
                          opacity: t,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              ClipRRect(
                                borderRadius: BorderRadius.circular(10),
                                child: Container(
                                  width: avatarSize,
                                  height: avatarSize,
                                  color: Colors.white,
                                  child: Image.network(
                                    'https://your-crew-icon-url.com/icon.png',
                                    fit: BoxFit.cover,
                                    errorBuilder:
                                        (context, error, stackTrace) =>
                                            const Icon(Icons.group,
                                                size: 24, color: Colors.grey),
                                  ),
                                ),
                              ),
                              SizedBox(width: 8.w),
                              Text(
                                '저속 노화 따라가기',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: nameFont.sp,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
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
                  labelPadding: const EdgeInsets.only(left: 5, right: 5),
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
        width: 101.w,
        decoration: ShapeDecoration(
          color: selected ? c900 : boxBackgroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        child: Container(
          padding: const EdgeInsets.fromLTRB(23, 9, 23, 9),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: 15.sp, fontWeight: FontWeight.w500, color: fontColor),
          ),
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
  double get minExtent => _tabBar.preferredSize.height + 9;

  @override
  double get maxExtent => _tabBar.preferredSize.height + 9;

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      margin: const EdgeInsets.only(left: 16),
      padding: const EdgeInsets.fromLTRB(0, 5, 0, 4), // 여기서 공간 확보
      color: background,
      child: SizedBox(
        height: _tabBar.preferredSize.height,
        child: _tabBar,
      ),
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
    return Container(
      color: boxBackgroundColor,
      margin: EdgeInsets.only(bottom: 10.h),
      child: Padding(
        padding: EdgeInsets.fromLTRB(21.w, 16.h, 13.w, 11.h),
        // padding: EdgeInsets.symmetric(horizontal: 21.w, vertical: 14.h),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20.r,
                  foregroundImage: const Svg('assets/img/account_circle.svg',
                      color: Colors.white),
                ),
                SizedBox(width: 12.w),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      nickname,
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 12.sp),
                    ),
                    Text(
                      date,
                      style: TextStyle(
                          color: const Color(0xFFC3C3C3), fontSize: 12.sp),
                    ),
                  ],
                ),
                const Spacer(),
                const Icon(Icons.more_vert, color: Color(0xFFD9D9D9), size: 20),
              ],
            ),
            SizedBox(height: 10.h),
            Text(
              title,
              style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 20.sp,
                  letterSpacing: 0.1.r),
            ),
            SizedBox(height: 5.h),
            Text(
              content,
              style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w400,
                  fontSize: 15.sp,
                  height: 1.5,
                  letterSpacing: 0.1.r),
            ),
            SizedBox(height: 15.h),
            Row(
              children: [
                SizedBox(
                  width: 1.w,
                ),
                Icon(TabBarIcon.heart, color: Colors.white, size: 16.sp),
                SizedBox(width: 19.w),
                Icon(TabBarIcon.comment, color: Colors.white, size: 19.sp),
              ],
            ),
            SizedBox(
              height: 10.h,
            )
          ],
        ),
      ),
    );
  }
}
