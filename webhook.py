from flask import Blueprint, request
from models import FacebookPage
import requests, os

webhook = Blueprint('webhook', __name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456")

@webhook.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid token", 403

    data = request.get_json()
    for entry in data['entry']:
        for change in entry['changes']:
            if change['field'] == 'feed' and change['value'].get('item') == 'comment':
                page_id = entry['id']
                comment_id = change['value']['comment_id']
                user_id = change['value']['from']['id']

                page = FacebookPage.query.filter_by(page_id=page_id).first()
                if page:
                    reply_to_comment(comment_id, page.reply_text or "ขอบคุณสำหรับความคิดเห็นครับ ❤️", page.access_token)
                    send_message(user_id, "แอดมินได้รับข้อความแล้วครับ ❤️", page.access_token)

    return "OK", 200

def reply_to_comment(comment_id, message, token):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
    requests.post(url, data={"message": message, "access_token": token})

def send_message(user_id, message, token):
    url = f"https://graph.facebook.com/v19.0/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE",
        "access_token": token
    }
    requests.post(url, json=payload)