import requests
import re
from telegram import *
from telegram.ext import *

# ================= CONFIG =================
BOT_TOKEN = "8289437839:AAFAg63ujCDn6ebG_WtjXZySZPQfDJrqBw8"
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

# ================= REF COUNT =================
def get_refs(uid):
    return len(referrals.get(uid, []))

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

    # referral system
    if context.args:
        ref = int(context.args[0])
        if ref != uid:
            referrals.setdefault(ref, [])
            if uid not in referrals[ref]:
                referrals[ref].append(uid)

    users.setdefault(uid, {"index": 0})

    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start={uid}"

    kb = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
    kb.append([InlineKeyboardButton("✅ چیک", callback_data="check")])

    update.message.reply_text(
        f"🔒 چینلونو کې ګډون وکړئ:\n\n👥 ستاسو ریفیرل: {get_refs(uid)}\n🔗 لینک:\n{ref_link}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= CHECK =================
def check(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if is_joined(context.bot, uid):
        kb = [
            [InlineKeyboardButton("📱 نمبرونه", callback_data="numbers")],
            [InlineKeyboardButton("👥 ګروف اضافه کول", callback_data="addg")],
            [InlineKeyboardButton("👤 زما حساب", callback_data="account")]
        ]
        q.edit_message_text("✅ ښه راغلاست:", reply_markup=InlineKeyboardMarkup(kb))
    else:
        q.answer("❌ Join وکړئ!", show_alert=True)

# ================= ACCOUNT =================
def account(update, context):
    q = update.callback_query
    uid = q.from_user.id

    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start={uid}"

    text = f"""╭━━━〔 👤 زمــا حـسـاب 〕━━━╮
┃ 🆔 ID: {uid}
┃ 👥 ریفیرل: {get_refs(uid)} / 10
┣━━━━━━━━━━━━━━━━━━━━━━━┫
🔗 لینک:
{ref_link}
┣━━━━━━━━━━━━━━━━━━━━━━━┫
⚡ 10 ریفیرل = نمبر
╰━━━━━━━━━━━━━━━━━━━━━━━╯"""

    q.edit_message_text(text)

# ================= NUMBER MENU =================
def numbers(update, context):
    q = update.callback_query
    uid = q.from_user.id

    if get_refs(uid) < 10:
        q.answer("❗ 10 ریفیرل پکار دی!", show_alert=True)
        return

    q.edit_message_text("⏳ انتظار وکړئ... نمبرونه درته راځي")

# ================= ADD GROUP =================
def addg(update, context):
    update.callback_query.message.reply_text("ګروپ username راولیږئ:")
    return 1

def saveg(update, context):
    uid = update.message.from_user.id
    group = update.message.text

    if get_refs(uid) < 10:
        update.message.reply_text("❗ 10 ریفیرل پکار دی!")
        return ConversationHandler.END

    try:
        m = context.bot.get_chat_member(group, context.bot.id)
        if m.status == "administrator":
            groups.append(group)

            # deduct referrals
            referrals[uid] = referrals.get(uid, [])[10:]

            update.message.reply_text("✅ ګروپ ثبت شو")
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

# ================= FORMAT USER =================
def user_msg(phone, time):
    return f"""╭━━━〔 💬 نـوی نـمـبـر 〕━━━╮
┃ 🌍 کوډ ➤ +??
┃ 💀 نمبر ➤ {phone[-6:]}
┃ ☠ مکمل ➤ {phone}
┃ ⏳ وخت ➤ {time}
╰━━━━━━━━━━━━━━━━━━╯"""

# ================= FORMAT GROUP =================
def group_msg(app, phone, msg, time):
    otp = "N/A"
    m = re.search(r"\d{4,8}", msg)
    if m:
        otp = m.group()

    return f"""📲 OTP راغی
App: {app}
Number: {phone}
Time: {time}
Code: {otp}
Msg: {msg}"""

# ================= MAIN JOB =================
def job(context):
    data = fetch()

    for i in data:
        app, phone, msg, time = i

        if phone in sent:
            continue

        sent.add(phone)

        # USERS
        for uid in users:
            if get_refs(uid) >= 10:
                try:
                    context.bot.send_message(uid, user_msg(phone, time))

                    # deduct referrals after sending
                    referrals[uid] = referrals.get(uid, [])[10:]

                except:
                    pass

        # GROUPS
        for g in groups:
            try:
                context.bot.send_message(g, group_msg(app, phone, msg, time))
            except:
                pass

        # ADMIN
        context.bot.send_message(ADMIN_ID, f"📊 NEW NUMBER\n{phone}")

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
    dp.add_handler(CallbackQueryHandler(check, pattern="check"))
    dp.add_handler(CallbackQueryHandler(numbers, pattern="numbers"))
    dp.add_handler(CallbackQueryHandler(account, pattern="account"))
    dp.add_handler(conv)

    up.job_queue.run_repeating(job, interval=10, first=5)

    up.start_polling()
    up.idle()

if __name__ == "__main__":
    main() 
