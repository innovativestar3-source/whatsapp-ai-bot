import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Credentials Environment Variables se aayenge
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1348874714979876")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_verify_token")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is Running!", 200

# Meta Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Incoming Messages Process Karna
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        if data.get("object"):
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]

            if "messages" in value:
                message = value["messages"][0]
                from_number = message["from"]
                
                if message.get("type") == "text":
                    user_text = message["text"]["body"]

                    response = model.generate_content(user_text)
                    bot_reply = response.text

                    send_whatsapp_message(from_number, bot_reply)

    except Exception as e:
        print(f"Error processing message: {e}")

    return jsonify({"status": "success"}), 200

def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
