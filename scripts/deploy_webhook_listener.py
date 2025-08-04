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

    try:
        result = subprocess.run(
            ["/bin/bash", deploy_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,  # decode bytes to string
        )
        return f"Deploy succeeded:\n{result.stdout}", 200
    except subprocess.CalledProcessError as e:
        return f"Deploy failed:\n{e.stderr}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
