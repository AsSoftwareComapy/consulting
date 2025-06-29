# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
import json
import datetime
import base64



class ConsultingWebhookController(http.Controller):

    @route('/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def webhook_post(self, **kw):
        body = request.get_json_data()
        request.env['ir.logging'].sudo().create({
            'name': 'Webhook Body',
            'type': 'server',
            'level': 'info',
            'message': json.dumps(body),
            'path': '/webhook',
            'line': 14,
            'func': 'webhook_post',
        })
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



    @route('/send_bulk_messages', type='http', auth='public', csrf=False, methods=['POST'])
    def send_bulk_messages(self, **kw):
        file = kw.get('file')
        location = kw.get('location')
        if not file or not location:
            return request.make_response(
                "Missing file or location", 
                headers=[('Content-Type', 'text/plain')],
                status=400
            )
        file_content = file.read()
        file_b64 = base64.b64encode(file_content)
        doc = request.env['consulting.document'].sudo().create({
            'name': file.filename,
            'document_file': file_b64,
            'location': location,
        })
        doc.action_import_and_send_whatsapp()
        return request.make_response(
            "Bulk messages sent successfully.",
            headers=[('Content-Type', 'text/plain')],
            status=200
        )

    @route('/get_logs', type='http', auth='public', csrf=False, methods=['GET'])
    def get_messages(self, status=None):
        domain = []
        reply_text = status
        # Filter for failed messages if reply_text is 'failed'
        if reply_text == 'failed':
            domain.append(('status_code', 'like', '400'))
        # Filter for reply_text yes/no/null as before
        elif reply_text == 'yes':
            domain.append(('reply_text', '=', 'yes'))
        elif reply_text == 'no':
            domain.append(('reply_text', '=', 'no'))
        elif reply_text == 'null':
            domain.append(('reply_text', '=', False))

        # Filter by response_text if provided

        logs = request.env['consulting.whatsapp.message.log'].sudo().search(domain, order='id desc')
        result = []
        for row in logs:
            result.append({
                "id": row.id,
                "phone_number": row.phone_number,
                "full_name": row.full_name,
                "location": row.location,
                "qualification": row.qualification,
                "status_code": row.status_code,
                "response_text": row.response_text,
                "sent_at": row.sent_at.isoformat() if row.sent_at else None,
                "reply": row.reply_text,
                "reply_date": row.reply_date.isoformat() if row.reply_date else None,
            })
            return request.make_response(
            data=json.dumps(result),
            headers=[('Content-Type', 'application/json')],
            status=200
        )
