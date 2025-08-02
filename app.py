import os
from flask import Flask, render_template, request
from models import db, FacebookPage
# from webhook import webhook  <--- เราจะไม่ใช้ไฟล์นี้แล้ว
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
# --- จบส่วนการตั้งค่า ---

db.init_app(app)

# --- ลงทะเบียน Blueprint อื่นๆ (แต่ลบของ webhook ออก) ---
# app.register_blueprint(webhook, url_prefix='/') <--- เราจะไม่ใช้บรรทัดนี้แล้ว
app.register_blueprint(fb_login, url_prefix='/')
app.register_blueprint(broadcast_bp, url_prefix='/')

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    pages = FacebookPage.query.all()
    return render_template('dashboard.html', pages=pages)

# =================================================================
#  ย้ายโค้ด Webhook มาไว้ตรงนี้โดยตรง
# =================================================================
@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        # นี่คือโค้ดสำหรับยืนยันตัวตนกับ Facebook (เวอร์ชันดีบัก)
        challenge = request.args.get("hub.challenge")
        verify_token_from_fb = request.args.get("hub.verify_token") # รับ Token ที่ FB ส่งมา
        
        # ดึง VERIFY_TOKEN ของเราจาก Environment
        VERIFY_TOKEN_FROM_ENV = os.getenv("VERIFY_TOKEN")
        
        # ตรวจสอบ Token และส่ง challenge กลับไป
        if verify_token_from_fb == VERIFY_TOKEN_FROM_ENV:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        # ส่วนนี้คือโค้ดสำหรับรับคอมเมนต์จริง (ยังคงเดิม)
        data = request.get_json()
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'feed' and change.get('value', {}).get('item') == 'comment':
                    page_id = entry.get('id')
                    comment_id = change.get('value', {}).get('comment_id')
                    user_id = change.get('value', {}).get('from', {}).get('id')

                    page = FacebookPage.query.filter_by(page_id=page_id).first()
                    if page:
                        # ฟังก์ชันสำหรับตอบกลับ (ต้อง import requests เพิ่มถ้ายังไม่มี)
                        import requests
                        def reply_to_comment(c_id, message, token):
                            url = f"https://graph.facebook.com/v19.0/{c_id}/comments"
                            requests.post(url, data={"message": message, "access_token": token})

                        reply_to_comment(comment_id, page.reply_text or "ขอบคุณสำหรับความคิดเห็นครับ ❤️", page.access_token)

        return "OK", 200

    return "Not Found", 404

# =================================================================
#  จบส่วนของ Webhook
# =================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
