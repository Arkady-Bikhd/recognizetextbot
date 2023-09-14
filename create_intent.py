import argparse
import json

from os import environ
from dotenv import load_dotenv

from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_text):
    message_texts = [message_text]
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)        
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )
    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )
    print("Intent created: {}".format(response))


def get_intent_file():
    parser = argparse.ArgumentParser(
        description='Программа формирует интент для Dialogflow',               
    )
    parser.add_argument('-jf', '--json_file', default='questions.json', help='Путь к json-файлу')
    args = parser.parse_args()
    return args.json_file


def fetch_training_phrases(file_name):
    with open(file_name, "r") as phrases_file:
        training_phrases_json = phrases_file.read()
    return json.loads(training_phrases_json)


def main():
    load_dotenv()
    df_project_id = environ['GOOGLE_CLOUD_PROJECT']
    file_name = get_intent_file()
    training_phrases = fetch_training_phrases(file_name)
    for display_name, training_phrases_components in training_phrases.items():        
       create_intent(df_project_id, display_name, training_phrases_components['questions'], training_phrases_components['answer'])


if __name__ == '__main__':
    main()