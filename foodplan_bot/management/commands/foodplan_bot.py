from textwrap import dedent

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import (
    LabeledPrice,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    PreCheckoutQueryHandler,
    Updater
)

from foodplan_bot.models import User
from .subscriptions import add_subscription

(
    REGISTER,
    CONFIRM_NAME,
    GET_NAME,
    GET_SURNAME,
    GET_PHONE,
    MAIN_MENU,
    GET_MENU_TYPE,
    GET_PERSONS_NUMBER,
    GET_MEALS_NUMBER,
    GET_ALLERGIE,
    GET_SUBSCRIPTION_TERM,
    GET_PROMOCODE,
    TAKE_PAYMENT,
    PRECHECKOUT,
    SUCCESS_PAYMENT,
    SUBSCRIPTIONS_MENU
) = range(16)


def start(update, context):
    user_id = update.message.from_user.id
    context.user_data['tg_id'] = user_id

    if context.user_data.get('current_subscription'):
        del context.user_data['current_subscription']

    if not User.objects.filter(tg_id=user_id):
        update.message.reply_text(
            'Приветствую! Вы обратились к боту сервиса FoodPlan.\n'
            'Он может рекомендовать вам блюда. Для использования бота\n'
            'нужно зарегистрироваться',
            reply_markup=ReplyKeyboardMarkup(
                [['Регистрация']],
                resize_keyboard=True,
            )
        )
        return REGISTER
    else:
        update.message.reply_text(
            'Рад вас снова видеть',
            reply_markup=ReplyKeyboardMarkup(
                [['Создать подписку', 'Мои подписки']],
                resize_keyboard=True,
            )
        )
        return MAIN_MENU


def confirm_name(update, context):
    full_name = update.message.from_user.full_name
    update.message.reply_text(
        f'Сохранить имя и фамилию из профиля? ({full_name})',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[['Сохранить', 'Изменить']],
            resize_keyboard=True,
        ),
    )

    return CONFIRM_NAME


def ask_name(update, context):
    update.message.reply_text(
        'Введите имя',
        reply_markup=ReplyKeyboardRemove(),
    )

    return GET_NAME


def ask_surname(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        'Введите фамилию',
        reply_markup=ReplyKeyboardRemove(),
    )

    return GET_SURNAME


def ask_contact(update, context):
    if not context.user_data.get('name'):
        context.user_data['name'] = update.message.from_user.first_name
        context.user_data['surname'] = update.message.from_user.last_name
    else:
        context.user_data['surname'] = update.message.text

    phone_request_button = KeyboardButton('Передать контакт', request_contact=True)
    update.message.reply_text(
        'Передайте контакт для сохранения номера телефона',
        reply_markup=ReplyKeyboardMarkup(
            [[phone_request_button]],
            resize_keyboard=True,
        ),
    )

    return GET_PHONE


def complete_registration(update, context):
    context.user_data['phone'] = update.message.contact.phone_number
    if not context.user_data['name']:
        context.user_data['name'] = 'noname'
    if not context.user_data['surname']:
        context.user_data['surname'] = 'nosurname'    
    User.objects.create(
        tg_id=context.user_data['tg_id'],
        name=context.user_data['name'],
        surname=context.user_data['surname'],
        phone=context.user_data['phone'],
    )
    update.message.reply_text(
        'Регистрация завершена!\n'
        'Теперь вы можете создать подписку.',
        reply_markup=ReplyKeyboardMarkup(
            [['Создать подписку']],
            resize_keyboard=True,
        ),
    )

    return MAIN_MENU


def ask_menu_type(update, context):
    reply_keyboard = [
        ['Классическое', 'Низкоуглеводное'],
        ['Вегетарианское', 'Кето'],
    ]

    update.message.reply_text(
        'Выбирите тип меню',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )

    return GET_MENU_TYPE


def ask_persons_number(update, context):
    context.user_data['menu_type'] = update.message.text

    reply_keyboard = [
        ['1', '2', '3'],
        ['4', '5', '6'],
    ]

    update.message.reply_text(
        'Выбирите количество персон',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return GET_PERSONS_NUMBER


def ask_meals_number(update, context):
    context.user_data['persons_number'] = update.message.text

    reply_keyboard = [
        ['1', '2', '3'],
        ['4', '5', '6'],
    ]

    update.message.reply_text(
        'Выбирите количество приёмов пищи',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )

    return GET_MEALS_NUMBER


def ask_allergie(update, context):
    context.user_data['meals_number'] = update.message.text

    reply_keyboard = [
        ['Рыба и морепродукты', 'Мясо'],
        ['Зерновые', 'Продукты пчеловодства'],
        ['Орехи и бобовые', 'Молочные продукты'],
        ['Пропустить'],
    ]

    update.message.reply_text(
        'Укажите имеющуюся аллергию',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )

    return GET_ALLERGIE


def ask_subscription_term(update, context):
    if update.message.text == 'Пропустить':
        context.user_data['allergie'] = '—'
    else:
        context.user_data['allergie'] = update.message.text

    reply_keyboard = [
        ['1', '3', '6', '12'],
    ]

    update.message.reply_text(
        'Укажите срок подписки (мес.)',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )

    return GET_SUBSCRIPTION_TERM


def ask_promocode(update, context):
    context.user_data['subscription_term'] = update.message.text

    update.message.reply_text(
        'Введите промокод',
        reply_markup=ReplyKeyboardMarkup(
            [['Пропустить']],
            resize_keyboard=True,
        ),
    )

    return GET_PROMOCODE


def confirm_subscription(update, context):
    if update.message.text == 'devman':
        cost = int(context.user_data['subscription_term']) * 150 * 0.9
    else:
        cost = int(context.user_data['subscription_term']) * 150
    
    context.user_data['cost'] = cost
    
    update.message.reply_text(
        dedent(
            f'''
            Условия подписки:
            Тип меню: {context.user_data['menu_type']}
            Количество персон: {context.user_data['persons_number']}
            Количество приёмов пищи: {context.user_data['meals_number']}
            Аллергия: {context.user_data['allergie']}
            Срок подписки: {context.user_data['subscription_term']}\n
            Стоимость подписки составит {cost} руб.
            '''
        ),
        reply_markup=ReplyKeyboardMarkup(
            [['Оплатить']],
            resize_keyboard=True,
        ),
    )

    return TAKE_PAYMENT


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


def success_payment(update, context):
    add_subscription(context.user_data)

    update.message.reply_text(
        'Оплата поступила. Спасибо за оформление подписки!',
        reply_markup=ReplyKeyboardMarkup(
            [['Создать подписку', 'Мои подписки']],
            resize_keyboard=True,
        )
    )

    return MAIN_MENU


def show_subscriptions(update, context):

    user = User.objects.get(tg_id=context.user_data['tg_id'])

    if user.subscriptions:
        if not context.user_data.get('current_subscription'):
            context.user_data['current_subscription'] = int(max(user.subscriptions))

        subscription = user.subscriptions[str(context.user_data['current_subscription'])]

        if len(user.subscriptions) == 1:
            reply_keyboard = [['Показать блюдо'], ['Создать подписку']]
        elif context.user_data['current_subscription'] == 1:
            reply_keyboard = [['Показать блюдо', 'Далее'], ['Создать подписку']]
        elif context.user_data['current_subscription'] == len(user.subscriptions):
            reply_keyboard = [['Назад', 'Показать блюдо'], ['Создать подписку']]
        else:
            reply_keyboard = [['Назад', 'Показать блюдо', 'Далее'], ['Создать подписку']]

        update.message.reply_text(
            dedent(
                f'''
                Подписка #{context.user_data['current_subscription']}:
                Тип меню: {subscription['menu_type']}
                Количество персон: {subscription['persons_number']}
                Количество приёмов пищи: {subscription['meals_number']}
                Аллергия: {subscription['allergie']}
                Действует до: {subscription['end_date']}
                '''
            ),
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
            )
        )
        return SUBSCRIPTIONS_MENU
        
    else:
        update.message.reply_text(
            'У Вас пока нет подписок',
            reply_markup=ReplyKeyboardMarkup(
                [['Создать подписку', 'Мои подписки']],
                resize_keyboard=True,
            )
        )
        return MAIN_MENU


def previous_subscription(update, context):
    context.user_data['current_subscription'] -= 1
    return show_subscriptions(update, context)


def next_subscription(update, context):
    context.user_data['current_subscription'] += 1
    return show_subscriptions(update, context)


def stub(update, context):
    update.message.reply_text(
        'В разработке...',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()

    return ConversationHandler.END


def done(update, context):
    """End conversation."""

    user_data = context.user_data

    update.message.reply_text(
        'До свидания!',
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data.clear()

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(settings.TG_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTER: [
                MessageHandler(Filters.regex('^Регистрация$'), confirm_name),
            ],
            CONFIRM_NAME: [
                MessageHandler(Filters.regex('^Сохранить$'), ask_contact),
                MessageHandler(Filters.regex('^Изменить$'), ask_name),
            ],
            GET_NAME: [
                MessageHandler(Filters.text, ask_surname),
            ],
            GET_SURNAME: [
                MessageHandler(Filters.text, ask_contact),
            ],
            GET_PHONE: [
                MessageHandler(Filters.contact, complete_registration),
            ],
            MAIN_MENU: [
                MessageHandler(Filters.regex('^Создать подписку$'), ask_menu_type),
                MessageHandler(Filters.regex('^Мои подписки$'), show_subscriptions),
            ],
            GET_MENU_TYPE: [
                MessageHandler(Filters.regex('^Классическое$|^Низкоуглеводное$|^Вегетарианское$|^Кето$'), ask_persons_number),
            ],
            GET_PERSONS_NUMBER: [
                MessageHandler(Filters.regex('^1$|^2$|^3$|^4$|^5$|^6$'), ask_meals_number),
            ],
            GET_MEALS_NUMBER: [
                MessageHandler(Filters.regex('^1$|^2$|^3$|^4$|^5$|^6$'), ask_allergie),
            ],
            GET_ALLERGIE: [
                MessageHandler(Filters.regex('^Рыба и морепродукты$|^Мясо$|^Зерновые$|^Продукты пчеловодства$|^Орехи и бобовые$|^Молочные продукты$|^Пропустить$'), ask_subscription_term),
            ],
            GET_SUBSCRIPTION_TERM: [
                MessageHandler(Filters.regex('^1$|^3$|^6$|^12$'), ask_promocode),
            ],
            GET_PROMOCODE: [
                MessageHandler(Filters.text, confirm_subscription),
            ],
            TAKE_PAYMENT: [
                MessageHandler(Filters.regex('^Оплатить$'), take_payment),
            ],
            PRECHECKOUT: [
                PreCheckoutQueryHandler(precheckout),
            ],
            SUCCESS_PAYMENT: [
                MessageHandler(Filters.successful_payment, success_payment)
            ],
            SUBSCRIPTIONS_MENU: [
                MessageHandler(Filters.regex('^Создать подписку$'), ask_menu_type),
                MessageHandler(Filters.regex('^Показать блюдо$'), stub),
                MessageHandler(Filters.regex('^Назад$'), previous_subscription),
                MessageHandler(Filters.regex('^Далее$'), next_subscription),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
        per_user=True,
        per_chat=False,
        allow_reentry=True
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        main()
