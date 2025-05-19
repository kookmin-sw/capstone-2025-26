from django.test import TestCase

# Create your tests here.
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta, time
from unittest.mock import patch, MagicMock

from retrospect.models import (
    Challenge, Kpi, Retrospect, KpiResult, 
    RetrospectWeeklyAnalysis, Template,
    ChallengeOwnerType, RetrospectWeeklyAnalysisOwnerType, KpiDataType,
    ChallengeStatus, RetrospectOwnerType
)
from ai_manager.tasks import (
    finalize_weekly_challenge_analysis,
    trigger_chunked_finalize_weekly_analyses,
    get_week_start_end_dates
)

User = get_user_model()

@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class WeeklyAnalysisTasksTests(TestCase):
    """
    주간 분석 태스크에 대한 테스트 클래스
    Celery 태스크를 동기적으로 실행하도록 설정
    """
    def setUp(self):
        """
        테스트에 필요한 기본 데이터 설정
        - 테스트 사용자 생성
        - 테스트 챌린지 생성
        - 테스트 KPI 생성
        - 공통 템플릿 생성
        """
        self.user1 = User.objects.create_user(
            username='user1', 
            email='user1@example.com', 
            password='password'
        )
        
        # 테스트용 챌린지 생성
        self.challenge1 = Challenge.objects.create(
            user=self.user1,
            challenge_name='테스트 챌린지 1',
            description="주간 분석을 위한 테스트 챌린지입니다.",
            deadline=timezone.now() + timedelta(days=30),
            owner_type=ChallengeOwnerType.USER,
            status=ChallengeStatus.LIVE
        )
        
        # 테스트용 KPI 생성
        self.kpi1_c1 = Kpi.objects.create(
            challenge=self.challenge1,
            user=self.user1,
            name='코딩 시간',
            data_type=KpiDataType.INTEGER,
            definition="일일 코딩 시간을 측정합니다."
        )
        
        self.kpi2_c1 = Kpi.objects.create(
            challenge=self.challenge1,
            user=self.user1,
            name='구현한 기능 수',
            data_type=KpiDataType.INTEGER,
            definition="완료한 기능의 수를 측정합니다."
        )
        
        # 테스트용 날짜 설정 (2025년 5월 17일)
        self.today = date(2025, 5, 17)
    
    def test_get_week_start_end_dates(self):
        """주간 날짜 계산 함수 테스트"""
        week_start, week_end = get_week_start_end_dates(self.today)
        self.assertEqual(week_start, date(2025, 5, 12))  # 월요일
        self.assertEqual(week_end, date(2025, 5, 18))    # 일요일

    @patch('ai_manager.tasks.generate_weekly_llm_summary')
    def test_finalize_weekly_challenge_analysis_with_llm_summary(self, mock_generate_weekly_llm_summary):
        """
        주간 챌린지 분석 생성 및 LLM 요약 테스트
        - LLM 응답 모킹
        - 테스트용 회고 및 KPI 결과 생성
        - 주간 분석 실행 및 결과 검증
        """
        # LLM 응답 모킹
        mock_llm_output = {
            "summary": "이번 주 아주 잘 하셨습니다!",
            "comment": "주요 목표 달성 완료.",
            "assessment": "매우 뛰어남"
        }
        mock_generate_weekly_llm_summary.return_value = mock_llm_output

        # 테스트용 회고 생성
        retrospect1 = Retrospect.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            content={"step1": "테스트 내용 1"},
            owner_type=RetrospectOwnerType.USER
        )
        retrospect2 = Retrospect.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            content={"step1": "테스트 내용 2"},
            owner_type=RetrospectOwnerType.USER
        )
        retrospect3 = Retrospect.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            content={"step1": "테스트 내용 3"},
            owner_type=RetrospectOwnerType.USER
        )

        # 주간 날짜 범위 설정
        week_start, week_end = get_week_start_end_dates(self.today)
        
        # KPI 결과 생성 (이전 주 데이터)
        base_datetime = timezone.datetime.combine(self.today - timedelta(days=7), time(12, 0))
        base_datetime = timezone.make_aware(base_datetime)
        
        # KPI 결과 데이터 생성
        kpi_result1 = KpiResult.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            kpi=self.kpi1_c1,
            retrospect=retrospect1,
            score=0.8,
            llm_feedback="KPI 1에 대한 피드백 1",
            created_at=base_datetime
        )
        
        kpi_result2 = KpiResult.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            kpi=self.kpi1_c1,
            retrospect=retrospect2,
            score=0.6,
            llm_feedback="KPI 1에 대한 피드백 2",
            created_at=base_datetime + timedelta(days=3)
        )
        
        kpi_result3 = KpiResult.objects.create(
            user=self.user1,
            challenge=self.challenge1,
            kpi=self.kpi2_c1,
            retrospect=retrospect3,
            score=1.0,
            llm_feedback="KPI 2에 대한 피드백",
            created_at=base_datetime + timedelta(days=5)
        )

        # 주간 분석 실행
        finalize_weekly_challenge_analysis(
            self.challenge1.id, 
            week_start.isoformat(), 
            week_end.isoformat()
        )

        # 결과 검증
        analysis = RetrospectWeeklyAnalysis.objects.first()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.summary, mock_llm_output['summary'])
        self.assertEqual(analysis.comment, mock_llm_output['comment'])
        
        # 점수 검증
        expected_avg_score = (0.8 + 0.6 + 1.0) / 3
        self.assertAlmostEqual(analysis.avg_score, expected_avg_score, places=7)
        self.assertAlmostEqual(analysis.min_score, 0.6, places=7)
        self.assertAlmostEqual(analysis.max_score, 1.0, places=7)

    def test_finalize_weekly_challenge_analysis_without_kpi_results(self):
        """KPI 결과가 없는 경우 테스트"""
        week_start, week_end = get_week_start_end_dates(self.today)
        
        # KPI 결과 없이 주간 분석 실행
        finalize_weekly_challenge_analysis(
            self.challenge1.id, 
            week_start.isoformat(), 
            week_end.isoformat()
        )
        
        # 분석이 생성되었는지 확인
        analysis = RetrospectWeeklyAnalysis.objects.first()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.avg_score, 0.0)
        self.assertEqual(analysis.min_score, 0.0)
        self.assertEqual(analysis.max_score, 0.0)

    @patch('ai_manager.tasks.finalize_weekly_challenge_analysis.s')
    @patch('ai_manager.tasks.group')
    def test_trigger_chunked_finalize_weekly_analyses(self, mock_celery_group, mock_finalize_task_s):
        """
        여러 챌린지에 대한 주간 분석 일괄 처리 테스트
        - 여러 챌린지 생성
        - Celery 태스크 그룹 생성 및 실행 검증
        - 날짜 범위 계산 검증
        """
        # 추가 테스트 챌린지 생성
        Challenge.objects.create(
            user=self.user1,
            challenge_name='테스트 챌린지 2',
            description="두 번째 테스트 챌린지입니다.",
            deadline=timezone.now() + timedelta(days=30),
            owner_type=ChallengeOwnerType.USER,
            status=ChallengeStatus.LIVE
        )
        
        # Celery 태스크 모킹
        mock_signature = MagicMock()
        mock_finalize_task_s.return_value = mock_signature
        mock_group_instance = MagicMock()
        mock_celery_group.return_value = mock_group_instance

        # 일괄 처리 태스크 실행
        trigger_chunked_finalize_weekly_analyses()

        # 태스크 호출 검증
        self.assertEqual(mock_finalize_task_s.call_count, 2)
        mock_celery_group.assert_called_once()
        mock_group_instance.apply_async.assert_called_once()

        # Verify date range calculation - 날짜 범위 계산 검증
        prev_week_target_date = self.today - timedelta(days=7)
        expected_week_start, expected_week_end = get_week_start_end_dates(prev_week_target_date)
        
        first_call_args = mock_finalize_task_s.call_args_list[0][0]
        self.assertEqual(first_call_args[1], expected_week_start.isoformat())
        self.assertEqual(first_call_args[2], expected_week_end.isoformat()) 
    
    def test_finalize_weekly_challenge_analysis_with_crew_challenge(self):
        """크루 챌린지에 대한 주간 분석 테스트"""
        crew = Crew.objects.create(name="Test Crew")
        crew_challenge = Challenge.objects.create(
            crew=crew,
            challenge_name='Crew Challenge Test',
            description="A test crew challenge",
            deadline=timezone.now() + timedelta(days=30),
            owner_type=ChallengeOwnerType.CREW,
            status=ChallengeStatus.LIVE
        )
        
        week_start, week_end = get_week_start_end_dates(self.today)
        
        # 크루 챌린지에 대한 주간 분석 실행
        finalize_weekly_challenge_analysis(
            crew_challenge.id,
            week_start.isoformat(),
            week_end.isoformat()
        )
        
        # 분석이 올바르게 생성되었는지 확인
        analysis = RetrospectWeeklyAnalysis.objects.first()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.crew, crew)
        self.assertEqual(analysis.owner_type, RetrospectWeeklyAnalysisOwnerType.CREW)

class RetrospectKpiAutoScoringSignalTest(TestCase):
    
    def setUp(self):
        # 사용자 생성
        self.user = User.objects.create_user(email="signaltest@example.com", password="1234", username="signaluser")
        
        # 챌린지 생성
        self.challenge = Challenge.objects.create(
            user=self.user,
            challenge_name="Signal Test Challenge",
            deadline=timezone.now() + timedelta(days=5),
            owner_type=ChallengeOwnerType.USER,
            status="LIVE"
        )
        
        # KPI 생성
        self.kpi = Kpi.objects.create(
            challenge=self.challenge,
            user=self.user,
            name="공부 시간",
            definition="하루 공부 시간",
            measurement_unit="시간",
            data_type=KpiDataType.FLOAT
        )
    
    def test_create_retrospect_triggers_kpi_result(self):
        """
        회고 생성 시 KPIResult 자동 생성 테스트
        """
        retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="오늘 3시간 공부했다.",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )

        print("\n[회고 생성] Retrospect ID:", retrospect.id, ", content:", retrospect.content)

        kpi_results = KpiResult.objects.filter(retrospect=retrospect)

        print("[KPI 평가 결과 개수]", kpi_results.count())

        for result in kpi_results:
            print(f"[KPI 평가 생성됨] KPI: {result.kpi.name}, Score: {result.score}, Feedback: {result.comment}")

        self.assertEqual(kpi_results.count(), 1)
        self.assertEqual(kpi_results.first().kpi, self.kpi)
        self.assertTrue(0 <= kpi_results.first().score <= 1)

    def test_update_retrospect_triggers_kpi_result_update(self):
        """
        회고 수정 시 기존 KPIResult 삭제 후 재생성 테스트
        """
        retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="오늘 3시간 공부했다.",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )

        print("\n[회고 최초 생성] Retrospect ID:", retrospect.id, ", content:", retrospect.content)

        initial_results = KpiResult.objects.filter(retrospect=retrospect)
        print("[초기 KPI 평가 결과 개수]", initial_results.count())
        for result in initial_results:
            print(f"[초기 KPI 평가] KPI: {result.kpi.name}, Score: {result.score}, Feedback: {result.comment}")

        # 회고 내용 수정 (save 발생 → KPIResult 재생성)
        retrospect.content = "오늘 5시간 공부했다. 더 열심히 했다."
        retrospect.save()

        updated_results = KpiResult.objects.filter(retrospect=retrospect)
        print("\n[회고 수정 후] Retrospect ID:", retrospect.id, ", content:", retrospect.content)
        print("[수정 후 KPI 평가 결과 개수]", updated_results.count())

        for result in updated_results:
            print(f"[수정 후 KPI 평가] KPI: {result.kpi.name}, Score: {result.score}, Feedback: {result.comment}")

        self.assertEqual(updated_results.count(), 1)
        self.assertTrue(0 <= updated_results.first().score <= 1)

    def test_delete_retrospect_deletes_kpi_results(self):
        """
        회고 삭제 시 KPIResult 자동 삭제 테스트
        """
        retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="오늘 3시간 공부했다.",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )

        print("\n[회고 생성 (삭제 테스트용)] Retrospect ID:", retrospect.id, ", content:", retrospect.content)

        results_before_delete = KpiResult.objects.filter(retrospect=retrospect)
        print("[삭제 전 KPI 평가 결과 개수]", results_before_delete.count())

        retrospect_id = retrospect.id

        # 회고 삭제
        retrospect.delete()

        # 삭제 후 확인
        results_after_delete = KpiResult.objects.filter(retrospect_id=retrospect_id)
        print("[회고 삭제 후 KPI 평가 결과 개수]", results_after_delete.count())

        self.assertEqual(results_after_delete.count(), 0)