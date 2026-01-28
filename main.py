from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ChatMemberHandler
import os
TOKEN = os.getenv("8534738656:AAHvzZLIaA4FooC35ViwBesgsnGzRsBVdAo")

CHANNEL_ID = -1003650837824 # apne channel ka ID
YOUTUBE_LINK = "https://youtube.com/@sasteheist?si=VN5cWyqSYOMt0Guf"

users = {}
referrals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"points": 0, "verified": False}
        if ref:
            referrals[user_id] = int(ref)

    keyboard = [
        [InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/yourchannel")],
        [InlineKeyboardButton("▶️ Subscribe YouTube", url=YOUTUBE_LINK)],
        [InlineKeyboardButton("✅ VERIFY", callback_data="verify")]
    ]
    await update.message.reply_text(
        "🔐 Verification Required\n\nJoin Telegram + Subscribe YouTube\nThen click VERIFY",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    if member.status not in ["member", "administrator", "creator"]:
        await query.answer("❌ Join Telegram channel first", show_alert=True)
        return

    if not users[user_id]["verified"]:
        users[user_id]["verified"] = True
        if user_id in referrals:
            referrer = referrals[user_id]
            users[referrer]["points"] += 1
            await context.bot.send_message(
                referrer,
                f"✅ New Verified Referral\n+1 Point\nTotal: {users[referrer]['points']}"
            )

    await query.answer("✅ Verified Successfully", show_alert=True)

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = users.get(user_id, {}).get("points", 0)
    await update.message.reply_text(f"⭐ Your Points: {points}")

async def track_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.chat_member.from_user.id
    new_status = update.chat_member.new_chat_member.status

    if new_status == "left" and user_id in referrals:
        referrer = referrals[user_id]
        users[referrer]["points"] -= 1
        await context.bot.send_message(
            referrer,
            f"⚠️ Your referral left\n-1 Point\nTotal: {users[referrer]['points']}"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mypoints", mypoints))
app.add_handler(CallbackQueryHandler(verify))
app.add_handler(ChatMemberHandler(track_leave, ChatMemberHandler.CHAT_MEMBER))

app.run_polling()
