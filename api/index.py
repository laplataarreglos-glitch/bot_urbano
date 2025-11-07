from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Servidor Flask en Vercel funcionando"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("Webhook recibido:", data)
    return jsonify({"ok": True, "echo": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
