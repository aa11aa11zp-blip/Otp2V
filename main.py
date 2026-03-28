import requests
import re
from telegram import *
from telegram.ext import *

# ========= CONFIG =========
BOT_TOKEN = "8547944263:AAEcZGBWImZyOWCWj9L0qIuKW1BM0OEN9ZM"
API_URL = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="
ADMIN_ID = 1316375131

CHANNELS = [
    "@ProTech43",
    "@WahidModeX",
    "@HematTech",
    "@Javeed_TECH",
    "@SQ_BotZ",
    "@HematOTP"
]

# ========= STORAGE =========
users = {}
referrals = {}
groups = []
sent = set()
used_codes = {}

# ========= JOIN CHECK =========
def is_joined(bot, uid):
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ========= START =========
def start(update, context):
    uid = update.effective_user.id

    if context.args:
        try:
            ref = int(context.args[0])
            if ref != uid:
                referrals.setdefault(ref, [])
                if uid not in referrals[ref]:
                    referrals[ref].append(uid)
        except:
            pass

    users[uid] = True

    buttons = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
    buttons.append([InlineKeyboardButton("✅ چیک", callback_data="check")])

    update.message.reply_text(
        "🔒 لطفاً چینلونه Join کړئ:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ========= MENU =========
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 نمبرونه", callback_data="numbers")],
        [InlineKeyboardButton("👥 ګروف اضافه کول", callback_data="addg")],
        [InlineKeyboardButton("👤 زما حساب", callback_data="account")]
    ])

# ========= CHECK =========
def check(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if is_joined(context.bot, uid):
        q.edit_message_text("✅ ښه راغلاست:", reply_markup=menu())
    else:
        q.answer("❌ ټول چینلونه Join کړئ!", show_alert=True)

# ========= ACCOUNT =========
def account(update, context):
    q = update.callback_query
    uid = q.from_user.id

    count = len(referrals.get(uid, []))
    link = f"https://t.me/{context.bot.username}?start={uid}"

    q.edit_message_text(
        f"👤 حساب\n\n👥 Referral: {count}/10\n\n🔗 لینک:\n{link}",
        reply_markup=menu()
    )

# ========= NUMBERS =========
def numbers(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if len(referrals.get(uid, [])) < 10:
        q.answer("❗ 10 Referral پکار دي!", show_alert=True)
        return

    q.edit_message_text("⏳ نمبرونه درته راځي...", reply_markup=menu())

# ========= GROUP =========
def addg(update, context):
    update.callback_query.message.reply_text("📩 د ګروف username راولیږئ:")
    return 1

def saveg(update, context):
    uid = update.message.from_user.id
    group = update.message.text

    if len(referrals.get(uid, [])) < 10:
        update.message.reply_text("❌ 10 Referral نشته!")
        return ConversationHandler.END

    try:
        m = context.bot.get_chat_member(group, context.bot.id)
        if m.status == "administrator":
            groups.append(group)
            referrals[uid] = referrals[uid][10:]
            update.message.reply_text("✅ ګروف ثبت شو (10 Referral کم شول)")
        else:
            update.message.reply_text("❌ Bot admin نه دی")
    except Exception as e:
        update.message.reply_text(f"ERROR: {e}")

    return ConversationHandler.END

# ========= GIFT CODE =========
def gift(update, context):
    uid = update.message.from_user.id
    text = update.message.text.strip().upper()

    if text == "NNJJK":
        if used_codes.get(uid):
            update.message.reply_text("❌ دا کوډ مخکې کارول شوی!")
            return

        used_codes[uid] = True
        referrals.setdefault(uid, [])

        for i in range(20):
            referrals[uid].append(f"gift_{i}_{uid}")

        update.message.reply_text("🎁 20 Referral درته اضافه شول ✅")

# ========= FETCH =========
def fetch():
    try:
        r = requests.get(API_URL, params={"token": API_TOKEN}, timeout=10)
        return r.json() if isinstance(r.json(), list) else []
    except:
        return []

# ========= USER MSG =========
def user_msg(phone, time):
    return f"""╭━━━〔 💬 نوی نمبر سیستم 〕━━━╮
┃ 💀 نمبر ➤ {phone[-6:]}
┃ ☠ مکمل ➤ {phone}
┃ ⏳ وخت ➤ {time}
╰━━━━━━━━━━━━━━━━━━━━━━━╯"""

# ========= GROUP MSG =========
def group_msg(app, phone, msg, time):
    otp = "N/A"
    m = re.search(r"\d{4,8}", msg)
    if m:
        otp = m.group()

    return f"""📲 OTP NEW

Service: {app}
Number: {phone}
Time: {time}
OTP: {otp}

{msg}
"""

# ========= JOB =========
def job(context):
    data = fetch()

    for i in data:
        try:
            app, phone, msg, time = i
        except:
            continue

        if phone in sent:
            continue

        sent.add(phone)

        # USERS
        for uid in users:
            ref = len(referrals.get(uid, []))

            if ref < 10:
                context.bot.send_message(uid, "📢 نوی نمبر راغی خو شرط نشته")
                continue

            context.bot.send_message(uid, user_msg(phone, time))

        # GROUPS
        for g in groups:
            context.bot.send_message(g, group_msg(app, phone, msg, time))

        # ADMIN
        context.bot.send_message(ADMIN_ID, f"📊 NEW NUMBER: {phone}")

# ========= ADMIN =========
def admin(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    update.message.reply_text(
        f"👑 ADMIN PANEL\nUsers: {len(users)}\nGroups: {len(groups)}"
    )

# ========= MAIN =========
def main():
    up = Updater(BOT_TOKEN, use_context=True)
    dp = up.dispatcher

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(addg, pattern="addg")],
        states={1: [MessageHandler(Filters.text, saveg)]},
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))

    dp.add_handler(CallbackQueryHandler(check, pattern="check"))
    dp.add_handler(CallbackQueryHandler(numbers, pattern="numbers"))
    dp.add_handler(CallbackQueryHandler(account, pattern="account"))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, gift))
    dp.add_handler(conv)

    up.job_queue.run_repeating(job, interval=10, first=5)

    up.start_polling()
    up.idle()

if __name__ == "__main__":
    main() 
