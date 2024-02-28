'''Отдельные функции, используемые для получения'''
from typing import Optional


def get_id(callback_data: str, separator: str = '_') -> Optional[int]:
    try:
        return int(callback_data.split(separator)[-1])
    except ValueError:
        return None
