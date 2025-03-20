from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Flask
from flask_login import login_required, current_user
import threading
import json
from services.reports.report_service import load_report_config, save_report_config
from services.connectors.connector_service import load_connector_config
from services.direct_reports import process_reports
from services.date_utils import parse_dates, get_periods
from services.reports.file_saver import save_report_to_file
from services.reports.google_sheets_saver import save_to_google_sheets
from services.reports.report_queue import add_report_to_queue, update_report_status, load_report_queue
from datetime import datetime
import pandas as pd

app = Flask(__name__)
reports_bp = Blueprint('reports', __name__)


def run_report_background(user_id, report_name):
    """Фоновый процесс для выполнения отчёта."""
    try:
        report_config = load_report_config(user_id, report_name)
        connector_config = load_connector_config("test-login", user_id)  # TODO: получать имя коннектора из конфига отчета
        token = connector_config.get("YANDEX_OAUTH_TOKEN")

        if not token:
            update_report_status(user_id, report_name, "Ошибка: отсутствует OAuth-токен")
            return

        field_names = report_config.get("FIELD_NAMES", [])
        if report_config.get("START_DATE") and report_config.get("END_DATE"):
            raw_start_date = report_config.get("START_DATE")
            raw_end_date = report_config.get("END_DATE")

            if raw_start_date and raw_end_date:
                start_date, end_date = parse_dates(raw_start_date, raw_end_date)
            else:
                start_date, end_date = None, None
            periods = get_periods(start_date, end_date, report_config.get("PERIOD_DETAIL", "none"))
            report_config["Periods"] = periods
        else:
            start_date, end_date = "Неизвестно", "Неизвестно"
        period_str = f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}" if start_date and end_date else "Неизвестно"

        df, report_lines, reports_ids = process_reports(token, field_names, report_config)

        if df.empty:
            update_report_status(client_login, report_name, "Готово (пустой отчет)", 0, f"{start_date} - {end_date}")
            return

        save_format = report_config.get("SAVE_FORMAT")
        if save_format in ["csv", "xlsx"]:
            save_report_to_file(df, client_login, report_name, save_format)

        save_type = report_config.get("SAVE_TYPE", "")
        result_link = "-"

        if save_type == "google_sheets":
            sheet_id = report_config.get("SHEET_ID")
            sheet_name = report_config.get("SHEET_NAME")
            credentials_file = report_config.get("CREDENTIALS_FILE", report_config.get("SAVE_DRIVER", ""))

            result_link = f"https://docs.google.com/spreadsheets/d/{sheet_id}" if sheet_id else None

            if sheet_id and sheet_name:
                success = save_to_google_sheets(df, sheet_id, sheet_name, credentials_file)
                if success:
                    update_report_status(client_login, report_name, "Готово", df.shape[0], period_str, result_link,
                                         reports_ids)
                else:
                    result_link = "-"

        update_report_status(client_login, report_name, "Готово", df.shape[0], period_str, result_link)

    except Exception as e:
        update_report_status(client_login, report_name, f"Ошибка: {str(e)}")


@reports_bp.route('/reports/<report_name>/run', methods=['GET', 'POST'])
@login_required
def run_report(report_name):
    user_id = current_user.id
    add_report_to_queue(user_id, report_name)
    thread = threading.Thread(target=run_report_background, args=(user_id, report_name))
    thread.start()
    flash(f"🚀 Отчёт {report_name} запущен!", "info")
    return redirect(url_for('reports.report_queue'))

@reports_bp.route('/reports/queue', methods=['GET'])
def report_queue():
    queue = load_report_queue()
    return render_template('reports/queue.html', queue=queue)

@reports_bp.route('/reports/', methods=['GET'])
@login_required
def list_reports():
    from services.reports.report_service import load_all_reports
    from services.reports.report_presets import ReportPresets

    reports = load_all_reports(current_user.id)
    presets = ReportPresets.get_available_presets()
    return render_template('reports/list.html', reports=reports, presets=presets)


@reports_bp.route('/reports/<int:user_id>/edit', methods=['GET'])
@login_required
def edit_report(user_id):
    if user_id != current_user.id:
        flash("❌ Ошибка: нет доступа к отчёту", "danger")
        return redirect(url_for('reports.list_reports'))
    user_id = current_user.id
    try:
        report_config = load_report_config(user_id, report_name)

        if not report_config:
            flash(f"❌ Ошибка: отчёт {report_name} не найден.", "danger")
            return "Ошибка: отчёт не найден", 404

        report_json = json.dumps(report_config, indent=4, ensure_ascii=False)

        return render_template(
            'reports/edit.html',
            report_name=report_name,
            report_json=report_json
        )

    except FileNotFoundError:
        flash(f"❌ Ошибка: файл отчета {report_name}.json не найден.", "danger")
        return "Ошибка: файл отчета не найден", 404

    except Exception as e:
        flash(f"❌ Внутренняя ошибка: {str(e)}", "danger")
        return f"Ошибка: {str(e)}", 500


def datetimeformat(value, format='%d-%m-%Y %H:%M:%S'):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return value
    return value.strftime(format)


def periodformat(value):
    try:
        start, end = value.split(" - ")
        start_date = datetime.strptime(start.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
        end_date = datetime.strptime(end.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
        return f"{start_date} - {end_date}"
    except Exception:
        return "Что-то пошло не так"

@reports_bp.route('/reports/<client_login>/<report_name>/save', methods=['POST'])
def save_report(client_login, report_name):
    try:
        report_data = request.get_json()
        save_report_config(client_login, report_name, report_data)
        return jsonify({"status": "success", "message": "✅ Отчет успешно сохранен!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Ошибка при сохранении: {str(e)}"}), 500