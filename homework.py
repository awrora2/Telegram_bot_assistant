import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from settings import ENDPOINT, HOMEWORK_STATUSES, RETRY_TIME

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
    except Exception:
        logger.error('Сбой. Запрос к API не выполнен.')
    if response.status_code == HTTPStatus.OK:
        try:
            return response.json()
        except Exception:
            logger.error('Ошибка при преобразовании')
    else:
        raise AssertionError('API возвращает код, отличный от 200')


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Некорректный тип')
    if 'homeworks' not in response:
        raise TypeError(f'Отсутствуют данные в {response}')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Некорректный тип')
    logging.info('Статус обновлен')
    if not response['homeworks']:
        logging.info('Статус не изменился')
    return response['homeworks']


def parse_status(homework):
    """Извлечение из информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствуют искомый ключ homework_name')
    elif 'status' not in homework:
        raise KeyError('Отсутствуют искомый ключ status')
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
    if not check_tokens():
        sys.exit()
    while True:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homework = check_response(response)[0]
            message = parse_status(homework)
        except Exception as error:
            logger.error(f'Сбой. {error}')
        finally:
            time.sleep(RETRY_TIME)
            send_message(bot, message)


if __name__ == '__main__':
    main()
