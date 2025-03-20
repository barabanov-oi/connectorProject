
from extensions import db

class Connector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    connector_type = db.Column(db.String(50), nullable=False)  # read/write
    service = db.Column(db.String(50), nullable=False)  # Яндекс.Директ/Google Sheets
    config_file = db.Column(db.String(150), nullable=False)  # Название файла с настройками
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
