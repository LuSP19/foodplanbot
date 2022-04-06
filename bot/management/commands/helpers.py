from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from telegram import (
    LabeledPrice,
    ReplyKeyboardRemove,
)

from bot.models import User


PRECHECKOUT, SUCCESS_PAYMENT = range(14,16)


def take_payment(update, context):
    price = context.user_data['cost']

    update.message.reply_text(
        'Формирую счёт...',
        reply_markup=ReplyKeyboardRemove(),
    )

    provider_token = settings.SB_TOKEN
    chat_id = update.message.chat_id
    title = 'Ваш заказ'
    description = f'Оплата заказа стоимостью {price} рублей'
    payload = 'Custom-Payload'
    currency = 'RUB'
    prices = [LabeledPrice('Стоимость', price * 100)]

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices
    )

    return PRECHECKOUT


def precheckout(update, _):
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message='Что-то пошло не так...')
    else:
        query.answer(ok=True)

    return SUCCESS_PAYMENT


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
        'allergie': user_data['allergie'],
        'end_date': formatted_end_date,
    }

    user.subscriptions = subscriptions
    user.save()
