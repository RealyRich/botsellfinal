import os
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

print("TOKEN:", TOKEN)


TOKEN = os.getenv("BOT_TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN não configurado nas variáveis de ambiente!")

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Assinar por R$12,60", url="https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=45c2cc75bd004c99b269482bc6a71b69")],
        [InlineKeyboardButton("Assinar por R$23,00", url="https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=9c8cf64efdbe4d26b2ea07e62c188421")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Escolha um dos planos abaixo para acessar nossos grupos VIPs:",
        reply_markup=reply_markup
    )

async def verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    url = f"https://api.mercadopago.com/v1/payments/search?external_reference={user_id}"
    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if "results" in data and data["results"]:
        status = data["results"][0]["status"]
        if status == "approved":
            # Substitua pelos seus links dos grupos VIP
            vip_link_1 = "https://t.me/+SEU_GRUPO_VIP1"
            vip_link_2 = "https://t.me/+SEU_GRUPO_VIP2"

            # Verifique qual plano foi pago pelo preapproval_plan_id
            preapproval_id = data["results"][0].get("preapproval_id", "")

            # Exemplo de checagem simplificada - ajuste conforme sua estrutura de dados no MP
            if "45c2cc75bd004c99b269482bc6a71b69" in str(data):
                await update.message.reply_text(f"✅ Pagamento confirmado! Acesse seu grupo VIP:\n{vip_link_1}")
            elif "9c8cf64efdbe4d26b2ea07e62c188421" in str(data):
                await update.message.reply_text(f"✅ Pagamento confirmado! Acesse seu grupo VIP:\n{vip_link_2}")
            else:
                await update.message.reply_text("✅ Pagamento confirmado! Mas não identifiquei o plano.")
        else:
            await update.message.reply_text("❌ Pagamento ainda não aprovado.")
    else:
        await update.message.reply_text("❌ Nenhum pagamento encontrado com seu ID.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("verificar", verificar))

if __name__ == "__main__":
    # Só use isso para rodar localmente
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

