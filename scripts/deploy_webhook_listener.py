# webhook_listener.py
import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    # Optional: validate GitHub secret here
    subprocess.Popen(["/bin/bash", "/home/ubuntu/deploy/deploy.sh"])
    return "Deploy started", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
