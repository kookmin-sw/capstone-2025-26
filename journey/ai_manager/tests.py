from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from user_manager.models import User
from retrospect.models import Challenge, Retrospect, Kpi, KpiResult, RetrospectOwnerType, RetrospectVisibility, ChallengeOwnerType, KpiDataType

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
