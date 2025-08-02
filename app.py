# app.py (เวอร์ชันสำหรับดีบักไฟล์เดียว)
from flask import Flask, request

app = Flask(__name__)

# 1. สร้างเส้นทางสำหรับหน้าแรก
@app.route('/')
def homepage():
    return "Homepage is working!", 200

# 2. สร้างเส้นทางสำหรับ Webhook
@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        challenge = request.args.get("hub.challenge")
        if challenge:
            return challenge, 200
        else:
            return "Webhook route is working. Ready for Facebook verification.", 200

    return "OK", 200
