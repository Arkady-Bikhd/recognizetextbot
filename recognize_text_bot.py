import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from os import environ
from dotenv import load_dotenv
from google.cloud import dialogflow


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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


def send_reply(update: Update, context: CallbackContext) -> None:
    
    bot_answer = detect_intent_texts(context.user_data['df_project_id'], context.user_data['session_id'], text=update.message.text)
    update.message.reply_text(bot_answer)


def detect_intent_texts(project_id, session_id, text, language_code='ru-RU'):
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )    
    return response.query_result.fulfillment_text


def main() -> None:
    load_dotenv()
    tg_bot_token = environ['TG_BOT_TOKEN']       
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_reply))
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()