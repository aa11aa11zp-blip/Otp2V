import requests
import re
from telegram import *
from telegram.ext import *

# ================= CONFIG =================
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

# ================= STORAGE =================
users = {}
referrals = {}
groups = []
sent = set()

# ================= JOIN CHECK =================
def is_joined(bot, uid):
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ================= START =================
def start(update, context):
    uid = update.effective_user.id

    if context.args:
        ref = int(context.args[0])
        if ref != uid:
            referrals.setdefault(ref, [])
            if uid not in referrals[ref]:
                referrals[ref].append(uid)

    users.setdefault(uid, {})

    kb = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
    kb.append([InlineKeyboardButton("✅ چیک", callback_data="check")])

    update.message.reply_text("🔒 چینلونو کې ګډون وکړئ:", reply_markup=InlineKeyboardMarkup(kb))

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 نمبرونه", callback_data="numbers")],
        [InlineKeyboardButton("👥 ګروف اضافه کول", callback_data="addg")],
        [InlineKeyboardButton("👤 زما حساب", callback_data="account")]
    ])

# ================= CHECK =================
def check(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if is_joined(context.bot, uid):
        q.edit_message_text("✅ ښه راغلاست:", reply_markup=menu())
    else:
        q.answer("❌ Join وکړئ!", show_alert=True)

# ================= ACCOUNT =================
def account(update, context):
    q = update.callback_query
    uid = q.from_user.id

    count = len(referrals.get(uid, []))
    link = f"https://t.me/{context.bot.username}?start={uid}"

    q.edit_message_text(
        f"👤 حساب\n\n👥 ریفیرل: {count}/10\n\n🔗 لینک:\n{link}",
        reply_markup=menu()
    )

# ================= NUMBERS =================
def numbers(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if len(referrals.get(uid, [])) < 10:
        q.answer("❗ 10 ریفیرل پکار دی!", show_alert=True)
        return

    q.edit_message_text("⏳ نمبرونه درته راځي...", reply_markup=menu())

# ================= GROUP =================
def addg(update, context):
    update.callback_query.message.reply_text("ګروپ username راولیږئ:")
    return 1

def saveg(update, context):
    uid = update.message.from_user.id
    group = update.message.text

    if len(referrals.get(uid, [])) < 10:
        update.message.reply_text("❗ 10 ریفیرل نشته!")
        return ConversationHandler.END

    try:
        m = context.bot.get_chat_member(group, context.bot.id)
        if m.status == "administrator":
            groups.append(group)
            referrals[uid] = referrals[uid][10:]
            update.message.reply_text("✅ ګروپ ثبت شو (10 ریفیرل کم شول)")
        else:
            update.message.reply_text("❌ بوت ادمین نه دی")
    except:
        update.message.reply_text("❌ غلط ګروپ")

    return ConversationHandler.END

# ================= FETCH =================
def fetch():
    try:
        r = requests.get(API_URL, params={"token": API_TOKEN}, timeout=10)
        return r.json() if isinstance(r.json(), list) else []
    except:
        return []

# ================= USER MSG =================
def user_msg(phone, time):
    return f"""╭━━━〔 💬 نـوی نـمـبـر سـیـسـټـم 〕━━━╮
┃
┃  💀 نمبر ➤ 【 {phone[-6:]} 】
┃  ☠ مکمل نمبر ➤ 【 {phone} 】
┃  ⏳ وخت ➤ 【 {time} 】
┃
┣━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ⚡ زر استفاده وکړئ
┃  🚫 ناوخته مه کوئ
╰━━━━━━━━━━━━━━━━━━━━━━━╯"""

# ================= GROUP MSG =================
def group_msg(app, phone, msg, time):
    otp = "N/A"
    m = re.search(r"\d{4,8}", msg)
    if m:
        otp = m.group()

    return f"""_______________________________
نوی کود راورسیده 📲
💠خدمات نوم: {app}
🌏هیواد: --
🎭نمبر کوډ: --
🎫نمبر: {phone}
🎯وخت: {time}
OTPکوډ: {otp}
مکمل پیغام⭐️:
{msg}
_______________________________"""

# ================= JOB =================
def job(context):
    data = fetch()

    for i in data:
        app = i[0]
        phone = i[1]
        msg = i[2]
        time = i[3]

        if phone in sent:
            continue

        sent.add(phone)

        # USERS
        for uid in users:
            ref = len(referrals.get(uid, []))

            if ref < 10:
                context.bot.send_message(uid, "📢 نوی نمبر جوړ شو خو تاسو شرط نه لرئ")
                continue

            context.bot.send_message(
                uid,
                user_msg(phone, time),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔑 کوډ دلته", url="https://t.me/HematOTP")],
                    [InlineKeyboardButton("📢 معلومات", url="https://t.me/ProTech43")]
                ])
            )

        # GROUPS
        for g in groups:
            context.bot.send_message(
                g,
                group_msg(app, phone, msg, time),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 زموږ چینل", url="https://t.me/ProTech43")],
                    [InlineKeyboardButton("📲 نمبرونه", url="https://t.me/HematOtp1VBot")]
                ])
            )

        # ADMIN
        context.bot.send_message(ADMIN_ID, f"📊 NEW NUMBER: {phone}")

# ================= ADMIN =================
def admin(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    update.message.reply_text(
        f"👑 ADMIN PANEL\nUsers: {len(users)}\nGroups: {len(groups)}"
    )

# ================= MAIN =================
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

    dp.add_handler(conv)

    up.job_queue.run_repeating(job, interval=10, first=5)

    up.start_polling()
    up.idle()

if __name__ == "__main__":
    main() 
