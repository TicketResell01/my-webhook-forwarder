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

    # --- MODIFIED LOGIC STARTS HERE ---

    user_email = data.get('email')
    product_id = data.get('product')
    site = data.get('site')
    price = data.get('Price') # Note: 'Price' is capitalized in your screenshot

    # Check if we have at least a product ID
    if not product_id:
        return jsonify({"status": "error", "message": "Missing product ID"}), 400

    # Check if this is a checkout (has an email) or a monitor notification
    if user_email:
        # This is a CHECKOUT notification
        discord_payload = {
            "embeds": [
                {
                    "title": "✅ Checkout Forwarded",
                    "color": 5763719, # Green
                    "fields": [
                        {"name": "Email", "value": user_email, "inline": True},
                        {"name": "Product ID", "value": product_id, "inline": True}
                    ]
                }
            ]
        }
    else:
        # This is a MONITOR notification
        discord_payload = {
            "embeds": [
                {
                    "title": "Monitor Notification",
                    "color": 16776960, # Yellow
                    "fields": [
                        {"name": "Product ID", "value": product_id, "inline": True},
                        {"name": "Site", "value": str(site), "inline": True},
                        {"name": "Price", "value": str(price), "inline": False}
                    ]
                }
            ]
        }
        
    # --- MODIFIED LOGIC ENDS HERE ---

    try:
        response = requests.post(DESTINATION_WEBHOOK_URL, json=discord_payload)
        response.raise_for_status()
        app.logger.info(f"Successfully forwarded webhook. Type: {'Checkout' if user_email else 'Monitor'}")
        return jsonify({"status": "success"}), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error sending webhook to Discord: {e}")
        return jsonify({"status": "error", "message": "Failed to forward webhook"}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
