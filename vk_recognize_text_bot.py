import random
import logging
import telegram

from os import environ
from dotenv import load_dotenv

import vk_api as vk

from vk_api.longpoll import VkLongPoll, VkEventType
from recognize_text_api import detect_intent_texts
from logging_api import TelegramLogsHandler


logger = logging.getLogger('speech_bot')


def send_answer(event, vk_api, bot_answer):    
    vk_api.messages.send(
        user_id=event.user_id,
        message=bot_answer,
        random_id=random.randint(1,1000)
    )


def main():
    load_dotenv()
    vk_access_token = environ['VK_ACCESS_TOKEN']
    df_project_id = environ['GOOGLE_CLOUD_PROJECT']    
    vk_session = vk.VkApi(token=vk_access_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    tg_chat_id = environ['TG_CHAT_ID']
    notice_bot_token = environ['TG_NOTICE_BOT_TOKEN']
    notice_bot = telegram.Bot(notice_bot_token)
    logger.setLevel(logging.WARNING)       
    logger.addHandler(
        TelegramLogsHandler(
            tg_bot=notice_bot,
            chat_id=tg_chat_id,
        )
    ) 
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                bot_answer = detect_intent_texts(df_project_id, f'vk-{event.user_id}', event.text)
                if not bot_answer.query_result.intent.is_fallback:            
                    send_answer(event, vk_api, bot_answer.query_result.fulfillment_text)
                else:
                    logger.warning('Бот не знает ответ')
            except Exception as err:
                logger.error(err)


if __name__ == '__main__':
    main()
