import os
try:
    import yaml
except ImportError:
    yaml = None
from types import SimpleNamespace


def get_config():
    """
    Lädt die Konfiguration aus der Datei `config.yaml` im Projekt-Root
    und gibt sie als Objekt zurück. Falls PyYAML nicht installiert oder Datei fehlt,
    werden nur Umgebungsvariablen genutzt.
    """
    # Projekt-Root ermitteln (eine Ebene über diesem Modul)
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")

    # YAML-Datei laden, falls möglich
    raw_cfg = {}
    if yaml:
        try:
            with open(config_path, 'r') as f:
                raw_cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            pass

    # Umgebungsvariablen überschreiben
    env_overrides = {
        "OPENAI_API_KEY": "openai_api_key",
        "GEMINI_API_KEY": "gemini_api_key",
        "WEBHOOK_URL": "webhook_url",
        "AI_PROVIDER": "ai_provider",
        "PICKLE_OUTPUT_PATH": "pickle_output_path",
        "GOOGLE_SHEETS_ENABLED": "google_sheets_enabled",
        "GOOGLE_SHEETS_CREDENTIALS": "google_sheets_credentials",
        "CRON_SCHEDULE": "cron_schedule",
    }
    for env_var, key in env_overrides.items():
        val = os.getenv(env_var)
        if val is not None:
            if key == 'google_sheets_enabled':
                raw_cfg[key] = val.lower() in ('1', 'true', 'yes')
            else:
                raw_cfg[key] = val

    # Als Objekt zurückgeben
    return SimpleNamespace(**raw_cfg)
