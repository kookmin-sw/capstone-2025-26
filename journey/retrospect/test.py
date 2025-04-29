from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from user_manager.models import User 
from retrospect.models import Challenge, Retrospect, Plan, RetrospectOwnerType, RetrospectVisibility
from django.test import TestCase
from retrospect.models import Retrospect, KpiResult, KpiWeeklyResult
from kpi_score_generator import score_kpis_from_retrospect, generate_weekly_kpi_summary
from datetime import datetime, timedelta

class ChallengeAPITest(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성 및 로그인
        self.user = User(email="test999@example.com", nickname="testuser")
        self.user.set_password("1234")
        self.user.save()
        login_successful = self.client.login(email="test999@example.com", password="1234")
        print("login_successful:", login_successful)
        self.client.force_authenticate(user=self.user)
        
        # 챌린지 생성에 사용할 기본 데이터
        self.challenge_data = {
            "challenge_name": "Test Challenge",
            "deadline": (timezone.now() + timedelta(days=10)).isoformat(),
            "owner_type": "USER",
            "status": "LIVE",
            "kpi_metrics": {"example": "metric"}
        }
    
    def test_create_challenge(self):
        """
        챌린지 생성 API 테스트
        """
        print("\n=== 테스트: 챌린지 생성 ===")
        # URL은 여러분의 URL 설정에 따라 다를 수 있습니다.
        url = reverse("challenge-list")  # 예: /api/retrospect/challenges/
        response = self.client.post(url, self.challenge_data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["challenge_name"], "Test Challenge")
        print("✅ 챌린지 생성 테스트 통과")
    
    def test_retrieve_challenge(self):
        """
        챌린지 상세 조회 테스트
        """
        print("\n=== 테스트: 챌린지 조회 ===")
        challenge = Challenge.objects.create(user=self.user, **self.challenge_data)
        url = reverse("challenge-detail", args=[challenge.id])  # 예: /api/retrospect/challenges/<id>/
        response = self.client.get(url, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["challenge_name"], challenge.challenge_name)
        print("✅ 챌린지 조회 테스트 통과")
    
    def test_update_challenge(self):
        """
        챌린지 수정(PATCH) 테스트
        """
        print("\n=== 테스트: 챌린지 수정 ===")
        challenge = Challenge.objects.create(user=self.user, **self.challenge_data)
        url = reverse("challenge-detail", args=[challenge.id])
        
        # deadline이 문자열인 경우 처리
        if isinstance(challenge.deadline, str):
            deadline = challenge.deadline
        else:
            deadline = challenge.deadline.isoformat()
            
        update_data = {
            "challenge_name": "Updated Challenge Name",
            "deadline": deadline,  # 기존 값을 그대로 전달
            "owner_type": challenge.owner_type,    # 기존 값을 그대로 전달
            "status": challenge.status             # 기존 값을 그대로 전달
        }
        response = self.client.patch(url, update_data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DB의 값을 새로고침 후 확인
        challenge.refresh_from_db()
        self.assertEqual(challenge.challenge_name, "Updated Challenge Name")
        print("✅ 챌린지 수정 테스트 통과")
    
    def test_delete_challenge(self):
        """
        챌린지 삭제 테스트
        """
        print("\n=== 테스트: 챌린지 삭제 ===")
        challenge = Challenge.objects.create(user=self.user, **self.challenge_data)
        url = reverse("challenge-detail", args=[challenge.id])
        response = self.client.delete(url)
        print(f"응답 상태 코드: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Challenge.objects.filter(id=challenge.id).exists())
        print("✅ 챌린지 삭제 테스트 통과")

class RetrospectAPITest(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성 및 로그인
        self.user = User(email="test999@example.com", nickname="testuser")
        self.user.set_password("1234")
        self.user.save()
        login_successful = self.client.login(email="test999@example.com", password="1234")
        print("login_successful:", login_successful)
        self.client.force_authenticate(user=self.user)

        # 회고 생성을 위한 챌린지 생성 (회고는 챌린지와 연결되어야 함)
        self.challenge = Challenge.objects.create(
            challenge_name="Retrospect Test Challenge",
            deadline=(timezone.now() + timedelta(days=10)).isoformat(),
            owner_type="USER",
            status="LIVE",
            kpi_metrics={"example": "metric"},
            user=self.user
        )
    
    def test_create_retrospect(self):
        """
        회고 생성 API 테스트
        """
        print("\n=== 테스트: 회고 생성 ===")
        data = {
            "challenge": self.challenge.id,
            "content": "Test retrospect content",
            "visibility": "PUBLIC",  # 예: "PRIVATE", "CREW" 등 실제 모델 정의에 따라
            "owner_type": "USER",
            "initial_plan_description": "이 회고를 바탕으로 다음 챌린지 계획을 생성해주세요."  # 필수 필드 추가
        }
        url = reverse("retrospect-list")  # 예: /api/retrospect/retrospects/
        response = self.client.post(url, data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "Test retrospect content")
        print("✅ 회고 생성 테스트 통과")
    
    def test_retrieve_retrospect(self):
        """
        회고 상세 조회 테스트
        """
        print("\n=== 테스트: 회고 조회 ===")
        retrospect = Retrospect.objects.create(
            challenge=self.challenge,
            user=self.user,
            content="Retrieve retrospect content",
            visibility=RetrospectVisibility.PUBLIC,
            owner_type=RetrospectOwnerType.USER
        )
        url = reverse("retrospect-detail", args=[retrospect.id])  # 예: /api/retrospect/retrospects/<id>/
        response = self.client.get(url, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Retrieve retrospect content")
        print("✅ 회고 조회 테스트 통과")
    
    def test_update_retrospect(self):
        """
        회고 수정(PATCH) 테스트
        """
        print("\n=== 테스트: 회고 수정 ===")
        retrospect = Retrospect.objects.create(
            challenge=self.challenge,
            user=self.user,
            content="Initial content",
            visibility=RetrospectVisibility.PUBLIC,
            owner_type=RetrospectOwnerType.USER
        )
        url = reverse("retrospect-detail", args=[retrospect.id])
        update_data = {
            "content": "Updated retrospect content",
            "visibility": RetrospectVisibility.PRIVATE,  # 가시성 변경 테스트
            "owner_type": RetrospectOwnerType.USER  # 소유자 타입 유지
        }
        response = self.client.patch(url, update_data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrospect.refresh_from_db()
        self.assertEqual(retrospect.content, "Updated retrospect content")
        self.assertEqual(retrospect.visibility, RetrospectVisibility.PRIVATE)
        print("✅ 회고 수정 테스트 통과")
    
    def test_delete_retrospect(self):
        """
        회고 삭제 테스트
        """
        print("\n=== 테스트: 회고 삭제 ===")
        retrospect = Retrospect.objects.create(
            challenge=self.challenge,
            user=self.user,
            content="Retrospect to delete",
            visibility=RetrospectVisibility.PUBLIC,
            owner_type=RetrospectOwnerType.USER
        )
        url = reverse("retrospect-detail", args=[retrospect.id])
        response = self.client.delete(url)
        print(f"응답 상태 코드: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Retrospect.objects.filter(id=retrospect.id).exists())
        print("✅ 회고 삭제 테스트 통과")
    
    def test_generate_plan_from_retrospect(self):
        """
        회고 기반 Plan 생성 API 테스트
        """
        print("\n=== 테스트: 회고 기반 Plan 생성 ===")
        # 회고 생성
        retrospect = Retrospect.objects.create(
            challenge=self.challenge,
            user=self.user,
            content="Generate plan from this retrospect",
            visibility=RetrospectVisibility.PUBLIC,
            owner_type=RetrospectOwnerType.USER
        )
        
        # Plan 생성 API 호출
        url = reverse("generate-plan", kwargs={"challenge_id": self.challenge.id})
        data = {"retrospect_id": retrospect.id}
        response = self.client.post(url, data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("plan", response.data)
        self.assertIn("id", response.data["plan"])
        
        # 생성된 Plan 확인
        plan = Plan.objects.get(id=response.data["plan"]["id"])
        self.assertIn(retrospect, plan.retrospects.all())
        self.assertEqual(retrospect.challenge, self.challenge)
        print("✅ 회고 기반 Plan 생성 테스트 통과")



class KpiScoringTestCase(TestCase):
    def test_score_retrospect_and_weekly_summary(self):
        # 회고 ID 24 가져오기
        retrospect = Retrospect.objects.get(id=24)

        # ✅ 1. 단일 회고 KPI 스코어링
        results = score_kpis_from_retrospect(retrospect)
        for r in results:
            print(f"KPI: {r.kpi.name}, Score: {r.score}, Comment: {r.comment}")
        self.assertTrue(len(results) > 0)

        # ✅ 2. 주간 KPI 요약 생성
        weekly_results = generate_weekly_kpi_summary()
        for w in weekly_results:
            print(f"[{w.kpi.name}] 주간 평균: {w.average_score:.2f}, 회고 수: {w.retrospect_count}")
        self.assertTrue(len(weekly_results) > 0)

        # ✅ 3. 최근 결과 조회 검증 (쿼리만 실행)
        recent_results = KpiResult.objects.all().order_by('-created_at')[:5]
        print("최근 KpiResult:", recent_results)

        # ✅ 4. 이번 주 요약 결과 조회
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())  # 월요일
        summaries = KpiWeeklyResult.objects.filter(week_start_date=week_start)
        print("이번 주 요약:", summaries)

