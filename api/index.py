from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Servidor Flask activo"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Update recibido:", data)
    return jsonify({"msg": "Webhook recibido", "ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
