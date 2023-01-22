# yatube_project
Социальная сеть блогеров
## Описание
### В этой социальной сети можно:
- Регистрировать личный блог.
- Общаться с аудиторией.
- Вести свой личный дневник в котором можно делиться впечатлениями и эмоциями!
- Подписываться на других пользователей.
- Оставлять комментарии под сообщениями.
### Технологии
- Python 3.7
- Django 2.2.19
- Unittest
- TDD
### Используемые зависимости
- Django==2.2.16
- mixer==7.1.2
- Pillow==8.3.1
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- requests==2.26.0
- six==1.16.0
- sorl-thumbnail==12.7.0
- Faker==12.0.1
- django-debug-toolbar==3.2.4
### Запуск проекта в dev-режиме

Переходим в папку с проектом:
```
cd hw05_final
```
Устанавливаем виртуальное окружение:
```
python -m venv venv
```
Активируем виртуальное окружение:
```
source venv/Scripts/activate
```
Для деактивации виртуального окружения выполним (после работы):
```
deactivate
```
Устанавливаем зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Применяем миграции:
```
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```
Создаем супер пользователя:
```
python yatube/manage.py createsuperuser
```
В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```
### Автор
- Дубихин Егор
