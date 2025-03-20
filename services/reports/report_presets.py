
import json
import os
from typing import Dict, List

class ReportPresets:
    PRESETS_PATH = "services/reports/presets"
    
    @staticmethod
    def get_available_presets() -> List[Dict]:
        """Получает список доступных пресетов отчетов"""
        presets = []
        if not os.path.exists(ReportPresets.PRESETS_PATH):
            os.makedirs(ReportPresets.PRESETS_PATH)
            return presets
            
        for filename in os.listdir(ReportPresets.PRESETS_PATH):
            if filename.endswith('.json'):
                with open(os.path.join(ReportPresets.PRESETS_PATH, filename)) as f:
                    preset = json.load(f)
                    presets.append({
                        'id': filename.replace('.json', ''),
                        'name': preset.get('REPORT_NAME', 'Unnamed preset'),
                        'description': preset.get('DESCRIPTION', ''),
                        'fields': preset.get('FIELD_NAMES', [])
                    })
        return presets

    @staticmethod
    def get_preset_config(preset_id: str) -> Dict:
        """Получает конфигурацию пресета по ID"""
        preset_path = os.path.join(ReportPresets.PRESETS_PATH, f"{preset_id}.json")
        if not os.path.exists(preset_path):
            raise FileNotFoundError(f"Preset {preset_id} not found")
            
        with open(preset_path) as f:
            return json.load(f)
