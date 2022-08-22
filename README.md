# Telegram_bot_assistant
Telegram-бот с определенной периодичностью обращается к API сервиса Практикум.Домашка и проверяет статус домашней работы студента Яндекс.Практикума. 

## Getting Started:

лонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/awrora2/hw05_final.git](https://github.com/awrora2/API_for_Yatube.git
cd yatube_api
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
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
cd yatube
python3 manage.py runserver
```

## Prerequisites
```
flake8==3.9.2
flake8-docstrings==1.6.0
pytest==6.2.5
python-dotenv==0.19.0
python-telegram-bot==13.7
requests==2.26.0
```


Возможные статусы: домашняя работа на ревью или проверена. 
При обновлении статуса Telegram-бот анализирует ответ API сервиса Практикум.Домашка и отправляет такому пользователю соответствующее уведомление в Telegram. 
Также Telegram-бот логирует свою работу и сообщает пользователю о важных проблемах сообщением в Telegram. 
