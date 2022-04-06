# FoodPlanBot
Бот для рекомендации блюд по подписке.

### Установка

python3 должен быть установлен в системе

Установите зависимости:

```
pip install -r requirements.txt
```
Также для запуска потребуется файл .env в каталоге **foodplan** содержащий токены телеграм-бота и платёжной системы.

Пример содержимого файла:

```
TG_BOT_TOKEN='1039612657:CDGAYatu3dkR9fH4SMZLE83WaJQpElO-BySa'
SB_TOKEN='401528713:TEST:2d1bf40a-2c3a-3147-4e21-17382badf371'
```
Создайте базу данных, запустив команду
```
python manage.py migrate
```

### Запуск
```
python manage.py foodplan_bot
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
