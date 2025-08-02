# app.py
import os
from flask import Flask, render_template
from models import db, FacebookPage
from webhook import webhook
from fb_login import fb_login
from broadcast import broadcast_bp

app = Flask(__name__)

# --- ส่วนที่แก้ไข ---
# ใช้ DATABASE_URL จาก Environment Variable ถ้ามี, ถ้าไม่มีให้ใช้ SQLite (สำหรับทดสอบบนเครื่อง)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook_pages.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# เพิ่ม SECRET_KEY เพื่อความปลอดภัย
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key')
# --- จบส่วนที่แก้ไข ---

db.init_app(app)
app.register_blueprint(webhook, url_prefix='/')
app.register_blueprint(fb_login, url_prefix='/')
app.register_blueprint(broadcast_bp, url_prefix='/')

# ใช้ app_context() ในการสร้างตาราง ซึ่งเป็นวิธีที่แนะนำ
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    pages = FacebookPage.query.all()
    return render_template('dashboard.html', pages=pages)

if __name__ == '__main__':
    # ส่วนนี้จะใช้เมื่อรันบนเครื่องตัวเองเท่านั้น
    app.run(host='0.0.0.0', port=5000, debug=True)
