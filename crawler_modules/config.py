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
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")

    # YAML laden, falls verfügbar
    raw_cfg = {}
    if yaml:
        try:
            with open(config_path, 'r') as f:
                raw_cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raw_cfg = {}

    # Env-Overrides
    env_map = {
        "OPENAI_API_KEY": "openai_api_key",
        "GEMINI_API_KEY": "gemini_api_key",
        "WEBHOOK_URL": "webhook_url",
        "AI_PROVIDER": "ai_provider",
        "PICKLE_OUTPUT_PATH": "pickle_output_path",
        "GOOGLE_SHEETS_ENABLED": "google_sheets_enabled",
        "GOOGLE_SHEETS_CREDENTIALS": "google_sheets_credentials",
        "CRON_SCHEDULE": "cron_schedule",
        "CLEANUP_DAYS": "cleanup_days",
        "GOOGLE_SHEETS_KEYFILE": "google_sheets_keyfile",
    }
    for env_var, key in env_map.items():
        val = os.getenv(env_var)
        if val is not None:
            if key == 'google_sheets_enabled':
                raw_cfg[key] = val.lower() in ('1', 'true', 'yes')
            elif key == 'cleanup_days':
                raw_cfg[key] = int(val)
            else:
                raw_cfg[key] = val

    # Default-Werte
    raw_cfg.setdefault('ai_provider', 'openai')
    raw_cfg.setdefault('pickle_output_path', os.path.join(project_root, 'data', 'pickle'))
    raw_cfg.setdefault('cleanup_days', 7)

    return Config(**raw_cfg)
