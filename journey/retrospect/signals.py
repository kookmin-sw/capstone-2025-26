from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from retrospect.models import Retrospect, KpiResult
from ai_manager.services.kpi_score_generator import score_kpis_from_retrospect  
import os
from langchain_google_vertexai.chat_models import ChatVertexAI

# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)


@receiver(post_save, sender=Retrospect)
def generate_or_update_kpi_scores_on_retrospect_save(sender, instance, created, **kwargs):
    """
    회고가 생성되거나 수정될 때 KPI 점수 생성 및 업데이트
    """
    print(f"[Signal] 회고 저장 감지됨 → KPI 스코어 생성 시작 (회고 ID: {instance.id})")

    # 이미 존재하는 KPI 결과가 있으면 삭제 (재생성)
    existing_results = KpiResult.objects.filter(retrospect=instance)
    if existing_results.exists():
        print(f"[Signal] 기존 KPI 결과 {existing_results.count()}개 삭제 후 재생성")
        existing_results.delete()

    # KPI 점수 생성
    score_kpis_from_retrospect(instance, llm)
    print(f"[Signal] KPI 점수 생성 완료")

@receiver(pre_delete, sender=Retrospect)
def delete_kpi_results_on_retrospect_delete(sender, instance, **kwargs):
    """
    회고가 삭제될 때 KPI 결과도 삭제
    """
    print(f"[Signal] 회고 삭제 감지됨 → KPI 결과 삭제 시작 (회고 ID: {instance.id})")
    
    kpi_results = KpiResult.objects.filter(retrospect=instance)
    deleted_count, _ = kpi_results.delete()
    
    print(f"[Signal] KPI 결과 {deleted_count}개 삭제 완료")
    
    
# [회고 생성]
#   ↓
# Retrospect.save() → post_save → KPI 결과 생성

# [회고 수정]
#   ↓
# Retrospect.save() → post_save → 기존 KPI 결과 삭제 후 재생성

# [회고 삭제]
#   ↓
# Retrospect.delete() → pre_delete → KPI 결과 삭제
