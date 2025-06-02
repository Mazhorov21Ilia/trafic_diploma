import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler


def poll_clients(config):
    interval = config["client_polling_interval_seconds"]
    clients = config["clients"]

    print("Starting client polling...")
    print(f"Polling interval: {interval} seconds")
    print(f"Clients: {', '.join(clients)}\n")

    def job():
        for client_url in clients:
            try:
                url = f"{client_url}/metrics"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"Metrics from {client_url}:")
                    print(response.json())
                    print("-" * 40)
                else:
                    print(f"Error fetching metrics from {client_url}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Network error with {client_url}: {str(e)}")

    scheduler = BackgroundScheduler()
    scheduler.add_job(job, "interval", seconds=interval)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()
