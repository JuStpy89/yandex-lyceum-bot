# Telegram bot FLAG GUESSER

## Введение
FlagGuesser – это бот которые загадывает пользователю рандомный флаг, а пользователь должен угадать какой стране этот флаг принадлежит. Этот бот поможет вам выучить флаги разных стран. За каждый правильный ответ пользователь получает один балл, а за неправильный теряет один балл.

## Используемые технологии
* python-telegram-bot – библиотека для работы с telegram
* sqlite3 – стандартная библиотека для работы с базой данных
* requests – библиотека для отправки запросов к API

## Функционал
* /start – начать диалог с ботом
* /play – сыграть с ботом
* /points – узнать свое количество очков
* /help – посмотреть правила и основные команды

## Ближайшие доработки
* Изменение уже существующего режим (у пользователя появиться возможность воспользоваться подсказкой, теперь за правильный ответ без подсказки пользователь получит 2 балла, за неправильный ответ без подсказки потеряет 1 балл, за правильный ответ с подсказкой получит 1 балл и за неправильный ответ с подсказкой потеряет 2 балла)
* Функция /myaccount, она будет выводить статисктику пользователя (кол-во сыгранных матчей, винрейт и т.п)
* Добавление Leaderboard'a