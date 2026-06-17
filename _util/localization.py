import json
import os


class Loc:
    _data = {}
    _default = "en_US"
    _current_lang = _default

    @classmethod
    def load(cls, lang_code):
        cls._current_lang = lang_code
        path = f"locales/{lang_code}.json"

        if not os.path.exists(path):
            print(f"WARNING: Locale {lang_code} not found. Falling back to default.")
            return

        with open(path, "r", encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def tr(cls, key_path, default=None):
        keys = key_path.split('.')
        value = cls._data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default if default is not None else f"{key_path}"