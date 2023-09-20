import logging
import telegram

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from os import environ
from dotenv import load_dotenv
from google.cloud import dialogflow


logger = logging.getLogger('speech_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext) -> None:     
    context.user_data['df_project_id'] = environ['GOOGLE_CLOUD_PROJECT']
    context.user_data['session_id'] = environ['GOOGLE_CLOUD_PROJECT']
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    
    update.message.reply_text('Help!')


def send_answer(update: Update, context: CallbackContext) -> None:
    
    bot_answer = detect_intent_texts(context.user_data['df_project_id'], context.user_data['session_id'], text=update.message.text)
    update.message.reply_text(bot_answer)


def detect_intent_texts(project_id, session_id, text, bot='tg', language_code='ru-RU'):
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    ) 
    if response.query_result.intent.is_fallback and bot == 'vk':
        return None
    else:   
        return response.query_result.fulfillment_text
    
    
def send_error(update: Update, context: CallbackContext) -> None:
    logger.error('Случилась ошибка')


def main() -> None:
    load_dotenv()
    tg_bot_token = environ['TG_BOT_TOKEN'] 
    notice_bot_token = environ['TG_NOTICE_BOT_TOKEN']
    tg_chat_id = environ['TG_CHAT_ID']
    notice_bot = telegram.Bot(notice_bot_token)
    logger.setLevel(logging.WARNING)       
    logger.addHandler(
        TelegramLogsHandler(
            tg_bot=notice_bot,
            chat_id=tg_chat_id,
        )
    )          
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_answer))
    dispatcher.add_error_handler(send_error)
    updater.start_polling()    
    updater.idle()


if __name__ == '__main__':
    main()