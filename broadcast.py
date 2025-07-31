from flask import Blueprint, request, redirect, url_for
from models import db, FacebookPage
import requests

broadcast_bp = Blueprint('broadcast', __name__)

@broadcast_bp.route("/update-reply/<int:page_id>", methods=["POST"])
def update_reply(page_id):
    reply_text = request.form.get("reply_text")
    page = FacebookPage.query.get(page_id)
    if page:
        page.reply_text = reply_text
        db.session.commit()
    return redirect(url_for("dashboard"))

@broadcast_bp.route("/broadcast/<int:page_id>", methods=["POST"])
def broadcast_message(page_id):
    message = request.form.get("broadcast_text")
    page = FacebookPage.query.get(page_id)
    if not page:
        return "Page not found", 404

    url = f"https://graph.facebook.com/v19.0/{page.page_id}/conversations?access_token={page.access_token}"
    conversations = requests.get(url).json().get("data", [])

    for convo in conversations:
        thread_id = convo["id"]
        send_url = f"https://graph.facebook.com/v19.0/{thread_id}/messages"
        payload = {
            "message": {"text": message},
            "access_token": page.access_token
        }
        requests.post(send_url, json=payload)

    return redirect(url_for("dashboard"))