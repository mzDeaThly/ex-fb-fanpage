from flask import Flask, render_template, redirect, url_for
from models import db, FacebookPage
from webhook import webhook
from fb_login import fb_login
from broadcast import broadcast_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook_pages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(webhook, url_prefix='/')
app.register_blueprint(fb_login, url_prefix='/')
app.register_blueprint(broadcast_bp, url_prefix='/')

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def dashboard():
    pages = FacebookPage.query.all()
    return render_template('dashboard.html', pages=pages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)