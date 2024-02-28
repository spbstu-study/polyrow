import configparser
import os


read_config = configparser.ConfigParser()
read_config.read("token.ini")


# TOKEN
BOT_TOKEN = read_config['token']['token'].strip().replace(" ", "")

# PATHS
DATABASE_PATH = os.path.join(os.getcwd(), 'database', 'row.db')
FILENAME_FAQ = "data/faq.txt"
FILENAME_CALENDAR = "data/competition_calendar.txt"
BOT_DATA_PATH = os.path.join(os.getcwd(), 'data', 'bot_data.json')

# URLS
URL_FORMS = 'https://docs.google.com/forms/'

# OTHER SETTINGS
# Не забудь поменять рекомендации в data/bot_data.json, если меняешь min и max
MIN_NUMBER_OF_TRAINING_DAYS, MAX_NUMBER_OF_TRAINING_DAYS = 3, 6 

WORKOUT_TYPES_ALIASES_RUS: dict[str, str] = {
    'strength': 'Сила',
    'endurance': 'Выносливость',
    'speed': 'Скорость',
    'recovery': 'Восстановление'
}
