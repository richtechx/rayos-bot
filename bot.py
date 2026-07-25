import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageReactionHandler
)

# 1. Inicializar la Base de Datos Local
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

# 2. Función para obtener o registrar usuarios automáticamente
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

# 3. Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rayos = obtener_o_crear_usuario(user.id, user.username or user.first_name)
    keyboard = [
        [InlineKeyboardButton("⚡ Ver Mi Perfil", callback_data='perfil')],
        [InlineKeyboardButton("🛒 Comprar Rayos (Stars)", callback_data='comprar')],
        [InlineKeyboardButton("🏆 Ver Tienda de Beneficios", callback_data='tienda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"¡Bienvenido, {user.first_name}! 💖\n\n"
        f"En nuestra batalla de fotos, acumula **⚡ Rayos** reaccionando en el canal, ganando concursos o sorteos.\n"
        f"Tienes un saldo inicial de **{rayos} ⚡ Rayos**.",
        reply_markup=reply_markup, parse_mode='Markdown'
    )

# 4. Ver Perfil
async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rayos = obtener_o_crear_usuario(user.id, user.username or user.first_name)
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

# 5. Manejador de Botones del Menú
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'perfil':
        await perfil(update, context)
    elif query.data == 'comprar':
        await query.message.edit_text("🛒 **Comprar Rayos con Stars:** Próximamente disponible.", parse_mode='Markdown')
    elif query.data == 'tienda':
        await query.message.edit_text(
            "🏆 **Tienda de Beneficios (Canjea tus ⚡):**\n\n"
            " * ✨ Votos adicionales\n"
            " * 🏆 Paso a la siguiente ronda\n"
            " * 👑 Acceso de administrador temporal\n"
            " * 📢 Publicidad en canales\n"
            " * 🎁 Sorteos exclusivos", 
            parse_mode='Markdown'
        )

# 6. Comando Administrador para premiar manualmente (Ganadores de batallas o sorteos)
async def premiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Uso correcto: `/premiar [ID_usuario] [cantidad]`", parse_mode='Markdown')
            return
        
        target_user_id = int(args[0])
        cantidad = int(args[1])

        conn = sqlite3.connect('rayos_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT rayos, username FROM usuarios WHERE user_id = ?', (target_user_id,))
        user = cursor.fetchone()

        if user:
            nuevo_saldo = user[0] + cantidad
            cursor.execute('UPDATE usuarios SET rayos = ? WHERE user_id = ?', (nuevo_saldo, target_user_id))
            conn.commit()
            conn.close()
            
            await update.message.reply_text(f"✅ ¡Éxito! Se han sumado **{cantidad} ⚡ Rayos** al usuario `{target_user_id}`. Nuevo saldo: {nuevo_saldo} ⚡.", parse_mode='Markdown')
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id, 
                    text=f"🎉 ¡Felicidades! Has ganado **{cantidad} ⚡ Rayos** por tu victoria en el concurso. Tu nuevo saldo es de {nuevo_saldo} ⚡.", 
                    parse_mode='Markdown'
                )
            except:
                pass
        else:
            conn.close()
            await update.message.reply_text("❌ No se encontró ningún usuario con ese ID (debe iniciar el bot con /start primero).")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar: {e}")

# 7. AUTOMÁTICO: Dar 1 Rayo cuando un usuario reacciona (vota) en el canal
async def track_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message_reaction:
        user = update.message_reaction.user
        if user:
            user_id = user.id
            username = user.username or user.first_name
            
            # Si añade una reacción nueva en el canal
            if update.message_reaction.new_reaction:
                conn = sqlite3.connect('rayos_bot.db')
                cursor = conn.cursor()
                cursor.execute('SELECT rayos FROM usuarios WHERE user_id = ?', (user_id,))
                db_user = cursor.fetchone()
                
                if db_user:
                    nuevo_saldo = db_user[0] + 1
                    cursor.execute('UPDATE usuarios SET rayos = ? WHERE user_id = ?', (nuevo_saldo, user_id))
                else:
                    cursor.execute('INSERT INTO usuarios (user_id, username, rayos) VALUES (?, ?, ?)', (user_id, username, 11))
                
                conn.commit()
                conn.close()

# 8. Configuración principal
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("perfil", perfil))
    app.add_handler(CommandHandler("premiar", premiar))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageReactionHandler(track_reactions)) # Escucha las reacciones del canal automáticamente
    
    app.run_polling()

if __name__ == '__main__':
    main()
