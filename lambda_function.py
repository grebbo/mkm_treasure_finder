import json
import requests
import os
import mkm_api_manager

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
URL = "https://api.telegram.org/bot{}/".format(TELEGRAM_TOKEN)


def send_message(text, chat_id):
    requests.get("{url}sendMessage?text={text}&chat_id={chat_id}".format(
        url=URL, text=text, chat_id=chat_id))


def is_valid_message(message):
    return True if message is not "/start" else False


def lambda_handler(event, context):
    input_text = json.loads(event['body'])
    chat_id = input_text['message']['chat']['id']
    message = input_text['message']['text']

    if is_valid_message(message):
        send_message("Looking for deals from {}...".format(message), chat_id)
        deals = mkm_api_manager.get_deals(message)

        for deal in deals:
            send_message(deal, chat_id)

        return {
            'statusCode': 200
        }
