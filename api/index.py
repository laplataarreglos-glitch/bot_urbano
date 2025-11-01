from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

@app.route("/", methods=["GET"])
def root():
    return "OK"

@app.route("/api/index", methods=["POST"])
def webhook():
    update = request.get_json()
    print(update)  # Para ver lo que llega de Telegram
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)
