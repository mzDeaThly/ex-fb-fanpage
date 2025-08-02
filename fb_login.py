# fb_login.py
import os
import requests
from flask import Blueprint, redirect, request, render_template
from models import db, FacebookPage

fb_login = Blueprint('fb_login', __name__)

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_REDIRECT_URI = os.getenv("FB_REDIRECT_URI") # เราจะตั้งค่านี้บน Render
FB_API_VERSION = "v19.0"

# --- ฟังก์ชันใหม่ที่เพิ่มเข้ามา ---
def get_long_lived_token(short_lived_token):
    """แลกเปลี่ยน Short-Lived Token เป็น Long-Lived Token"""
    url = f"https://graph.facebook.com/{FB_API_VERSION}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "fb_exchange_token": short_lived_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("access_token")
# --- จบฟังก์ชันใหม่ ---

@fb_login.route("/connect")
def connect_page():
    return render_template("connect.html")

@fb_login.route("/fb-login")
def fb_login_redirect():
    auth_url = f"https://www.facebook.com/{FB_API_VERSION}/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&scope=pages_manage_metadata,pages_read_engagement,pages_manage_posts,pages_messaging,pages_show_list"
    return redirect(auth_url)

@fb_login.route("/fb-callback")
def fb_callback():
    code = request.args.get("code")
    token_url = f"https://graph.facebook.com/{FB_API_VERSION}/oauth/access_token"
    params = {
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "redirect_uri": FB_REDIRECT_URI,
        "code": code
    }
    response = requests.get(token_url, params=params).json()
    user_token = response.get("access_token")

    if not user_token:
        return "Error getting user access token.", 400

    # Get page list
    page_url = f"https://graph.facebook.com/{FB_API_VERSION}/me/accounts?access_token={user_token}"
    pages = requests.get(page_url).json().get("data", [])

    for page_data in pages:
        existing_page = FacebookPage.query.filter_by(page_id=page_data["id"]).first()
        
        # --- ส่วนที่แก้ไข ---
        # รับ Long-Lived Page Access Token
        short_lived_page_token = page_data["access_token"]
        long_lived_page_token = get_long_lived_token(short_lived_page_token)

        if long_lived_page_token:
            if existing_page:
                # ถ้าเพจมีอยู่แล้ว ให้อัปเดต Token
                existing_page.access_token = long_lived_page_token
                existing_page.page_name = page_data["name"] # อัปเดตชื่อเผื่อมีการเปลี่ยนแปลง
            else:
                # ถ้าเป็นเพจใหม่ ให้สร้างรายการใหม่
                new_page = FacebookPage(
                    page_id=page_data["id"],
                    page_name=page_data["name"],
                    access_token=long_lived_page_token
                )
                db.session.add(new_page)
        # --- จบส่วนที่แก้ไข ---
        
    db.session.commit()
    return redirect(url_for("dashboard"))