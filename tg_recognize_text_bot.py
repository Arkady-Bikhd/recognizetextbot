import logging

from functools import partial

import telegram

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from os import environ
from dotenv import load_dotenv
from recognize_text_api import TelegramLogsHandler, detect_intent_texts


logger = logging.getLogger('speech_bot')


def start(update: Update, context: CallbackContext) -> None: 
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def send_answer(update: Update, context: CallbackContext, df_project_id) -> None:
    bot_answer = detect_intent_texts(df_project_id, f'vk-{update.message.chat_id}', text=update.message.text)
    update.message.reply_text(bot_answer.query_result.fulfillment_text)
    
    
def send_error(update: Update, context: CallbackContext) -> None:
    logger.error('Случилась ошибка')


def main() -> None:
    load_dotenv()
    tg_bot_token = environ['TG_BOT_TOKEN'] 
    notice_bot_token = environ['TG_NOTICE_BOT_TOKEN']
    tg_chat_id = environ['TG_CHAT_ID']
    df_project_id = environ['GOOGLE_CLOUD_PROJECT']    
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
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, partial(send_answer, df_project_id=df_project_id)))
    dispatcher.add_error_handler(send_error)
    updater.start_polling()    
    updater.idle()


if __name__ == '__main__':
    main()