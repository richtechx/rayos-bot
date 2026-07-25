Para agregar el ruso (ru) al bot, simplemente sumamos un nuevo diccionario de traducciones con todos sus textos al idioma ruso y lo incorporamos al sistema junto con el español, inglés y ucraniano.
Aquí tienes el código completo y listo para copiar en tu archivo bot.py de GitHub:
import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler
)

# Diccionario de traducciones (Español, Inglés, Ucraniano y Ruso)
TEXTOS = {
    'es': {
        'bienvenida': "¡Bienvenido, {name}! 💖\n\nEn nuestra batalla de fotos, acumula **⚡ Rayos** votando en el canal, ganando concursos o sorteos.\nTienes un saldo inicial de **{rayos} ⚡ Rayos**.",
        'btn_perfil': "⚡ Ver Mi Perfil",
        'btn_comprar': "🛒 Comprar Rayos (Stars)",
        'btn_tienda': "🏆 Ver Tienda de Beneficios",
        'ya_voto': "⚠️ **¡Ya has votado en esta batalla!**\nNo puedes acumular rayos dos veces en la misma publicación.\n⚡ Tu saldo actual es de: **{saldo} Rayos**",
        'voto_exito': "✅ ¡Voto registrado con éxito!\n🎁 Has ganado **+1 ⚡ Rayo** por participar.\n⚡ Tu nuevo saldo es de: **{saldo} Rayos**",
        'perfil_txt': "👤 **Perfil:** @{username}\n🆔 ID: `{user_id}`\n\n⚡ **Saldo Actual:** {rayos} Rayos",
        'tienda_txt': "🏆 **Tienda de Beneficios (Canjea tus ⚡):**\n\n * ✨ Votos adicionales\n * 🏆 Paso a la siguiente ronda\n * 👑 Acceso de administrador temporal\n * 📢 Publicidad en canales\n * 🎁 Sorteos exclusivos",
        'comprar_txt': "🛒 **Comprar Rayos con Stars:** Próximamente disponible."
    },
    'en': {
        'bienvenida': "Welcome, {name}! 💖\n\nIn our photo battle, earn **⚡ Rays** by voting in the channel, winning contests, or giveaways.\nYou have an initial balance of **{rayos} ⚡ Rays**.",
        'btn_perfil': "⚡ View My Profile",
        'btn_comprar': "🛒 Buy Rays (Stars)",
        'btn_tienda': "🏆 View Benefits Store",
        'ya_voto': "⚠️ **You have already voted in this battle!**\nYou cannot accumulate rays twice on the same post.\n⚡ Your current balance is: **{saldo} Rays**",
        'voto_exito': "✅ Vote successfully registered!\n🎁 You have earned **+1 ⚡ Ray** for participating.\n⚡ Your new balance is: **{saldo} Rays**",
        'perfil_txt': "👤 **Profile:** @{username}\n🆔 ID: `{user_id}`\n\n⚡ **Current Balance:** {rayos} Rays",
        'tienda_txt': "🏆 **Benefits Store (Redeem your ⚡):**\n\n * ✨ Additional votes\n * 🏆 Advance to the next round\n * 👑 Temporary admin access\n * 📢 Channel advertising\n * 🎁 Exclusive giveaways",
        'comprar_txt': "🛒 **Buy Rays with Stars:** Coming soon."
    },
    'uk': {
        'bienvenida': "Ласкаво просимо, {name}! 💖\n\nУ нашій фотобитві заробляйте **⚡ Промені**, голосуючи в каналі, виграючи конкурси чи розіграші.\nВаш початковий баланс: **{rayos} ⚡ Променів**.",
        'btn_perfil': "⚡ Переглянути мій профіль",
        'btn_comprar': "🛒 Купити промені (Stars)",
        'btn_tienda': "🏆 Переглянути магазин привілеїв",
        'ya_voto': "⚠️ **Ви вже голосували в цій битві!**\nВи не можете отримувати промені двічі за один і той самий пост.\n⚡ Ваш поточний баланс: **{saldo} Променів**",
        'voto_exito': "✅ Голос успішно зараховано!\n🎁 Ви отримали **+1 ⚡ Промінь** за участь.\n⚡ Ваш новий баланс: **{saldo} Променів**",
        'perfil_txt': "👤 **Профіль:** @{username}\n🆔 ID: `{user_id}`\n\n⚡ **Поточний баланс:** {rayos} Променів",
        'tienda_txt': "🏆 **Магазин привілеїв (Обмінюйте ⚡):**\n\n * ✨ Додаткові голоси\n * 🏆 Прохід у наступний раунд\n * 👑 Тимчасовий доступ адміністратора\n * 📢 Реклама в каналах\n * 🎁 Ексклюзивні розіграші",
        'comprar_txt': "🛒 **Купити промені за Stars:** Незабаром буде доступно."
    },
    'ru': {
        'bienvenida': "Добро пожаловать, {name}! 💖\n\nВ нашей фотобитве зарабатывайте **⚡ Лучи**, голосуя в канале, побеждая в конкурсах или розыгрышах.\nВаш начальный баланс: **{rayos} ⚡ Лучей**.",
        'btn_perfil': "⚡ Посмотреть мой профиль",
        'btn_comprar': "🛒 Купить лучи (Stars)",
        'btn_tienda': "🏆 Магазин привилегий",
        'ya_voto': "⚠️ **Вы уже голосовали в этой битве!**\nНельзя получать лучи дважды за один и тот же пост.\n⚡ Ваш текущий баланс: **{saldo} Лучей**",
        'voto_exito': "✅ Голос успешно засчитан!\n🎁 Вы получили **+1 ⚡ Луч** за участие.\n⚡ Ваш новый баланс: **{saldo} Лучей**",
        'perfil_txt': "👤 **Профиль:** @{username}\n🆔 ID: `{user_id}`\n\n⚡ **Текущий баланс:** {rayos} Лучей",
        'tienda_txt': "🏆 **Магазин привилегий (Обменивайте ⚡):**\n\n * ✨ Дополнительные голоса\n * 🏆 Проход в следующий раунд\n * 👑 Временный доступ администратора\n * 📢 Реклама в каналах\n * 🎁 Эксклюзивные розыгрыши",
        'comprar_txt': "🛒 **Купить лучи за Stars:** Скоро будет доступно."
    }
}

def obtener_idioma(update: Update):
    user = update.effective_user
    if user and user.language_code:
        lang = user.language_code[:2].lower()
        if lang in TEXTOS:
            return lang
    return 'es'

# 1. Inicializar la Base de Datos Local
def init_db():
    conn = sqlite3.connect('rayos_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            rayos INTEGER DEFAULT 10
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votos_historial (
            user_id INTEGER,
            batalla_id TEXT,
            PRIMARY KEY (user_id, batalla_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 2. Función para obtener o registrar usuarios automáticamente
def obtener_o_crear_usuario(user_id, username):
    conn = sqlite3.connect('rayos_bot.db', check_same_thread=False)
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

# 3. Comando /start (Multilenguaje con soporte Ruso)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args 
    lang = obtener_idioma(update)
    t = TEXTOS[lang]
    
    rayos_actuales = obtener_o_crear_usuario(user.id, user.username or user.first_name)
    
    if args and args[0].startswith('votar_'):
        batalla_id = args[0]
        
        conn = sqlite3.connect('rayos_bot.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM votos_historial WHERE user_id = ? AND batalla_id = ?', (user.id, batalla_id))
        ya_voto = cursor.fetchone()
        
        if ya_voto:
            cursor.execute('SELECT rayos FROM usuarios WHERE user_id = ?', (user.id,))
            row = cursor.fetchone()
            saldo_actual = row[0] if row else rayos_actuales
            conn.close()
            
            await update.message.reply_text(
                t['ya_voto'].format(saldo=saldo_actual),
                parse_mode='Markdown'
            )
            return
        
        nuevo_saldo = rayos_actuales + 1
        cursor.execute('UPDATE usuarios SET rayos = ? WHERE user_id = ?', (nuevo_saldo, user.id))
        cursor.execute('INSERT INTO votos_historial (user_id, batalla_id) VALUES (?, ?)', (user.id, batalla_id))
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            t['voto_exito'].format(saldo=nuevo_saldo),
            parse_mode='Markdown'
        )
        return

    # Menú normal /start
    keyboard = [
        [InlineKeyboardButton(t['btn_perfil'], callback_data='perfil')],
        [InlineKeyboardButton(t['btn_comprar'], callback_data='comprar')],
        [InlineKeyboardButton(t['btn_tienda'], callback_data='tienda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        t['bienvenida'].format(name=user.first_name, rayos=rayos_actuales),
        reply_markup=reply_markup, parse_mode='Markdown'
    )

# 4. Ver Perfil
async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = obtener_idioma(update)
    t = TEXTOS[lang]
    rayos = obtener_o_crear_usuario(user.id, user.username or user.first_name)
    
    texto = t['perfil_txt'].format(username=user.username or user.first_name, user_id=user.id, rayos=rayos)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(texto, parse_mode='Markdown')
    else:
        await update.message.reply_text(texto, parse_mode='Markdown')

# 5. Manejador de Botones del Menú
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = obtener_idioma(update)
    t = TEXTOS[lang]
    
    if query.data == 'perfil':
        await perfil(update, context)
    elif query.data == 'comprar':
        await query.message.edit_text(t['comprar_txt'], parse_mode='Markdown')
    elif query.data == 'tienda':
        await query.message.edit_text(t['tienda_txt'], parse_mode='Markdown')

# 6. Comando Administrador
async def premiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Uso correcto: `/premiar [ID_usuario] [cantidad]`", parse_mode='Markdown')
            return
        
        target_user_id = int(args[0])
        cantidad = int(args[1])

        conn = sqlite3.connect('rayos_bot.db', check_same_thread=False)
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

# 7. Configuración principal
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("perfil", perfil))
    app.add_handler(CommandHandler("premiar", premiar))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == '__main__':
    main()

