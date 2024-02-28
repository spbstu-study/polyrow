'''Инструменты для удобства работы с json файлом из папки data'''
import logging
import json
from typing import Any, Optional

from config import BOT_DATA_PATH


LOGGER = logging.getLogger()


def load_from_json() -> Optional[Any]:
    try:
        with open(BOT_DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        LOGGER.error('The json file was not found or a decoding error occurred.')
        return None
    

def write_in_json(data: dict) -> Optional[str]:
    try:
        with open(BOT_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except UnicodeEncodeError:
        LOGGER.error('Decode error when writing in json.')
        return 'Ошибка кодировки: не удалось записать даннные в json файл'
    except:
        LOGGER.error('Unknown error when writing in json.')
        return 'Неизвестная ошибка'
    
    return None

def get_recommendation(number_of_training_days: int) -> Optional[str]:
    loaded_recommendations: Optional[dict] =  load_from_json()

    if loaded_recommendations is None:
        LOGGER.info('Recommendations were not found.')
        return None

    try:
        recommendation = loaded_recommendations.get(str(number_of_training_days))
    except TypeError:
        LOGGER.error('Type error when try to get recommendation to certain number of training days.')
        return None
    
    return recommendation if type(recommendation) == str else None


def get_password() -> Optional[str]:
    loaded_data: Optional[dict] = load_from_json()

    if loaded_data is None:
        LOGGER.info('Failed to load information from a json file.')
        return None

    password = loaded_data.get('admin_password')
    
    return password if type(password) == str else None


def json_change_admin_password(new_password: str) -> Optional[str]:
    loaded_data: Optional[dict] =  load_from_json()

    if loaded_data is None:
        LOGGER.info('Failed to load information from a json file.')
        return 'Не удалось загрузить данные из json файла'

    loaded_data['admin_password'] = new_password

    error_text = write_in_json(loaded_data)
    
    return error_text
