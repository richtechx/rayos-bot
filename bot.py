import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Base de datos local
def init_db():
    conn = sqlite3.connect('rayos_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            rayos INTEGER DEFAULT 10
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def obtener_o_crear_usuario(user_id, username):
    conn = sqlite3.connect('rayos_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT rayos FROM usuarios WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO usuarios (user_id, username, rayos) VALUES (?, ?, ?)', (user_id, username, 10))
        conn.commit()
        rayos = 10
    else:
        rayos = user[0]
    conn.close()
    return rayos

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rayos = obtener_o_crear_usuario(user.id, user.username)
    keyboard = [
        [InlineKeyboardButton("⚡ Ver Mi Perfil", callback_data='perfil')],
        [InlineKeyboardButton("🛒 Comprar Rayos (Stars)", callback_data='comprar')],
        [InlineKeyboardButton("🏆 Ver Tienda de Beneficios", callback_data='tienda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"¡Bienvenido, {user.first_name}! 💖\n\n"
        f"Tienes un saldo inicial de **{rayos} ⚡ Rayos**.",
        reply_markup=reply_markup, parse_mode='Markdown'
    )

async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rayos = obtener_o_crear_usuario(user.id, user.username)
    texto = (
        f"👤 **Perfil:** @{user.username or user.first_name}\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"⚡ **Saldo Actual:** {rayos} Rayos"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(texto, parse_mode='Markdown')
    else:
        await update.message.reply_text(texto, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'perfil':
        await perfil(update, context)
    elif query.data == 'comprar':
        await query.message.edit_text("🛒 **Comprar Rayos con Stars:** Próximamente disponible.", parse_mode='Markdown')
    elif query.data == 'tienda':
        await query.message.edit_text("🏆 **Tienda:** Votos extra, pases de ronda y más.", parse_mode='Markdown')

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("perfil", perfil))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
