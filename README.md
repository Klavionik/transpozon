# Курсовая работа: интернет-магазин Transpozon

## Нетология, модуль "Django: создание функциональных веб-приложений", апрель 2020 г.

### Описание

Проект интернет-магазина Transpozon (все совпадения случайны!).

### Установка

`$ git clone https://github.com/Klavionik/transpozon.git`  
`$ cd transpozon`  
`$ pip install -r requirements.txt`  
`$ ./manage.py migrate`  
`$ ./manage.py loaddata fixtures.json`

### Использование

Запуск сервера: `$ ./manage.py runserver`

Доступны товары в категориях "Смартфоны" и "Обувь". Работает регистрация, логин, добавление товара в корзину, чекаут, администрирование. Аккаунт администратора: `admin@admin.ru`
