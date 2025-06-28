# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
import json
import datetime



class ConsultingWebhookController(http.Controller):

    @route('/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def webhook_post(self, **kw):
        body = request.get_json_data()
        try:
            entry = body["entry"][0]
            change = entry["changes"][0]["value"]

            message = change["messages"][0]
            contact = change["contacts"][0]

            wa_id = message["from"]  # User's WhatsApp number
            name = contact["profile"]["name"]
            payload = message["button"]["payload"]
            timestamp = message["timestamp"]

            readable_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            if payload == "yes":
                print(f"✅ {name} ({wa_id}) replied YES at {readable_time}")
                # Optionally: update DB or trigger follow-up
            elif payload == "no":
                print(f"❌ {name} ({wa_id}) replied NO at {readable_time}")

        except Exception as e:
            print("❗ Error handling webhook:", e)

        return {"status": "received"}

    @route('/webhook', type='http', auth='public', csrf=False, methods=['GET'])
    def webhook_get(self, **kw):
        hub_challenge = kw.get('hub.challenge')
        if hub_challenge:
            try:
                return str(int(hub_challenge))
            except Exception:
                return "Invalid challenge", 400
        return "No challenge", 400

