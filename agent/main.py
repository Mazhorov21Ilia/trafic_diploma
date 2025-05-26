from flask import Flask, jsonify
import argparse
import socket
from collector import collect_network_metrics


app = Flask(__name__)


@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        metrics_data = collect_network_metrics(config)
        return jsonify(metrics_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def parse_args():
    parser = argparse.ArgumentParser(description="Traffic Monitoring Agent")
    parser.add_argument("--port", type=int, help="Port to run the agent HTTP server")
    return parser.parse_args()


if __name__ == "__main__":
    from config_m import load_config
    config = load_config()

    args = parse_args()
    port = args.port if args.port else config.get("server_polling_port", 8080)

    print(f"Starting Traffic Agent on http://{get_local_ip()}:{port}/metrics")
    app.run(host="0.0.0.0", port=port)