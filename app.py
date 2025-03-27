from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)

# Store user data temporarily (Replace with DB later)
user_data = {}

# WhatsApp number to forward details to
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUM")

# Load environment variables from .env file
load_dotenv()
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.form.get("Body").strip().lower()
    sender = request.form.get("From")

    response = MessagingResponse()
    msg = response.message()

    if sender not in user_data:
        # Initial Greeting
        msg.body("Hi, welcome to our Services! We provide services in the below modes:\n\n"
                 "1️⃣ Online Mode\n"
                 "2️⃣ Offline Mode\n\n"
                 "Please reply with '1' for Online Mode or '2' for Offline Mode.")
        user_data[sender] = {"step": "choose_mode"}

    elif user_data[sender]["step"] == "choose_mode":
        if incoming_msg == "1":
            msg.body("Please choose on which day we can provide our services:\n\n"
                     "1️⃣ Tuesday\n"
                     "2️⃣ Wednesday\n"
                     "3️⃣ Thursday\n"
                     "4️⃣ Saturday\n\n"
                     "Reply with the number corresponding to your preferred day.")
            user_data[sender]["step"] = "choose_day"
        elif incoming_msg == "2":
            msg.body("The available locations for our offline services are:\n\n"
                     "1️⃣ Bangalore\n"
                     "2️⃣ Hosakote\n"
                     "3️⃣ Malur\n\n"
                     "Reply with the number corresponding to your preferred location.")
            user_data[sender]["step"] = "choose_location"
        else:
            msg.body("Invalid input. Please reply with '1' for Online Mode or '2' for Offline Mode.")

    elif user_data[sender]["step"] == "choose_day":
        days = {"1": "Tuesday", "2": "Wednesday", "3": "Thursday", "4": "Saturday"}
        if incoming_msg in days:
            user_data[sender]["day"] = days[incoming_msg]
            msg.body(f"Our services are available from 3 PM - 6 PM on {days[incoming_msg]}.\n\n"
                     "Please enter your full name.")
            user_data[sender]["step"] = "enter_name"
        else:
            msg.body("Invalid choice. Please reply with 1, 2, 3, or 4.")

    elif user_data[sender]["step"] == "enter_name":
        user_data[sender]["name"] = incoming_msg
        msg.body("Please enter your 10-digit phone number.")
        user_data[sender]["step"] = "enter_phone"

    elif user_data[sender]["step"] == "enter_phone":
        if re.match(r"^\d{10}$", incoming_msg):
            user_data[sender]["phone"] = incoming_msg
            forward_message = (f"New Online Booking:\n\n"
                               f"Name: {user_data[sender]['name']}\n"
                               f"Phone: {user_data[sender]['phone']}\n"
                               f"Selected Day: {user_data[sender]['day']}")

            # Send to Admin via WhatsApp
            send_whatsapp_message(ADMIN_PHONE_NUMBER, forward_message)

            msg.body("Thank you! Our support team will reach you shortly.")
            del user_data[sender]  # Clear session
        else:
            msg.body("Invalid phone number. Please enter a valid 10-digit number.")

    elif user_data[sender]["step"] == "choose_location":
        locations = {
            "1": "Our location in Bangalore is near Manipal Hospital Malleshwaram.\nTimings: Monday & Friday, 3 PM - 5 PM.",
            "2": "DQ Clinic, Contact: +919980257071. Please contact us before coming.",
            "3": "Balaji Clinic, Contact: +918310364418. Please contact us before coming."
        }
        if incoming_msg in locations:
            msg.body(locations[incoming_msg])
            del user_data[sender]  # End session
        else:
            msg.body("Invalid choice. Please reply with 1, 2, or 3.")

    return str(response)


def send_whatsapp_message(to, message):
    """Function to send a WhatsApp message via Twilio API"""
    from twilio.rest import Client

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    client.messages.create(
        from_="whatsapp:+14155238886",  # Twilio Sandbox Number
        body=message,
        to=to
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
