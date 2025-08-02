# webhook.py (เวอร์ชันสำหรับดีบักชั่วคราว)
from flask import Blueprint, request

webhook = Blueprint('webhook', __name__)

@webhook.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    # สำหรับการดีบัก เราจะจัดการเฉพาะ GET request ที่ Facebook ส่งมาเพื่อยืนยันตัวตน
    if request.method == 'GET':
        # ดึงค่า challenge ที่ Facebook ส่งมา
        challenge = request.args.get("hub.challenge")

        # ถ้ามีค่า challenge ส่งมา ให้ส่งค่านั้นกลับไปทันที
        if challenge:
            return challenge, 200
        else:
            # ถ้าเป็นการเข้าผ่านเบราว์เซอร์ปกติ ให้แสดงข้อความนี้
            return "Webhook is ready. Please verify from Facebook Developer page.", 200

    # สำหรับ POST request (ข้อความคอมเมนต์จริง) ให้ตอบกลับไปก่อนว่า OK
    return "OK", 200
