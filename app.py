from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()
    from auth import register_routes as auth_routes
    from routes import register_routes as app_routes
    auth_routes(app, login_manager)
    app_routes(app)

@app.route('/')
def index():
    return 'Groom Suite is live!'

if __name__ == '__main__':
    app.run(debug=True)