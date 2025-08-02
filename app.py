import os
import requests # <--- ย้าย import มาไว้ข้างบนสุด
from flask import Flask, render_template, request, url_for, redirect
from models import db, FacebookPage
from fb_login import fb_login
from broadcast import broadcast_bp

app = Flask(__name__)

# --- ส่วนของการตั้งค่าฐานข้อมูลและ SECRET_KEY (เหมือนเดิม) ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook_pages.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key')

db.init_app(app)

# --- ลงทะเบียน Blueprint อื่นๆ ---
app.register_blueprint(fb_login, url_prefix='/')
app.register_blueprint(broadcast_bp, url_prefix='/')

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    pages = FacebookPage.query.all()
    # เพิ่มโค้ดสำหรับปุ่มเชื่อมต่อในหน้า dashboard
    show_connect_button = not pages 
    return render_template('dashboard.html', pages=pages, show_connect_button=show_connect_button)

# =================================================================
#  โค้ด Webhook ที่สมบูรณ์
# =================================================================
def reply_to_comment(comment_id, message, token):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
    params = {"message": message, "access_token": token}
    requests.post(url, params=params)

def send_private_reply(recipient_id, message, token):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={token}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "messaging_type": "MESSAGE_TAG",
        "tag": "POST_PURCHASE_UPDATE" # ใช้ Tag ที่เหมาะสม
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        VERIFY_TOKEN_FROM_ENV = os.getenv("VERIFY_TOKEN")
        if request.args.get("hub.verify_token") == VERIFY_TOKEN_FROM_ENV:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.get_json()
        if data and data.get("object") == "page":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "feed" and change.get("value", {}).get("item") == "comment":
                        page_id = entry.get("id")
                        comment_data = change.get("value")
                        comment_id = comment_data.get("comment_id")
                        sender_id = comment_data.get("from", {}).get("id")
                        
                        # ป้องกันการตอบกลับคอมเมนต์ของตัวเอง
                        if sender_id == page_id:
                            continue

                        page = FacebookPage.query.filter_by(page_id=page_id).first()
                        if page and page.access_token:
                            # ตอบกลับคอมเมนต์
                            reply_text = page.reply_text or "ขอบคุณสำหรับความคิดเห็นครับ ❤️"
                            reply_to_comment(comment_id, reply_text, page.access_token)
                            
                            # ส่งข้อความเข้า Inbox
                            inbox_message = "แอดมินได้รับข้อความแล้วครับ ❤️"
                            send_private_reply(sender_id, inbox_message, page.access_token)
        return "OK", 200

    return "Not Found", 404

# ... (ส่วน if __name__ == '__main__': เหมือนเดิม)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
