from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FacebookPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String, unique=True)
    page_name = db.Column(db.String)
    access_token = db.Column(db.String)
    reply_text = db.Column(db.String)