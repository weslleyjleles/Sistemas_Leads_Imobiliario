from flask import Flask, redirect
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from database import db

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

from models.user import User
from models.lead import Lead
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route("/")
def home():
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)