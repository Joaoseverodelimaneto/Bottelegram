import telebot
from flask import Flask, request, jsonify
import threading
import requests

TOKEN = "8670710885:AAEFkqDNOOIuIAD7Dn1HuEADYR1MxoVi5TE"

GROUP = "@ScorpionRevv"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

users = {}

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

    data = request.json

    username = data.get("username","").replace("@","").lower()

    if username not in users:

        return jsonify({
            "success": False,
            "message": "Usuário não iniciou o bot"
        })

    user_id = users[username]

    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember"

    params = {
        "chat_id": GROUP,
        "user_id": user_id
    }

    r = requests.get(url, params=params)

    result = r.json()

    try:

        status = result["result"]["status"]

        if status in ["member", "administrator", "creator"]:

            return jsonify({
                "success": True,
                "message": "Verificado"
            })

        else:

            return jsonify({
                "success": False,
                "message": "Não está no grupo"
            })

    except:

        return jsonify({
            "success": False,
            "message": "Erro"
        })

# =========================
# RUN
# =========================

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

app.run(host="0.0.0.0", port=5000)
