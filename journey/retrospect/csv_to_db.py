"""
CSV 파일에서 회고 데이터를 읽어 Django Retrospect 테이블에 저장하는 스크립트
GTPAR (Goal, Try, Problem, Achievement) 형식으로 된 회고를 처리합니다.
"""
import os
import sys

# 1. 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
journey_root = os.path.abspath(os.path.join(current_dir, '..'))
project_root = os.path.abspath(os.path.join(journey_root, '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, journey_root)

# 2. Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()  # ⬅️ 반드시 import 전 실행해야 함

# 3. 이제 import 가능 (이후에 models, services 등)
from langchain_google_vertexai.chat_models import ChatVertexAI
from ai_manager.services.kpi_score_generator import score_kpis_from_retrospect
from langfuse.callback import CallbackHandler
from django.utils import timezone
from django.db import transaction
import datetime
import csv
from uuid import uuid4

# Langfuse 핸들러 초기화
langfuse_handler = None
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)
# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
    callbacks=[langfuse_handler] if langfuse_handler else None,
)



# 프로젝트 루트 디렉토리를 Python 경로에 추가


# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django 설정을 가져오기 전에 경로 설정이 필요
import django
django.setup()

# 모델 import (Django 설정 초기화 후에 import 해야 함)
from retrospect.models import Retrospect, Challenge, Template, RetrospectOwnerType, RetrospectVisibility
from user_manager.models import User

# CSV 파일이 있는 디렉토리 경로 설정
CSV_DIR = os.path.join(journey_root, 'retrospect', 'dummy_csv')

def get_or_create_template():
    """GTPAR 형식의 템플릿이 없으면 생성"""
    
    try:
        template = Template.objects.get(name='GTPAR')
        print(f"기존 GTPAR 템플릿을 사용합니다. (ID: {template.id})")
    except Template.DoesNotExist:
        steps = {
            "1": "Goal",
            "2": "Try",
            "3": "Problem",
            "4": "Achievement",
            "5": "Reflection",
        }
        
        template = Template.objects.create(
            name='GTPAR 회고',
            owner_type='COMMON',
            steps=steps,
            description='Goal, Try, Problem, Achievement, Reflection 형식의 회고 템플릿',
            hashtag=["회고", "GTPAR"]
        )
        print(f"새로운 GTPAR 템플릿을 생성했습니다. (ID: {template.id})")
    
    return template

def get_or_create_user(username, email=None):
    if not email:
        # UUID 일부를 붙여서 고유성 확보
        uid = str(uuid4())[:8]
        base_email = username.replace(' ', '_').lower()
        email = f"{base_email}_{uid}@example.com"

    try:
        user = User.objects.get(username=username)
        print(f"기존 사용자를 사용합니다: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password='password123'
        )
        print(f"새로운 사용자를 생성했습니다: {username}")

    return user

def get_or_create_challenge(challenge_name, user):
    """Challenge 이름으로 Challenge를 찾거나 생성"""
    try:
        challenge = Challenge.objects.get(challenge_name=challenge_name, user=user)
        print(f"기존 챌린지를 사용합니다: {challenge_name}")
    except Challenge.DoesNotExist:
        # 기본 마감일: 현재로부터 1달 후
        deadline = timezone.now() + datetime.timedelta(days=30)
        
        challenge = Challenge.objects.create(
            challenge_name=challenge_name,
            user=user,
            owner_type='USER',
            deadline=deadline,
            status='LIVE'
        )
        print(f"새로운 챌린지를 생성했습니다: {challenge_name}")
    
    return challenge

def parse_csv_file(file_path):
    """CSV 파일을 파싱하여 회고 데이터 추출"""
    user_name = os.path.basename(file_path).replace('.csv', '').split(' - ')[1]
    
    retrospects = []
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        # 첫 번째 행("회고록") 건너뛰기
        next(csvfile)
        
        # CSV 파일 읽기
        csv_data = csv.reader(csvfile)
        
        # 두 번째 행을 헤더로 설정하고 매핑
        headers = next(csv_data)
        # 한글 헤더를 영어 헤더로 매핑
        header_mapping = {
            '작성날짜': 'Written_date',
            '목표날짜': 'Goal_date',
            '목표': 'Goal',
            '시도한것': 'Try',
            '문제가 있던것': 'Problem',
            '성취한것': 'Achievement',
            '반성할것': 'Reflection',
            '일간/주간': 'Week/Month'
        }
        
        # 매핑된 헤더 생성
        mapped_headers = [header_mapping.get(h, h) for h in headers]
        
        # 나머지 데이터를 처리
        for row in csv_data:
            # 빈 행 건너뛰기
            if not any(row):
                continue
                
            # 데이터를 딕셔너리로 변환
            row_dict = {mapped_headers[i]: row[i] if i < len(row) else '' for i in range(len(mapped_headers))}
            
            # 필요한 필드 추출
            date_str = row_dict.get('Written_date', '')
            good = row_dict.get('Goal', '')
            try_item = row_dict.get('Try', '')
            problem = row_dict.get('Problem', '')  
            achievement = row_dict.get('Achievement', '')
            reflection = row_dict.get('Reflection', '')
            
            # 날짜 파싱 (형식에 맞게 수정 필요)
            date = datetime.date.today()  # 기본값으로 오늘 날짜 설정
            if date_str:
                # 다양한 날짜 형식 처리
                success = False
                for date_format in ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%Y년 %m월 %d일']:
                    try:
                        date = datetime.datetime.strptime(date_str, date_format).date()
                        success = True
                        break
                    except ValueError:
                        continue
                
                # 모든 형식이 실패하면 직접 연, 월, 일 추출 시도
                if not success:
                    try:
                        # "2025.04.07" 형식 처리
                        parts = date_str.split('.')
                        if len(parts) == 3:
                            year = int(parts[0])
                            month = int(parts[1])
                            day = int(parts[2])
                            date = datetime.date(year, month, day)
                            success = True
                    except (ValueError, IndexError):
                        print(f"날짜 형식을 파싱할 수 없습니다: {date_str}, 기본 날짜를 사용합니다.")
                
                if not success:
                    print(f"[경고] 날짜 형식을 파싱할 수 없습니다: '{date_str}', 기본 날짜({date})를 사용합니다.")
            
            content = {
                "Goal": good,
                "Try": try_item,
                "Problem": problem,
                "Achievement": achievement,
                "Reflection": reflection
            }
            
            retrospects.append({
                'content': content,
                'date': date,
            })
    
    return user_name, retrospects

@transaction.atomic
def create_retrospect_from_csv_data(user, challenge, template, title, content, created_date, llm):
    """CSV 데이터로부터 회고 생성 및 KPI 평가"""
    retrospect = Retrospect.objects.create(
        challenge=challenge,
        template=template,
        content=content,
        visibility=RetrospectVisibility.PUBLIC,
        owner_type=RetrospectOwnerType.USER,
        created_at=created_date,
        updated_at=created_date,
        user=user,
        crew=None,
    )
    results = score_kpis_from_retrospect(retrospect, llm)
    print(f"    → KPI {len(results)}개 평가 완료")
    return retrospect

def import_csv_files():
    """폴더 내의 모든 CSV 파일을 가져와 DB에 저장"""
    
    if not os.path.exists(CSV_DIR):
        print(f"CSV 디렉토리를 찾을 수 없습니다: {CSV_DIR}")
        return
    
    # GTPAR 템플릿 가져오기 또는 생성
    template = get_or_create_template()
    
    file_count = 0
    retrospect_count = 0
    
    for filename in os.listdir(CSV_DIR):
        if not filename.endswith('.csv'):
            continue
        
        file_path = os.path.join(CSV_DIR, filename)
        print(f"처리 중: {filename}")
        
        try:
            user_name, retrospects_data = parse_csv_file(file_path)
            user = get_or_create_user(user_name)
            
            # 사용자에게 기본 챌린지 생성
            challenge = get_or_create_challenge("회고 습관 만들기", user)
            
            for retro_data in retrospects_data:
                created_date = timezone.make_aware(datetime.datetime.combine(
                    retro_data['date'], datetime.time()
                ))
                
                # 회고 생성
                retrospect = create_retrospect_from_csv_data(
                    user=user,
                    challenge=challenge,
                    template=template,
                    title='', 
                    content=retro_data['content'],
                    created_date=created_date,
                    llm=llm  
                )
                
                retrospect_count += 1
                print(f"  회고를 생성했습니다: ({retro_data['date']})")
            
            file_count += 1
            
        except Exception as e:
            print(f"파일 처리 중 오류 발생: {filename}")
            print(f"오류 메시지: {str(e)}")
    
    print(f"\n{file_count}개의 CSV 파일에서 총 {retrospect_count}개의 회고를 가져왔습니다.")

if __name__ == "__main__":
    print("CSV 파일에서 회고 데이터를 가져오는 작업을 시작합니다...")
    import_csv_files()
    print("작업이 완료되었습니다.")