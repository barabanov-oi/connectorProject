from flask import Flask, render_template
from extensions import db, login_manager  # ✅ Теперь импортируем из extensions.py
from flask_login import LoginManager
from routes.reports import reports_bp, datetimeformat, periodformat  # ✅ Добавляем импорт


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем расширения
db.init_app(app)
login_manager.init_app(app)

# Импортируем auth_bp **после** инициализации Flask
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы (если нет)
    from routes.connectors import connectors_bp

    app.register_blueprint(connectors_bp)
    app.register_blueprint(reports_bp)  # ✅ Регистрируем Blueprint
    app.jinja_env.filters['datetimeformat'] = datetimeformat # Регистрируем фильтр в Jinja
    app.jinja_env.filters['periodformat'] = periodformat
    app.run(host='0.0.0.0', port=8080, debug=True)
