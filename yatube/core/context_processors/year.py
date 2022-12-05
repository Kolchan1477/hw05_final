from datetime import datetime


def year(request):
    """Добавляем переменную с текущим годом"""
    return {
        'year': datetime.now().year,
    }
