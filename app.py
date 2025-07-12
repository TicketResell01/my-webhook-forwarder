from flask import Flask, request, jsonify
import requests
import logging

# --- PASTE YOUR DESTINATION WEBHOOK URL HERE ---
DESTINATION_WEBHOOK_URL = "https://discord.com/api/webhooks/1352678838039085196/EhZFWXxlFUizfRXDZaUggMdMbgBxl08c63GyMY7y2mwiq54HAms14Dfavp9dTDk0bP8z"
# ----------------------------------------------

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

def find_field_value(fields, field_name):
    """Helper function to find a value from the 'fields' list."""
    for field in fields:
        if field.get('name') == field_name:
            return field.get('value')
    return 'N/A' # Return 'N/A' if not found

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    app.logger.info(f"Received data: {data}")

    if not data:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    # --- NEW LOGIC TO PARSE THE EMBED ---
    try:
        # The data is nested inside several layers
        embed = data['embeds'][0]
        fields = embed['fields']

        # Extract data using the helper function
        product_id = find_field_value(fields, 'Product')
        site = find_field_value(fields, 'Site')
        price = find_field_value(fields, 'Price')
        
        # We will assume that if 'email' exists at the top level, it's a checkout
        # Otherwise, we treat it as a monitor notification from the embed.
        user_email = data.get('email')

    except (KeyError, IndexError):
        app.logger.error("Received data is not in the expected embed format.")
        return jsonify({"status": "error", "message": "Unexpected data format"}), 400
    
    # --- END OF NEW PARSING LOGIC ---


    if user_email: # This part remains for your checkout notifications
        discord_payload = {
            "embeds": [
                {
                    "title": "✅ Checkout Forwarded",
                    "color": 5763719,
                    "fields": [
                        {"name": "Email", "value": user_email, "inline": True},
                        {"name": "Product ID", "value": product_id, "inline": True}
                    ]
                }
            ]
        }
    else: # This part now works correctly for the monitor notifications
        discord_payload = {
            "embeds": [
                {
                    "title": "Monitor Notification",
                    "color": 16776960,
                    "fields": [
                        {"name": "Product ID", "value": product_id, "inline": True},
                        {"name": "Site", "value": site, "inline": True},
                        {"name": "Price", "value": price, "inline": False}
                    ]
                }
            ]
        }

    try:
        response = requests.post(DESTINATION_WEBHOOK_URL, json=discord_payload)
        response.raise_for_status()
        app.logger.info("Successfully forwarded webhook.")
        return jsonify({"status": "success"}), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error sending webhook to Discord: {e}")
        return jsonify({"status": "error", "message": "Failed to forward webhook"}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
