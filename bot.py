import os
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # defina essa variável no Render
VIP1_LINK = "https://t.me/+SEU_GRUPO_VIP1"
VIP2_LINK = "https://t.me/+SEU_GRUPO_VIP2"

PLANO_1260 = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=45c2cc75bd004c99b269482bc6a71b69"
PLANO_2300 = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=9c8cf64efdbe4d26b2ea07e62c188421"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def index():
    return "Bot rodando!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Assinar por R$12,60", url=PLANO_1260)],
        [InlineKeyboardButton("Assinar por R$23,00", url=PLANO_2300)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Escolha um dos planos abaixo para acessar nossos grupos VIPs:",
        reply_markup=reply_markup
    )

async def verificar(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    url = f"https://api.mercadopago.com/v1/payments/search?external_reference={user_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('MP_ACCESS_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if "results" in data and data["results"]:
        status = data["results"][0]["status"]
        plan_id = data["results"][0].get("metadata", {}).get("plan_id", "")
        if status == "approved":
            if "45c2cc75bd004c99b269482bc6a71b69" in str(data):
                await update.message.reply_text(f"✅ Pagamento confirmado! Acesse seu grupo VIP:\n{VIP1_LINK}")
            elif "9c8cf64efdbe4d26b2ea07e62c188421" in str(data):
                await update.message.reply_text(f"✅ Pagamento confirmado! Acesse seu grupo VIP:\n{VIP2_LINK}")
            else:
                await update.message.reply_text("✅ Pagamento confirmado! Mas não identifiquei o plano.")
        else:
            await update.message.reply_text("❌ Pagamento ainda não aprovado.")
    else:
        await update.message.reply_text("❌ Nenhum pagamento encontrado com seu ID.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("verificar", verificar))
