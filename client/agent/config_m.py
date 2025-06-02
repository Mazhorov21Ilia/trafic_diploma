import os
import yaml


def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Не найден файл {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config
