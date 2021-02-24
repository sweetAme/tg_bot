import telegram
import models
from telegram.ext import Updater, CommandHandler

token = ''
bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

chat_id = ''
my_id = ''
supported_chat_id = [chat_id, my_id]

# Decorator to prevent unauthorized access to bot commands
def authorized(func):
    def inner(*args, **kwargs):
        update, context = args
        if update.message.chat_id in supported_chat_id:
            func(*args, **kwargs)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Access denied')
        
    return inner

message = '''
“The Three Laws of Robotics:

1: A robot may not injure a human being or, through inaction, allow a human being to come to harm;

2: A robot must obey the orders given it by human beings except where such orders would conflict with the First Law;

3: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law;

The Zeroth Law: A robot may not harm humanity, or, by inaction, allow humanity to come to harm.”
'''

@authorized
def bot_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

@authorized
def grouplist(update, context):
    data = models.get_grouplist_bot()
    context.bot.send_message(chat_id=update.effective_chat.id, text=data)

@authorized
def add_group(update, context):
    arguments = context.args
    if len(arguments) > 0:
        try:
            models.add_to_supported(arguments)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Группа успешно добавлена.')
        except:       
            context.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка в базе данных.')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Не указана группа.')

@authorized
def remove_group(update, context):
    arguments = context.args
    try:
        query = models.remove_from_supported(arguments)
        if query > 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Группа успешно удалена.')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Группы с таким названием не найдено.')
    except:       
        context.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка в базе данных.')

help_handler = CommandHandler('help', bot_help)
dispatcher.add_handler(help_handler)

grouplist_handler = CommandHandler('grouplist', grouplist)
dispatcher.add_handler(grouplist_handler)

add_group_handler = CommandHandler('add_group', add_group)
dispatcher.add_handler(add_group_handler)

remove_group_handler = CommandHandler('remove_group', remove_group)
dispatcher.add_handler(remove_group_handler)

updater.start_polling()
