import random

from os import environ
from dotenv import load_dotenv

from google.cloud import dialogflow

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from recognize_text_bot import detect_intent_texts


def send_replay(event, vk_api, bot_answer):    
    vk_api.messages.send(
        user_id=event.user_id,
        message=bot_answer,
        random_id=random.randint(1,1000)
    )


def main():
    load_dotenv()
    vk_access_token = environ['VK_ACCESS_TOKEN']
    df_project_id = environ['GOOGLE_CLOUD_PROJECT']
    session_id = environ['VK_GROUP_ID']
    vk_session = vk.VkApi(token=vk_access_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            bot_answer = detect_intent_texts(df_project_id, session_id, event.text)            
            send_replay(event, vk_api, bot_answer)


if __name__ == '__main__':
    main()