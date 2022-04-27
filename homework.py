import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from settings import RETRY_TIME, ENDPOINT, HOMEWORK_STATUSES

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


HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


def send_message(bot, message):
    """Отправка уведомления."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        logger.error('Сбой. Сообщение не отправлено')


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == HTTPStatus.OK:
            return response.json()
    except Exception:
        logger.error('Сбой. Запрос к API не выполнен.')
    raise AssertionError('API возвращает код, отличный от 200')


def check_response(response):
    """Проверка ответа API на корректность."""
    homework = response['homeworks']
    if not isinstance(response, dict):
        raise TypeError('Некорректный тип')
    if not response['homeworks']:
        raise TypeError(f'Отсутствуют данные в {response}')
    if not isinstance(homework, list):
        raise TypeError('Некорректный тип')
    if not homework:
        raise TypeError('Список пуст')
    logging.info('Статус обновлен')
    return homework


def parse_status(homework):
    """Извлечение из информации о конкретной домашней работе."""
    if not isinstance(homework, dict):
        raise TypeError('Некорректный тип ответа')
    if 'homework_name' and 'status' not in homework:
        raise KeyError('Отсутствуют искомые ключи')
    if homework['status'] not in HOMEWORK_STATUSES:
        raise KeyError('Недокументированный статус')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    check_tokens()
    while True:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            if not homework:
                logger.debug('Обновлений нет')
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
