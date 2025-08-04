import os
import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    workdir = os.getenv("WORKDIR")
    if not workdir:
        return "WORKDIR environment variable not set", 500

    deploy_script = os.path.join(workdir, "scripts", "deploy.sh")
    subprocess.Popen(["/bin/bash", deploy_script])
    return "Deploy started", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
