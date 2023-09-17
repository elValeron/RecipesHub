from django.core.exceptions import ValidationError


def hex_validate(value):
    """Валидация формата ввода цвета."""
    valid_regex = (r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    if value == valid_regex:
        return value
    else:
        ValidationError('Введите данные в формате HEX')
