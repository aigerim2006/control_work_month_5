from rest_framework.exceptions import ValidationError
from datetime import datetime, date

def validate_price(value):
    if value <= 0:
        raise ValidationError("Цена должна быть больше 0")
    
def validate_age_from_token(request):
    birthdate_str = request.auth.get("birthdate")
    if not birthdate_str:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    birthdate = datetime.fromisoformat(birthdate_str).date()
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")

