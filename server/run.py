from server.main import poll_clients
from config.config_m import load_config

config = load_config()
poll_clients(config)