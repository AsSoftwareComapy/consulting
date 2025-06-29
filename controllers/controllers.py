# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
import json
import datetime



class ConsultingWebhookController(http.Controller):

    @route('/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def webhook_post(self, **kw):
        body = request.get_json_data()
        print(body)
        try:
            entry = body["entry"][0]
            change = entry["changes"][0]["value"]

            message = change["messages"][0]
            contact = change["contacts"][0]

            wa_id = message["from"]  
            name = contact["profile"]["name"]
            payload = message["button"]["payload"]
            timestamp = message["timestamp"]

            readable_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            # Find the most recent log record for this wa_id (phone_number)
            log = request.env['consulting.whatsapp.message.log'].sudo().search(
                [('phone_number', '=', wa_id)],
                order='create_date desc',
                limit=1
            )
            if log:
                log.write({
                    'reply_text': payload,
                    'reply_date': readable_time,
                })
            if payload == "yes":
                print(f"✅ {name} ({wa_id}) replied YES at {readable_time}")
                # Optionally: update DB or trigger follow-up
            elif payload == "no":
                print(f"❌ {name} ({wa_id}) replied NO at {readable_time}")

        except Exception as e:
            print("❗ Error handling webhook:", e)

        return "received"

    @route('/webhook', type='http', auth='none', csrf=False, methods=['GET'])
    def webhook_get(self, **kw):
        hub_challenge = kw.get('hub.challenge')
        if hub_challenge:
            try:
                return str(int(hub_challenge))
            except Exception:
                return "Invalid challenge", 400
        return "No challenge", 400

