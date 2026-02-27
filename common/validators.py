from rest_framework.exceptions import ValidationError

def validate_price(value):
    if value <= 0:
        raise ValidationError("Цена должна быть больше 0")