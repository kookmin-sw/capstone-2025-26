# Django 가 시작될 때 app이 구동되도록 하여 @shared_task 데코레이터를 사용할 수 있도록 합니다.

from .celery import app as celery_app

__all__ = ("celery_app",)