# Telegram_bot_assistant
Telegram-бот с определенной периодичностью обращается к API сервиса Практикум.Домашка и проверяет статус домашней работы студента Яндекс.Практикума. 

## Getting Started:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone

```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Запустить проект


## Prerequisites
```
flake8==3.9.2
flake8-docstrings==1.6.0
pytest==6.2.5
python-dotenv==0.19.0
python-telegram-bot==13.7
requests==2.26.0
```

### Examples:
Возможные статусы: домашняя работа на ревью или проверена. 
При обновлении статуса Telegram-бот анализирует ответ API сервиса Практикум.Домашка и отправляет такому пользователю соответствующее уведомление в Telegram. 
Также Telegram-бот логирует свою работу и сообщает пользователю о важных проблемах сообщением в Telegram. 
