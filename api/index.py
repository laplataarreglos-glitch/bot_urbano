from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Servidor Flask en Vercel funcionando"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("Webhook recibido:", data)
    return jsonify({"ok": True, "msg": "Webhook recibido"}), 200

if __name__ == "__main__":
    app.run(debug=True)
