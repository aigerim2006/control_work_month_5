from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from time import sleep
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def generate_report(user_id):
    sleep(5)
    print(f"Report generated for user {user_id}")
    return "REPORT_READY"


@shared_task
def send_welcome_email(email):
    send_mail(
        "Добро пожаловать",
        "Вы успешно зарегистрировались!",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return "EMAIL_SENT"


@shared_task
def delete_old_products():
    print("Checking old products...")
    return "CRON_WORKED"

