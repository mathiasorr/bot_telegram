import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Obtener el token desde una variable de entorno
TOKEN = os.getenv("7935540841:AAHeU2ErYGWb1GLSVl6PaBq_JNGM9rjOFBQ")
if not TOKEN:
    raise ValueError("El token no está definido. Configura la variable de entorno TELEGRAM_BOT_TOKEN.")

# Cargar preguntas y respuestas desde el archivo JSON
with open('preguntas_respuestas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extraer los temas disponibles
TEMAS = list(data.keys())

# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = "¡Hola! Escoge un tema escribiendo su número o nombre:\n\n"
    for i, tema in enumerate(TEMAS, 1):
        mensaje += f"{i}. {tema}\n"
    await update.message.reply_text(mensaje)

# Función para manejar la selección de temas
async def manejar_tema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text.strip()

    # Manejar selección por número
    if mensaje_usuario.isdigit():
        indice = int(mensaje_usuario) - 1
        if 0 <= indice < len(TEMAS):
            tema = TEMAS[indice]
        else:
            await update.message.reply_text("Número inválido. Escoge un número válido.")
            return
    # Manejar selección por nombre del tema
    elif mensaje_usuario in TEMAS:
        tema = mensaje_usuario
    else:
        await update.message.reply_text("Tema no encontrado. Escribe un número o nombre válido.")
        return

    # Mostrar las preguntas del tema seleccionado
    preguntas = data[tema]
    mensaje_respuesta = f"Has seleccionado el tema: *{tema}*\n\n"
    for i, pregunta in enumerate(preguntas.keys(), 1):
        mensaje_respuesta += f"{i}. {pregunta}\n"

    mensaje_respuesta += "\nEscribe el número o la pregunta completa para obtener una respuesta."
    await update.message.reply_text(mensaje_respuesta, parse_mode="Markdown")

    # Guardar el tema seleccionado en el contexto del usuario
    context.user_data['tema_actual'] = tema

# Función para manejar preguntas y responder
async def manejar_pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text.strip()
    tema_actual = context.user_data.get('tema_actual')

    if not tema_actual:
        await update.message.reply_text("Primero debes seleccionar un tema. Usa /start para comenzar.")
        return

    preguntas = data[tema_actual]

    # Manejar selección por número
    if mensaje_usuario.isdigit():
        indice = int(mensaje_usuario) - 1
        if 0 <= indice < len(preguntas):
            pregunta = list(preguntas.keys())[indice]
        else:
            await update.message.reply_text("Número inválido. Escoge un número válido.")
            return
    # Manejar selección por texto completo
    elif mensaje_usuario in preguntas:
        pregunta = mensaje_usuario
    else:
        await update.message.reply_text("Pregunta no encontrada. Escribe un número o la pregunta completa.")
        return

    # Responder a la pregunta seleccionada
    respuesta = preguntas[pregunta]
    await update.message.reply_text(f"*Pregunta:* {pregunta}\n*Respuesta:* {respuesta}", parse_mode="Markdown")

# Función para el comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "Comandos disponibles:\n"
        "/start - Iniciar el bot y mostrar los temas\n"
        "/help - Mostrar esta ayuda\n\n"
        "Después de seleccionar un tema, puedes escribir el número o la pregunta completa para obtener una respuesta."
    )
    await update.message.reply_text(mensaje)

# Función principal
def main():
    # Crear la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Definir los manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Manejador de mensajes para seleccionar temas y preguntas
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_tema))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_pregunta))

    # Iniciar el bot
    print("El bot está corriendo... ¡Pulsa Ctrl+C para detenerlo!")
    application.run_polling()

if __name__ == "__main__":
    main()
