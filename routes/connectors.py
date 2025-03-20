from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os
import json
from werkzeug.utils import secure_filename
from services.connectors.connector_service import save_connector_config
from services.reports.report_service import load_all_reports


connectors_bp = Blueprint('connectors', __name__)

# Папка для хранения файлов настроек доступа Google Sheets
GOOGLE_CREDENTIALS_PATH = "static/connectors/google_crend"
os.makedirs(GOOGLE_CREDENTIALS_PATH, exist_ok=True)  # Создаем папку, если ее нет


@connectors_bp.route('/connectors', methods=['GET'])
def list_connectors():
    """Список всех доступных коннекторов (группируем по типу read/write)."""
    from models.connector import Connector
    from flask_login import current_user
    
    reading_connectors = []  # Коннекторы типа "Чтение"
    writing_connectors = []  # Коннекторы типа "Запись"
    
    user_path = os.path.join("static/users", str(current_user.id), "connectors")
    if os.path.exists(user_path):
        for filename in os.listdir(user_path):
            if filename.endswith('.json'):
                file_path = os.path.join(user_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    connector_type = config.get("CONNECTOR_TYPE")
                    connector_info = {
                        "name": filename.replace('.json', ''),
                        "service": config.get("CONNECTOR_SERVICE", "Unknown"),
                        "type": connector_type
                    }
                    
                    if connector_type == "read":
                        reading_connectors.append(connector_info)
                    else:
                        writing_connectors.append(connector_info)
                except:
                    continue

    reports = load_all_reports(current_user.id)  # ✅ Загружаем отчёты с учетом пользователя
    print(reports)
    return render_template('connectors/list.html',
                           reading_connectors=reading_connectors,
                           writing_connectors=writing_connectors,
                           reports=reports)

@connectors_bp.route('/connectors/new', methods=['GET', 'POST'])
@login_required
def add_connector():
    user_id = current_user.id
    """Создание нового коннектора (выбор шаблона и сохранение данных)."""
    if request.method == 'POST':
        connector_name = request.form['connector_name']
        connector_type = request.form['connector_type']
        connector_template = request.form['connector_template']

        # Определяем шаблон коннектора
        if connector_template == "Яндекс.Директ":
            config_data = {
                "CONNECTOR_TYPE": "Яндекс.Директ",
                "YANDEX_OAUTH_TOKEN": request.form['yandex_oauth_token'],
                "CLIENT_LOGIN": request.form['client_login']
            }
        elif connector_template == "Google Sheets":
            # Загружаем файл учетных данных
            file = request.files['credentials_file']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(GOOGLE_CREDENTIALS_PATH, filename)
                file.save(file_path)
            else:
                flash("Ошибка: необходимо загрузить файл учетных данных!", "danger")
                return redirect(url_for('connectors.add_connector'))

            config_data = {
                "CONNECTOR_TYPE": "Google Sheets",
                "SERVICE_ACCOUNT": request.form['service_account'],
                "CREDENTIALS_FILE": filename  # Сохраняем только имя файла
            }
        else:
            flash("Ошибка: неизвестный шаблон коннектора!", "danger")
            return redirect(url_for('connectors.add_connector'))

        # Сохраняем конфиг в файл
        save_connector_config(connector_name, config_data, current_user.id)
        flash('Коннектор успешно сохранен!', 'success')
        return redirect(url_for('connectors.list_connectors'))

    return render_template('connectors/new.html')


