from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

mensajes = {}

#Guardar el mensaje del usuario
def handle_user_message(message):
    #Si el usuario no ha enviado ningun mensaje, se crea un nuevo diccionario
    if mensajes.get(message.from_user.id) == None:
        mensajes[message.from_user.id] = {"messages": [{
            "role": "user",
            "content": message.text}]}
    #Si el usuario ya ha enviado mensajes, se añade el mensaje al diccionario
    else:
        mensajes[message.from_user.id]["messages"].append({
            "role": "user",
            "content": message.text})
        
#Generar la respuesta del bot
def generate_response(message):
    #Generamos la respuesta con ChatGPT
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=mensajes[message.from_user.id]["messages"],)
    
    #Obtenemos la respuesta
    response = completion.choices[0].message.content

    #Añadimos la respuesta al diccionario
    mensajes[message.from_user.id]["messages"].append({
        "role": "assistant",
        "content": response})
    return response

#Funcion que se ejecuta cuando se recibe un mensaje
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_user_message(update.message)
    response = generate_response(update.message)
    await update.message.reply_text(response)

def main():
    #Cargamos el token de la API de Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    #Creamos el bot
    bot = Application.builder().token(TELEGRAM_TOKEN).build()

    #Funcion que se ejecuta cuando se recibe un mensaje
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    #Ejecutamos el bot
    bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()