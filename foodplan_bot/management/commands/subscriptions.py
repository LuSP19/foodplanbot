import json
from datetime import date

from dateutil.relativedelta import relativedelta

from foodplan_bot.models import User


def add_subscription(user_data):
    user = User.objects.get(tg_id=user_data['tg_id'])
    subscriptions = user.subscriptions

    if subscriptions:
        subscription_num = int(max(subscriptions)) + 1
    else:
        subscriptions = dict()
        subscription_num = 1

    term = int(user_data['subscription_term'])
    end_date = date.today() + relativedelta(months=+term)
    formatted_end_date = end_date.strftime('%d.%m.%Y')

    subscriptions[subscription_num] = {
        'menu_type': user_data['menu_type'],
        'persons_number': user_data['persons_number'],
        'meals_number': user_data['meals_number'],
        'allergies': user_data['allergies'],
        'end_date': formatted_end_date,
    }

    user.subscriptions = subscriptions
    user.save()
