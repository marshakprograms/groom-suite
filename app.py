from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from models import db

mail = Mail()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)

from datetime import datetime

@app.template_filter('format_date')
def format_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime('%B %d, %Y')
    except:
        return value
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()
    from auth import register_routes as auth_routes
    from routes import register_routes as app_routes
    auth_routes(app, login_manager)
    app_routes(app, mail)

if __name__ == '__main__':
    app.run(debug=True)