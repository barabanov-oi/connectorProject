import gspread
from google.oauth2.service_account import Credentials
import os
import pandas as pd

# 🔹 Файл с ключами доступа
GOOGLE_CREDENTIALS_PATH = "services/connectors/config/google_crend"


def save_to_google_sheets(df, sheet_id, sheet_name, credentials_file):
    try:
        creds_path = os.path.join(GOOGLE_CREDENTIALS_PATH, credentials_file)

        if not os.path.exists(creds_path):
            print(f"❌ Ошибка: Файл {creds_path} не найден!")
            return False

        creds = Credentials.from_service_account_file(creds_path,
                                                      scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

        if df.empty:
            print("⚠️ DataFrame пуст, запись в Google Sheets пропущена.")
            return False

        print(f"📊 Записываем {len(df)} строк в Google Sheets.")

        # Очищаем лист перед записью
        sheet.clear()

        # Преобразуем DataFrame в список списков
        data = [df.columns.tolist()] + df.values.tolist()

        # Записываем данные в Google Sheets
        sheet.update("A1", data)

        print(f"✅ Данные успешно записаны в Google Sheets: {sheet_id} ({sheet_name})")
        return True

    except Exception as e:
        print(f"❌ Ошибка Google Sheets: {str(e)}")
        return False
