import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("practicum_token")
TELEGRAM_TOKEN = os.getenv("telegram_token")
TELEGRAM_CHAT_ID = os.getenv("telegram_chat_id")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[logging.FileHandler("my_log.txt"),
              logging.StreamHandler(sys.stdout),
              ],
)
logger = logging.getLogger(__name__)


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка уведомления."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.OK:
        return response.json()
    else:
        raise AssertionError


def check_response(response):
    """Проверка ответа API на корректность."""
    if not response['homeworks']:
        error = f'Отсутствуют данные в {response}'
        raise TypeError(error)
    homework = response['homeworks']
    if not homework:
        error = 'Список пуст'
        raise TypeError(error)
    if not isinstance(homework, list):
        error = 'Некорректный тип'
        raise TypeError(error)
    if not isinstance(response, dict):
        error = 'Некорректный тип'
        raise TypeError(error)
    logging.info('Статус обновлен')
    return homework


def parse_status(homework):
    """Извлечение из информации о конкретной домашней работе."""
    if not isinstance(homework, dict):
        error = 'Некорректный тип ответа'
        raise TypeError(error)
    if 'homework_name' and 'status' not in homework:
        error = 'Отсутствуют искомые ключи'
        raise KeyError(error)
    if homework['status'] not in HOMEWORK_STATUSES:
        error = 'Недокументированный статус'
        raise KeyError(error)
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        return 'Error'
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    status = True
    for token in tokens.values():
        if token is None:
            status = False
    logging.critical(f'Отсутствует {token}')
    return status


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    check_tokens()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            if not homework:
                logger.debug('Обновлений нет')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
