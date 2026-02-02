import os
import asyncio
import time
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, render_template, request, session

from telethon import TelegramClient

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

SESSION_FOLDER = 'sessions'
os.makedirs(SESSION_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', watermark='— anuj_creation')

@app.route('/send_code', methods=['POST'])
def send_code():
    api_id = int(request.form['api_id'])
    api_hash = request.form['api_hash']
    phone = request.form['phone']

    session['api_id'] = api_id
    session['api_hash'] = api_hash
    session['phone'] = phone

    async def start_client():
        client = TelegramClient(os.path.join(SESSION_FOLDER, phone), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            result = await client.send_code_request(phone)
            session['phone_code_hash'] = result.phone_code_hash
        await client.disconnect()

    asyncio.run(start_client())
    return render_template('login.html', watermark='— anuj_creation')
# my apps this is my app
@app.route('/verify', methods=['POST'])
def verify():
    try:
        code = int(request.form['code'])
        api_id = session.get('api_id')
        api_hash = session.get('api_hash')
        phone = session.get('phone')
        phone_code_hash = session.get('phone_code_hash', None)

        if not all([api_id, api_hash, phone, phone_code_hash]):
            return render_template('error.html', error="Session expired. Please login again", watermark='— anuj_creation'), 401

        async def complete_login():
            client = TelegramClient(os.path.join(SESSION_FOLDER, phone), api_id, api_hash)
            await client.connect()
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            dialogs = await client.get_dialogs()
            await client.disconnect()

            groups = [
                {'id': dialog.id, 'title': dialog.title}
                for dialog in dialogs if dialog.is_group
            ]
            return groups

        groups = asyncio.run(complete_login())
        return render_template('schedule.html', groups=groups, watermark='— anuj_creation')
    except ValueError:
        return render_template('error.html', error="Invalid code format. Please enter numbers only", watermark='— anuj_creation'), 400
    except Exception as e:
        return render_template('error.html', error=f"Verification failed: {str(e)}. Please try again", watermark='— anuj_creation'), 400

def wait_until(target: datetime):
    while True:
        now = datetime.now()
        diff = (target - now).total_seconds()
        if diff <= 0:
            break
        elif diff > 1:
            time.sleep(0.9)
        elif diff > 0.1:
            time.sleep(0.05)
        elif diff > 0.01:
            time.sleep(0.005)
        else:
            time.sleep(0.001)

def send_message_at_time(api_id, api_hash, phone, group_id, message, send_time):
    async def sender():
        session_file = os.path.join(SESSION_FOLDER, f"{phone}.session")
        try:
            client = TelegramClient(session_file, api_id, api_hash)
            await client.connect()
            print(f"[{datetime.now()}] Client connected for phone {phone}")

            wait_until(send_time)
            await client.send_message(group_id, message)
            print(f"[{datetime.now()}] Message sent successfully to group {group_id}")
            await client.disconnect()
        except Exception as e:
            print(f"[{datetime.now()}] Error sending message: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(sender())

@app.route('/schedule_message', methods=['POST'])
def schedule_message():
    try:
        group_id = int(request.form['group_id'])
        message = request.form['message'].strip()

        if not message:
            return render_template('error.html', error="Message cannot be empty", watermark='— anuj_creation'), 400

        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        second = int(request.form['second'])
        millisecond = int(request.form['millisecond'])

        if not all(key in session for key in ['api_id', 'api_hash', 'phone']):
            return render_template('error.html', error="Session expired. Please login again", watermark='— anuj_creation'), 401

        api_id = session['api_id']
        api_hash = session['api_hash']
        phone = session['phone']

        now = datetime.now()
        send_time = now.replace(
            hour=hour, minute=minute, second=second, microsecond=millisecond * 1000
        )
        if send_time < now:
            send_time += timedelta(days=1)

        Thread(
            target=send_message_at_time,
            args=(api_id, api_hash, phone, group_id, message, send_time),
            daemon=True,
        ).start()

        return render_template('redirect.html', delay=10, watermark='— anuj_creation')
    except Exception as e:
        return render_template('error.html', error=f"Error scheduling message: {str(e)}", watermark='— anuj_creation'), 400

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Clear the session after message is sent"""
    session.clear()
    print(f"Session cleared at {datetime.now()}")
    return render_template('index.html', watermark='— anuj_creation')

if __name__ == '__main__':
    # Note: In production (Docker), use Gunicorn instead
    # This is only for local development
    app.run(debug=False, host='0.0.0.0', port=5000)
