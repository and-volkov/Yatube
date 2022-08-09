#  Проект Yatube

Проект yatube - платформа для блогов. Пользователи могут создавать и редактировать записи.
Комментировать посты других пользователей. 

## Технологии
- Python 3.7
- Django 2.2.28

## Установка

Скопируйте репозиторий.
```sh
git clone https://github.com/and-volkov/Yatube.git
```
Установите и активируйте виртуальное окружение.
```sh
cd api_yamdb
python -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
```
Установите зависимости, выполните миграции и запустите сервер.

```sh
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```
