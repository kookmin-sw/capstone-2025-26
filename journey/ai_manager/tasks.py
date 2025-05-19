from celery import shared_task, group
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, date, time
import logging
from django.db.models import Avg, Count

from retrospect.models import (
    Challenge, RetrospectWeeklyAnalysis, RetrospectWeeklyAnalysisOwnerType, 
    Kpi, KpiResult, ChallengeStatus
)
from .services.weekly_analyzer import generate_weekly_llm_summary

logger = logging.getLogger(__name__)

def get_week_start_end_dates(today=None):
    """Returns the start (Monday) and end (Sunday) dates of the current week."""
    if today is None:
        today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    print(f"today : {today}, start_of_week:{start_of_week}, end_of_week:{end_of_week}")
    return start_of_week, end_of_week

@shared_task(name="ai_manager.finalize_weekly_challenge_analysis")
def finalize_weekly_challenge_analysis(challenge_id, week_start_str, week_end_str):
    """
    Finalizes weekly analysis for a single challenge using KpiResult data from RDBMS.
    """
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        week_start_date = date.fromisoformat(week_start_str)
        week_end_date = date.fromisoformat(week_end_str)

        # Determine owner and owner_type
        owner_user = None
        owner_crew = None
        owner_type_enum = None

        if challenge.owner_type == Challenge.ChallengeOwnerType.USER:
            owner_user = challenge.user
            owner_type_enum = RetrospectWeeklyAnalysisOwnerType.USER
        elif challenge.owner_type == Challenge.ChallengeOwnerType.CREW:
            owner_crew = challenge.crew
            owner_type_enum = RetrospectWeeklyAnalysisOwnerType.CREW
        else:
            logger.warning(f"Unknown challenge owner type for challenge {challenge_id}. Skipping.")
            return

        # Get KPI results for the week from RDBMS
        # Convert dates to datetime for proper comparison
        week_start_datetime = timezone.make_aware(timezone.datetime.combine(week_start_date, time.min))
        week_end_datetime = timezone.make_aware(timezone.datetime.combine(week_end_date, time.max))
        
        logger.info(f"Querying KPI results for challenge {challenge_id} between {week_start_datetime} and {week_end_datetime}")
        
        kpi_results = KpiResult.objects.filter(
            challenge=challenge,
            created_at__gte=week_start_datetime,
            created_at__lte=week_end_datetime
        )
        
        # Log the query results
        logger.info(f"Found {kpi_results.count()} KPI results")
        for result in kpi_results:
            logger.info(f"KPI Result: id={result.id}, score={result.score}, created_at={result.created_at}")

        # Calculate statistics
        scores = list(kpi_results.values_list('score', flat=True))
        logger.info(f"Calculated scores: {scores}")
        
        avg_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        logger.info(f"Calculated statistics: avg={avg_score}, min={min_score}, max={max_score}")

        # Get daily comment snippets
        daily_feedback_snippets = list(kpi_results.exclude(
            comment__isnull=True
        ).values_list('comment', flat=True))
        
        logger.info(f"Retrieved {len(daily_feedback_snippets)} daily comment snippets")
        if daily_feedback_snippets:
            logger.info("Sample of first comment snippet: %s", daily_feedback_snippets[0] if daily_feedback_snippets else "No snippets")

        # Generate Weekly Summary using LLM
        logger.info("Preparing to call generate_weekly_llm_summary")
        llm_generated_summary = generate_weekly_llm_summary(
            challenge, 
            [{"name": kpi.name, "avg_score": avg_score} for kpi in Kpi.objects.filter(challenge=challenge)],
            daily_feedback_snippets, 
            week_start_str, 
            week_end_str
        )
        logger.info("Received LLM generated summary")

        # Create or update RetrospectWeeklyAnalysis
        analysis_content = {
            'comment': llm_generated_summary.get('comment', ''),
            'summary': llm_generated_summary.get('summary', ''),
            'assessment': llm_generated_summary.get('assessment', ''),
            'avg_score': avg_score,
            'min_score': min_score,
            'max_score': max_score,
        }

        if owner_type_enum == RetrospectWeeklyAnalysisOwnerType.USER:
            analysis, created = RetrospectWeeklyAnalysis.objects.update_or_create(
                user=owner_user,
                challenge=challenge,
                owner_type=owner_type_enum,
                start_date=week_start_date,
                end_date=week_end_date,
                defaults=analysis_content
            )
        elif owner_type_enum == RetrospectWeeklyAnalysisOwnerType.CREW:
            analysis, created = RetrospectWeeklyAnalysis.objects.update_or_create(
                crew=owner_crew,
                challenge=challenge,
                owner_type=owner_type_enum,
                start_date=week_start_date,
                end_date=week_end_date,
                defaults=analysis_content
            )

        action = "Created" if created else "Updated"
        logger.info(f"{action} weekly analysis for challenge {challenge_id} for week {week_start_str} - {week_end_str}")

    except Challenge.DoesNotExist:
        logger.error(f"Challenge with ID {challenge_id} not found during finalization.")
    except Exception as e:
        logger.error(f"Error in finalize_weekly_challenge_analysis for challenge {challenge_id}: {e}", exc_info=True)

@shared_task(name="ai_manager.trigger_chunked_finalize_weekly_analyses")
def trigger_chunked_finalize_weekly_analyses():
    """
    Fetches all active challenge IDs and launches finalize_weekly_challenge_analysis for each.
    """
    today = date.today()
    target_date_for_week_calculation = today - timedelta(days=7)
    week_start, week_end = get_week_start_end_dates(target_date_for_week_calculation)
    week_start_str = week_start.isoformat()
    week_end_str = week_end.isoformat()

    challenge_ids = list(Challenge.objects.filter(status=ChallengeStatus.LIVE).values_list('id', flat=True))
    
    if not challenge_ids:
        logger.info("No active challenges found to finalize weekly analysis.")
        return
    
    # chunk_size는 현재 로직에서는 태스크 생성 루프를 구성하는 방식에만 영향을 미치고, 워커 할당 방식에는 직접적인 영향을 주지 않음.
    chunk_size = getattr(settings, 'WEEKLY_ANALYSIS_CHUNK_SIZE', 20)
    chunks = [challenge_ids[i:i + chunk_size] for i in range(0, len(challenge_ids), chunk_size)]

    finalize_tasks_group = group([
        finalize_weekly_challenge_analysis.s(challenge_id, week_start_str, week_end_str)
        for chunk in chunks for challenge_id in chunk
    ])
    
    if finalize_tasks_group.tasks:
        finalize_tasks_group.apply_async()
        logger.info(f"Triggered weekly analysis finalization for {len(challenge_ids)} challenges, week: {week_start_str} - {week_end_str}")
    else:
        logger.info(f"No tasks to dispatch for weekly analysis finalization for week: {week_start_str} - {week_end_str}")

@shared_task(name="ai_manager.send_daily_reminder")
def send_daily_reminder():
    """
    Placeholder for a daily reminder task.
    Implement actual reminder logic here (e.g., check for users who haven't done a retrospect today).
    """
    logger.info("Executing daily reminder task at 23:00.")

# Optional: Task for sending notifications after weekly analysis is complete
# @shared_task(name="retrospect.send_weekly_analysis_notification")
# def send_weekly_analysis_notification(results, week_start_str, week_end_str):
#     # 'results' would be the return values of the tasks in the chord header if used.
#     # Here, we don't have direct results from finalize_weekly_challenge_analysis in this setup.
#     # This task would typically query the database for users/crews with new weekly analyses.
#     logger.info(f"Weekly analysis for {week_start_str} - {week_end_str} finalized. Sending notifications...")
#     # Add notification logic here 