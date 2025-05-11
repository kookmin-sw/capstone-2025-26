from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from user_manager.models import User 
from retrospect.models import Challenge, Retrospect, Plan, RetrospectOwnerType, RetrospectVisibility, Kpi, KpiResult, KpiDataType, ChallengeOwnerType
from django.test import TestCase
from ai_manager.services.kpi_score_generator import score_kpis_from_retrospect, extract_meaning_units, match_meaning_units_to_kpi, score_matched_units, generate_feedback
from unittest.mock import patch

class ChallengeAPITest(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성 및 로그인
        self.user = User(email="test999@example.com", username="testuser")
        self.user.set_password("1234")
        self.user.save()
        login_successful = self.client.login(email="test999@example.com", password="1234")
        print("login_successful:", login_successful)
        self.client.force_authenticate(user=self.user)
        
        # 챌린지 생성에 사용할 기본 데이터
        self.challenge_data = {
            "challenge_name": "Test Challenge",
            "description": "Test Challenge Description",
            "deadline": (timezone.now() + timedelta(days=10)).isoformat(),
            "owner_type": "USER",
            "status": "LIVE"
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
        self.user = User(email="test999@example.com", username="testuser")
        self.user.set_password("1234")
        self.user.save()
        login_successful = self.client.login(email="test999@example.com", password="1234")
        print("login_successful:", login_successful)
        self.client.force_authenticate(user=self.user)

        # 회고 생성을 위한 챌린지 생성 (회고는 챌린지와 연결되어야 함)
        self.challenge = Challenge.objects.create(
            challenge_name="Retrospect Test Challenge",
            description="Test Challenge Description",
            deadline=timezone.now() + timedelta(days=10),
            owner_type="USER",
            status="LIVE",
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
        url = reverse("generate-plan")
        data = {
            "challenge_id": self.challenge.id,
            "retrospect_id": retrospect.id
        }
        response = self.client.post(url, data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("plans", response.data)
        self.assertIsInstance(response.data["plans"], dict)
        self.assertTrue(len(response.data["plans"]) > 0)
        print("✅ 회고 기반 Plan 생성 테스트 통과")

class KpiScoringTestCase(TestCase):
    def test_score_retrospect(self):
        # 테스트용 사용자 생성
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 테스트용 챌린지 생성
        challenge = Challenge.objects.create(
            user=user,
            challenge_name='테스트 챌린지',
            description='테스트용 챌린지입니다',
            deadline=timezone.now() + timedelta(days=7),
            owner_type=ChallengeOwnerType.USER
        )
        
        # 테스트용 KPI 생성
        kpi = Kpi.objects.create(
            challenge=challenge,
            user=user,
            name='테스트 KPI',
            definition='테스트용 KPI입니다',
            measurement_unit='시간',
            data_type=KpiDataType.INTEGER
        )
        
        # 테스트용 회고 생성
        retrospect = Retrospect.objects.create(
            user=user,
            challenge=challenge,
            content='오늘 3시간 공부했고 집중도가 좋았습니다.',
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )
        
        # KPI 스코어링 실행
        results = score_kpis_from_retrospect(retrospect)
        

        # 결과 검증
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].kpi, kpi)
        self.assertTrue(0 <= results[0].score <= 1)

class KpiAPITest(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성 및 로그인
        self.user = User(email="test999@example.com", username="testuser")
        self.user.set_password("1234")
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # 테스트용 챌린지 생성
        self.challenge = Challenge.objects.create(
            user=self.user,
            challenge_name="Test Challenge",
            description="Test Challenge Description",
            deadline=timezone.now() + timedelta(days=10),
            owner_type=ChallengeOwnerType.USER,
            status="LIVE"
        )
        
        # 테스트용 KPI 생성
        self.kpi = Kpi.objects.create(
            challenge=self.challenge,
            user=self.user,
            name="Test KPI",
            definition="Test KPI definition",
            measurement_unit="시간",
            data_type=KpiDataType.FLOAT
        )
    
    def test_create_kpi(self):
        """
        KPI 생성 API 테스트
        """
        print("\n=== 테스트: KPI 생성 ===")
        data = {
            "challenge": self.challenge.id,
            "user": self.user.id,  # user 필드 추가
            "name": "New KPI",
            "definition": "New KPI definition",
            "measurement_unit": "회",
            "data_type": KpiDataType.INTEGER
        }
        url = reverse("kpi-list")
        response = self.client.post(url, data, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New KPI")
        print("✅ KPI 생성 테스트 통과")
    
    
    def test_get_kpi_results(self):
        """
        KPI 결과 조회 API 테스트
        """
        print("\n=== 테스트: KPI 결과 조회 ===")
        # 테스트용 회고 생성
        retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="Test retrospect content",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )
        
        # KPI 결과 생성
        KpiResult.objects.create(
            user=self.user,
            challenge=self.challenge,
            kpi=self.kpi,
            retrospect=retrospect,
            score=0.8,
            comment="Test comment"
        )
        
        url = reverse("kpi-result-list")
        response = self.client.get(url, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["score"], 0.8)
        print("✅ KPI 결과 조회 테스트 통과")
    
    def test_get_kpi_results_by_challenge(self):
        """
        챌린지별 KPI 결과 조회 API 테스트
        """
        print("\n=== 테스트: 챌린지별 KPI 결과 조회 ===")
        # 테스트용 회고 생성
        retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="Test retrospect content",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )
        
        # KPI 결과 생성
        KpiResult.objects.create(
            user=self.user,
            challenge=self.challenge,
            kpi=self.kpi,
            retrospect=retrospect,
            score=0.8,
            comment="Test comment"
        )
        
        url = reverse("kpi-result-by-challenge")
        response = self.client.get(url, {"challenge_id": self.challenge.id}, format="json")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["score"], 0.8)
        print("✅ 챌린지별 KPI 결과 조회 테스트 통과")

class KpiScoreGeneratorTest(TestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email="test999@example.com",
            password="1234",
            username="testuser"
        )
        
        # 테스트용 챌린지 생성
        self.challenge = Challenge.objects.create(
            user=self.user,
            challenge_name="Test Challenge",
            deadline=timezone.now() + timedelta(days=10),
            owner_type=ChallengeOwnerType.USER,
            status="LIVE"
        )
        
        # 테스트용 KPI 생성
        self.kpi = Kpi.objects.create(
            challenge=self.challenge,
            user=self.user,
            name="공부 시간",
            definition="하루 공부 시간",
            measurement_unit="시간",
            data_type=KpiDataType.FLOAT
        )
        
        # 테스트용 회고 생성
        self.retrospect = Retrospect.objects.create(
            user=self.user,
            challenge=self.challenge,
            content="오늘 3시간 공부했고 집중도가 좋았습니다. 내일은 4시간 목표로 하겠습니다.",
            visibility=RetrospectVisibility.PRIVATE,
            owner_type=RetrospectOwnerType.USER
        )
    
    def test_extract_meaning_units(self):
        """
        의미 단위 추출 테스트
        """
        print("\n=== 테스트: 의미 단위 추출 ===")
        text = "오늘 3시간 공부했고 집중도가 좋았습니다."
        units = extract_meaning_units(text)
        print(f"추출된 의미 단위: {units}")
        
        # 결과 검증
        self.assertIsInstance(units, list)
        self.assertTrue(any(unit["category"] == "행동" for unit in units))
        self.assertTrue(any(unit["keyword"] == "공부" for unit in units))
        self.assertTrue(any(unit["value"] == "3시간" for unit in units))
        print("✅ 의미 단위 추출 테스트 통과")
    
    def test_match_meaning_units_to_kpi(self):
        """
        KPI와 의미 단위 매핑 테스트
        """
        print("\n=== 테스트: KPI와 의미 단위 매핑 ===")
        units = [
            {"category": "행동", "keyword": "공부", "value": "3시간"},
            {"category": "성과", "keyword": "집중도", "value": "좋음"}
        ]
        matched_units = match_meaning_units_to_kpi(self.kpi, units)
        print(f"매핑된 의미 단위: {matched_units}")
        
        # 결과 검증
        self.assertIsInstance(matched_units, list)
        self.assertTrue(any(unit["keyword"] == "공부" for unit in matched_units))
        print("✅ KPI와 의미 단위 매핑 테스트 통과")
    
    def test_score_matched_units(self):
        """
        매핑된 단위 점수 계산 테스트
        """
        print("\n=== 테스트: 매핑된 단위 점수 계산 ===")
        units = [
            {"category": "행동", "keyword": "공부", "value": "3시간"},
            {"category": "성과", "keyword": "집중도", "value": "좋음"}
        ]
        score = score_matched_units(units)
        print(f"계산된 점수: {score}")
        
        # 결과 검증
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 1)
        print("✅ 매핑된 단위 점수 계산 테스트 통과")
    
    def test_score_kpis_from_retrospect(self):
        """
        회고 기반 KPI 점수 생성 테스트
        """
        print("\n=== 테스트: 회고 기반 KPI 점수 생성 ===")
        results = score_kpis_from_retrospect(self.retrospect)
        print(f"생성된 KPI 결과: {results}")
        
        # 결과 검증
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].kpi, self.kpi)
        self.assertTrue(0 <= results[0].score <= 1)
        print("✅ 회고 기반 KPI 점수 생성 테스트 통과")
    
    def test_score_kpis_from_retrospect_with_multiple_kpis(self):
        """
        여러 KPI에 대한 점수 생성 테스트
        """
        print("\n=== 테스트: 여러 KPI 점수 생성 ===")
        # 추가 KPI 생성
        kpi2 = Kpi.objects.create(
            challenge=self.challenge,
            user=self.user,
            name="집중도",
            definition="공부 집중도",
            measurement_unit="점",
            data_type=KpiDataType.FLOAT
        )
        
        results = score_kpis_from_retrospect(self.retrospect)
        print(f"생성된 KPI 결과: {results}")
        
        # 결과 검증
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)  # 두 개의 KPI 결과가 생성되어야 함
        self.assertTrue(any(result.kpi == self.kpi for result in results))
        self.assertTrue(any(result.kpi == kpi2 for result in results))
        print("✅ 여러 KPI 점수 생성 테스트 통과")



class GenerateFeedbackTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="feedbacktest@example.com", password="1234", username="feedbackuser")
        self.challenge = Challenge.objects.create(
            user=self.user,
            challenge_name="Feedback KPI Challenge",
            deadline=timezone.now() + timedelta(days=5),
            owner_type=ChallengeOwnerType.USER,
            status="LIVE"
        )
        self.kpi = Kpi.objects.create(
            challenge=self.challenge,
            user=self.user,
            name="공부 시간",
            definition="하루 공부 시간 측정",
            measurement_unit="시간",
            data_type=KpiDataType.FLOAT
        )

    @patch("ai_manager.services.kpi_score_generator.LLMChain.invoke")
    def test_generate_feedback_high_score(self, mock_invoke):
        """
        높은 점수일 때 칭찬 위주의 피드백 테스트
        """
        mock_invoke.return_value = {"text": "정말 훌륭해요! 오늘 목표를 완벽하게 달성했어요."}

        units = [
            {"category": "행동", "keyword": "공부", "value": "5시간"},
        ]
        score = 1.0  # 높은 점수

        feedback = generate_feedback(self.kpi, units, score)
        print(f"생성된 피드백: {feedback}")

        self.assertIn("정말 훌륭해요", feedback)

    @patch("ai_manager.services.kpi_score_generator.LLMChain.invoke")
    def test_generate_feedback_low_score(self, mock_invoke):
        """
        낮은 점수일 때 개선 제안 포함 피드백 테스트
        """
        mock_invoke.return_value = {"text": "조금 더 노력하면 목표에 도달할 수 있어요. 내일은 더 집중해보세요."}

        units = [
            {"category": "행동", "keyword": "공부", "value": "1시간"},
        ]
        score = 0.2  # 낮은 점수

        feedback = generate_feedback(self.kpi, units, score)
        print(f"생성된 피드백: {feedback}")

        self.assertIn("노력", feedback)

    @patch("ai_manager.services.kpi_score_generator.LLMChain.invoke", side_effect=Exception("LLM Error"))
    def test_generate_feedback_on_llm_error(self, mock_invoke):
        """
        LLM 에러 발생 시 기본 피드백 반환 테스트
        """
        units = [
            {"category": "행동", "keyword": "공부", "value": "3시간"},
        ]
        score = 0.5

        feedback = generate_feedback(self.kpi, units, score)
        print(f"에러 시 피드백: {feedback}")

        self.assertEqual(feedback, "좋은 시도였어요! 다음에도 도전해보세요.")

