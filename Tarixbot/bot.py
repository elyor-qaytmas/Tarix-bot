import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import json, os

# --- SOZLAMALAR ---
TOKEN = "8162587349:AAHIw8rbmidX-giaQVA595Ky1ifobQSv9sI"  # Bot tokeningiz
ADMIN_ID = 1162175915  # Sizning Telegram ID
CHANNEL_USERNAME = "@Tarix1_Dominant"  # Kanal username

DATA_FILE = "tests.json"

# --- Yordamchi funksiyalar ---
def ensure_datafile():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_tests():
    ensure_datafile()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tests(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_answers(s: str):
    return [p.strip().upper() for p in s.replace(",", " ").split() if p.strip()]

def grade_from_percent(percent: float):
    if percent >= 86: return 5
    if percent >= 71: return 4
    if percent >= 56: return 3
    return 2

# --- START / HELP ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Testlar ro‘yxati", callback_data="list")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Salom! 👋\nMen test javoblarini tekshiruvchi botman ✅",
        reply_markup=reply_markup
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Foydalanish:\n\n"
        "/addtest KOD A,B,C,...   (faqat admin)\n"
        "/removetest KOD          (faqat admin)\n"
        "/listtests               (barcha testlarni ko‘rish)\n"
        "/check KOD A,B,C,...     (javoblarni tekshirish)\n"
    )

# --- ADMIN BUYRUQLARI ---
async def addtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Sizda ruxsat yo‘q!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❗ Foydalanish: /addtest <kod> <A,B,C,...>")
        return

    code = context.args[0]
    answers = normalize_answers(" ".join(context.args[1:]))
    data = load_tests()
    data[code] = answers
    save_tests(data)

    await update.message.reply_text(f"✅ Test '{code}' saqlandi ({len(answers)} ta savol).")

async def removetest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Sizda ruxsat yo‘q!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❗ Foydalanish: /removetest <kod>")
        return

    code = context.args[0]
    data = load_tests()

    if code in data:
        del data[code]
        save_tests(data)
        await update.message.reply_text(f"✅ Test '{code}' o‘chirildi.")
    else:
        await update.message.reply_text("❗ Test topilmadi.")

# --- TEST TEKSHIRISH ---
async def check_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ Foydalanish: /check <kod> <A,B,C,...>")
        return

    code = context.args[0]
    user_answers = normalize_answers(" ".join(context.args[1:]))
    data = load_tests()

    if code not in data:
        await update.message.reply_text("❌ Test topilmadi.")
        return

    correct_answers = data[code]
    total = len(correct_answers)
    user_answers = user_answers[:total] + [""] * max(0, total - len(user_answers))
    correct = sum(1 for u, c in zip(user_answers, correct_answers) if u == c)
    percent = round((correct / total) * 100, 2)
    grade = grade_from_percent(percent)

    await update.message.reply_text(
        f"🧾 Test: {code}\n"
        f"✅ To‘g‘ri: {correct}/{total}\n"
        f"📊 Foiz: {percent}%\n"
        f"🎯 Baho: {grade}"
    )

# --- TESTLAR RO‘YXATI ---
async def list_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_tests()
    if not data:
        await update.message.reply_text("📂 Hozircha testlar mavjud emas.")
    else:
        text = "📘 Mavjud testlar:\n" + "\n".join(f"• {k}" for k in data.keys())
        await update.message.reply_text(text)

# --- CALLBACK FUNKSIYALARI ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "list":
        data = load_tests()
        if not data:
            await query.edit_message_text("📂 Hozircha testlar mavjud emas.")
        else:
            text = "📘 Mavjud testlar:\n" + "\n".join(f"• {k}" for k in data.keys())
            await query.edit_message_text(text)

    elif query.data == "help":
        await query.edit_message_text(
            "📘 Foydalanish:\n"
            "/listtests — testlar ro‘yxati\n"
            "/check <kod> <javoblar> — test tekshirish\n"
            "/help — yordam"
        )

# --- ASOSIY FUNKSIYA ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("addtest", addtest))
    app.add_handler(CommandHandler("removetest", removetest))
    app.add_handler(CommandHandler("listtests", list_tests))
    app.add_handler(CommandHandler("check", check_test))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()

