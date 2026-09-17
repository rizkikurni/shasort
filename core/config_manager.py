import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

APP_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = APP_ROOT / "presets"
USER_SETTINGS_PATH = APP_ROOT / "user_settings.json"

DEFAULT_PROFILE = {
    "profile_name": "Wedding Sorter",
    "mode": "move",
    "duplicate_strategy": "rename",
    "bindings": {
        "1": {"folder": "Close_Up", "label": "Foto Close Up"},
        "2": {"folder": "Foto_Bareng", "label": "Group Photos"},
        "3": {"folder": "Dokumentasi", "label": "Dokumentasi Umum"},
        "4": {"folder": "Dekorasi", "label": "Detail & Dekorasi"},
        "Delete": {"folder": "_Rejected", "label": "Foto Ditolak / Blur"}
    }
}

class ConfigManager:
    """Manages preset profiles, bindings, and persistent user settings."""

    @staticmethod
    def ensure_directories():
        PRESETS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_folder_name(name: str) -> str:
        """Sanitizes folder name to prevent illegal filesystem characters."""
        # Replace Windows illegal chars < > : " / \ | ? *
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', name.strip())
        return cleaned or "Folder"

    @classmethod
    def list_presets(cls) -> List[Dict[str, str]]:
        """Returns a list of available presets with their filename and profile_name."""
        cls.ensure_directories()
        presets = []
        for file in PRESETS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profile_name = data.get("profile_name", file.stem)
                    presets.append({
                        "file_stem": file.stem,
                        "file_path": str(file),
                        "profile_name": profile_name
                    })
            except Exception:
                presets.append({
                    "file_stem": file.stem,
                    "file_path": str(file),
                    "profile_name": file.stem
                })
        return presets

    @classmethod
    def load_preset(cls, preset_identifier: str) -> Dict[str, Any]:
        """
        Loads a preset by either full path, file stem, or profile_name.
        Returns DEFAULT_PROFILE if not found.
        """
        cls.ensure_directories()
        
        # Check if direct path
        path_candidate = Path(preset_identifier)
        if path_candidate.is_file():
            try:
                with open(path_candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error loading {path_candidate}: {e}")

        # Check by stem in presets directory
        stem_candidate = PRESETS_DIR / f"{preset_identifier}.json"
        if stem_candidate.is_file():
            try:
                with open(stem_candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error loading {stem_candidate}: {e}")

        # Check by matching profile_name inside JSON files
        for file in PRESETS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("profile_name", "").lower() == preset_identifier.lower():
                        return data
            except Exception:
                continue

        return DEFAULT_PROFILE.copy()

    @classmethod
    def save_preset(cls, profile_name: str, config_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Saves a preset JSON into the presets folder."""
        cls.ensure_directories()
        safe_profile_name = profile_name.strip() or "Custom Preset"
        if not filename:
            # Generate safe filename from profile name
            safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', safe_profile_name.lower()) + ".json"
        else:
            safe_filename = filename if filename.endswith(".json") else f"{filename}.json"

        target_path = PRESETS_DIR / safe_filename
        config_data["profile_name"] = safe_profile_name

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return str(target_path)

    @classmethod
    def load_user_settings(cls) -> Dict[str, Any]:
        """Loads last user preferences (last source, last destination, etc.)."""
        if USER_SETTINGS_PATH.is_file():
            try:
                with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error loading user settings: {e}")
        return {
            "last_source": "",
            "last_destination": "",
            "last_preset": "Wedding Sorter",
            "mode": "move",
            "duplicate_strategy": "rename"
        }

    @classmethod
    def save_user_settings(cls, settings: Dict[str, Any]):
        """Saves user preferences to user_settings.json."""
        try:
            with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigManager] Error saving user settings: {e}")

    @classmethod
    def validate_profile(cls, profile: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that a profile config has valid bindings and fields."""
        if not isinstance(profile, dict):
            return False, "Data konfigurasi tidak valid (bukan dictionary)."
        
        bindings = profile.get("bindings")
        if not bindings or not isinstance(bindings, dict):
            return False, "Profil harus memiliki minimal 1 shortcut tombol."

        seen_keys = set()
        for key, info in bindings.items():
            k = str(key).strip().upper()
            if not k:
                return False, "Terdapat shortcut dengan tombol kosong."
            if k in seen_keys:
                return False, f"Shortcut ganda ditemukan untuk tombol '{key}'."
            seen_keys.add(k)

            if not isinstance(info, dict) or not info.get("folder", "").strip():
                return False, f"Shortcut tombol '{key}' tidak memiliki folder tujuan."

        return True, "OK"
