import telebot
from flask import Flask, request, jsonify
import threading
import requests

TOKEN = "SEU_TOKEN"

GROUP = "@ScorpionRevv"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

users = {}

# versões em manutenção
maintenance_versions = [
    "1.0"
]

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    username = message.from_user.username
    nome = message.from_user.first_name

    if username:

        users[username.lower()] = user_id

        bot.reply_to(
            message,

            f"✅ Verificação iniciada\n\n"
            f"Nome: {nome}\n"
            f"@{username}\n"
            f"ID: {user_id}\n\n"
            f"Agora volte para o aplicativo."
        )

    else:

        bot.reply_to(
            message,
            "❌ Coloque um @ no Telegram."
        )

# =========================
# API VERIFY
# =========================

@app.route('/verify', methods=['POST'])
def verify():

    try:

        data = request.json

        username = data.get(
            "username",
            ""
        ).replace("@","").lower()

        version = data.get(
            "version",
            "0"
        )

        # =========================
        # MANUTENÇÃO
        # =========================

        if version in maintenance_versions:

            return jsonify({
                "success": False,
                "maintenance": True,
                "inGroup": True,
                "message": "Versão em manutenção"
            })

        # =========================
        # NÃO INICIOU BOT
        # =========================

        if username not in users:

            return jsonify({
                "success": False,
                "maintenance": False,
                "inGroup": False,
                "message": "Usuário não iniciou o bot"
            })

        user_id = users[username]

        # =========================
        # CHECK GROUP
        # =========================

        url = (
            f"https://api.telegram.org/bot"
            f"{TOKEN}/getChatMember"
        )

        params = {
            "chat_id": GROUP,
            "user_id": user_id
        }

        r = requests.get(url, params=params)

        result = r.json()

        status = result["result"]["status"]

        # =========================
        # ESTÁ NO GRUPO
        # =========================

        if status in [
            "member",
            "administrator",
            "creator"
        ]:

            return jsonify({
                "success": True,
                "maintenance": False,
                "inGroup": True,
                "message": "Verificado"
            })

        # =========================
        # SAIU DO GRUPO
        # =========================

        else:

            # remove do sistema
            if username in users:
                del users[username]

            return jsonify({
                "success": False,
                "maintenance": False,
                "inGroup": False,
                "message": "Saiu do grupo"
            })

    except Exception as e:

        return jsonify({
            "success": False,
            "maintenance": False,
            "inGroup": False,
            "message": str(e)
        })

# =========================
# RUN
# =========================

def run_bot():
    bot.infinity_polling()

threading.Thread(
    target=run_bot
).start()

app.run(
    host="0.0.0.0",
    port=5000
        )
