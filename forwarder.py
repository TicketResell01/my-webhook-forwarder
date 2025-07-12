
from flask import Flask, request, jsonify
import requests
import logging

# --- PASTE YOUR DESTINATION WEBHOOK URL HERE ---
DESTINATION_WEBHOOK_URL = "YOUR_DESTINATION_DISCORD_WEBHOOK_URL"
# ----------------------------------------------

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    app.logger.info(f"Received data: {data}")

    if not data:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    user_email = data.get('email')
    product_id = data.get('product')

    if not user_email or not product_id:
        return jsonify({"status": "error", "message": "Missing email or product ID"}), 400

    discord_payload = {
        "embeds": [
            {
                "title": "✅ Checkout Forwarded",
                "color": 5763719,
                "fields": [
                    {"name": "User Email", "value": user_email, "inline": True},
                    {"name": "Product ID", "value": product_id, "inline": True}
                ]
            }
        ]
    }

    try:
        response = requests.post(DESTINATION_WEBHOOK_URL, json=discord_payload)
        response.raise_for_status()
        app.logger.info(f"Successfully forwarded webhook for {user_email}.")
        return jsonify({"status": "success"}), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error sending webhook to Discord: {e}")
        return jsonify({"status": "error", "message": "Failed to forward webhook"}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)