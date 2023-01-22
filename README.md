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
- Егор
