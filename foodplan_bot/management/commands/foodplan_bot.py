from django.conf import settings
from django.core.management.base import BaseCommand
from foodplan_bot.models import Tg_user
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)


(
    REGISTER,
    CONFIRM_NAME,
    GET_NAME,
    GET_SURNAME,
    GET_PHONE,
    MAIN_MENU,
) = range(6)


def start(update, context):
    user_id = update.message.from_user.id

    if not Tg_user.objects.filter(tg_id=user_id):
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
                [['Мои подписки', 'Создать подписку']],
                resize_keyboard=True,
            )
        )
        return MAIN_MENU


def confirm_name(update, context):
    if context.user_data.get('name'):
        del context.user_data['name']
    if context.user_data.get('surname'):
        del context.user_data['surname']
    if context.user_data.get('phone'):
        del context.user_data['phone']
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


def phone(update, context):
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
    context.user_data['tg_id'] = update.message.from_user.id
    if not context.user_data['name']:
        context.user_data['name'] = 'noname'
    if not context.user_data['surname']:
        context.user_data['surname'] = 'nosurname'    
    Tg_user.objects.create(
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


def dummy(update, context):
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
                MessageHandler(Filters.regex('^Сохранить$'), phone),
                MessageHandler(Filters.regex('^Изменить$'), ask_name),
            ],
            GET_NAME: [
                MessageHandler(Filters.text, ask_surname),
            ],
            GET_SURNAME: [
                MessageHandler(Filters.text, phone),
            ],
            GET_PHONE: [
                MessageHandler(Filters.contact, complete_registration),
            ],
            MAIN_MENU: [
                MessageHandler(Filters.regex('^Создать подписку$'), dummy),
                MessageHandler(Filters.regex('^Мои подписки$'), dummy),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
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
