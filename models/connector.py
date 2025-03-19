from extensions import db


class Connector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Название коннектора
    api_key = db.Column(db.String(100), nullable=False)  # API-ключ
    client_login = db.Column(db.String(100), nullable=False)  # Логин клиента Яндекс Директа
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Дата создания
    config_file = db.Column(db.String(150), nullable=False)  # Название файла с настройками коннектора
