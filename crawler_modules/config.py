import os
try:
    import yaml
except ImportError:
    yaml = None
from types import SimpleNamespace


class Config(SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)


def get_config():
    """
    Lädt Konfiguration aus `config.yaml` oder Umgebungsvariablen.
    Gibt ein Config-Objekt zurück, das Attribute und .get() unterstützt.
    """
    # Projekt-Root ist eine Ebene über diesem Modul
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")

    # YAML laden, falls installiert und Datei vorhanden
    raw_cfg = {}
    if yaml:
        try:
            with open(config_path, 'r') as f:
                raw_cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raw_cfg = {}

    # Environment-Overrides für alle relevanten Keys
    env_map = {
        "REDDIT_CLIENT_ID":          "reddit_client_id",
        "REDDIT_CLIENT_SECRET":      "reddit_client_secret",
        "REDDIT_USER_AGENT":         "reddit_user_agent",
        "OPENAI_API_KEY":            "openai_api_key",
        "GEMINI_API_KEY":            "gemini_api_key",
        "AI_PROVIDER":               "ai_provider",
        "WEBHOOK_URL":               "webhook_url",
        "GOOGLE_SHEETS_KEYFILE":     "google_sheets_keyfile",
        "GOOGLE_SHEETS_SPREADSHEET": "google_sheets_spreadsheet",
        "PICKLE_OUTPUT_PATH":        "pickle_output_path",
        "CLEANUP_DAYS":              "cleanup_days",
        "CRON_SCHEDULE":             "cron_schedule",
    }
    for env_var, key in env_map.items():
        val = os.getenv(env_var)
        if val is not None:
            if key == 'cleanup_days':
                raw_cfg[key] = int(val)
            else:
                raw_cfg[key] = val

    # Default-Werte, falls nicht gesetzt
    raw_cfg.setdefault('ai_provider', 'openai')
    raw_cfg.setdefault('pickle_output_path', os.path.join(project_root, 'data', 'pickle'))
    raw_cfg.setdefault('cleanup_days', 7)

    return Config(**raw_cfg)
