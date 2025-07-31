import os
import requests
from flask import Blueprint, redirect, request, session, url_for, render_template
from models import db, FacebookPage

fb_login = Blueprint('fb_login', __name__)

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_REDIRECT_URI = os.getenv("FB_REDIRECT_URI", "https://your-domain.onrender.com/fb-callback")
FB_API_VERSION = "v19.0"

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

    # Get page list
    page_url = f"https://graph.facebook.com/{FB_API_VERSION}/me/accounts?access_token={user_token}"
    pages = requests.get(page_url).json().get("data", [])

    for page in pages:
        existing = FacebookPage.query.filter_by(page_id=page["id"]).first()
        if not existing:
            new_page = FacebookPage(
                page_id=page["id"],
                page_name=page["name"],
                access_token=page["access_token"]
            )
            db.session.add(new_page)
    db.session.commit()

    return redirect(url_for("dashboard"))