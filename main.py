import requests
import re
from telegram import *
from telegram.ext import *

================= CONFIG =================

BOT_TOKEN = "8628239633:AAG0SNJDxLzVrA6-tnb9hvA-HlwrqQ8NCtk"
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

================= STORAGE =================

users = {}
referrals = {}
groups = []
sent = set()

================= JOIN CHECK =================

def is_joined(bot, uid):
for ch in CHANNELS:
try:
m = bot.get_chat_member(ch, uid)
if m.status not in ["member", "administrator", "creator"]:
return False
except:
return False
return True

================= START =================

def start(update, context):
uid = update.effective_user.id

# referral  
if context.args:  
    ref = int(context.args[0])  
    if ref != uid:  
        referrals.setdefault(ref, [])  
        if uid not in referrals[ref]:  
            referrals[ref].append(uid)  

users.setdefault(uid, {"index": 0})  

kb = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]  
kb.append([InlineKeyboardButton("✅ چیک", callback_data="check")])  

update.message.reply_text("🔒 چینلونو کې ګډون وکړئ:", reply_markup=InlineKeyboardMarkup(kb))

================= CHECK =================

def check(update, context):
q = update.callback_query
uid = q.from_user.id

if is_joined(context.bot, uid):  
    kb = [  
        [InlineKeyboardButton("📱 نمبرونه", callback_data="numbers")],  
        [InlineKeyboardButton("👥 ګروف اضافه کول", callback_data="addg")]  
    ]  
    q.edit_message_text("✅ ښه راغلاست:", reply_markup=InlineKeyboardMarkup(kb))  
else:  
    q.answer("❌ Join وکړئ!", show_alert=True)

================= NUMBER MENU =================

def numbers(update, context):
q = update.callback_query
uid = q.from_user.id

if len(referrals.get(uid, [])) < 10:  
    q.answer("❗ 10 ریفیرل پکار دی!", show_alert=True)  
    return  

q.edit_message_text("⏳ انتظار وکړئ... نمبرونه درته راځي")

================= ADD GROUP =================

def addg(update, context):
update.callback_query.message.reply_text("ګروپ username راولیږئ:")
return 1

def saveg(update, context):
uid = update.message.from_user.id
group = update.message.text

try:  
    m = context.bot.get_chat_member(group, context.bot.id)  
    if m.status == "administrator":  
        groups.append(group)  

        if uid in referrals:  
            referrals[uid] = referrals[uid][10:]  

        update.message.reply_text("✅ ګروپ ثبت شو")  
    else:  
        update.message.reply_text("❌ بوت ادمین نه دی")  
except:  
    update.message.reply_text("❌ غلط ګروپ")  

return ConversationHandler.END

================= FETCH =================

def fetch():
try:
r = requests.get(API_URL, params={"token": API_TOKEN}, timeout=10)
return r.json() if isinstance(r.json(), list) else []
except:
return []

================= FORMAT USER =================

def user_msg(phone, time):
return f"""╭━━━〔 💬 نـوی نـمـبـر سـیـسـټـم 〕━━━╮
┃
┃  🌍 هیواد کوډ ➤ 【 +?? 】
┃  💀 نمبر ➤ 【 {phone[-6:]} 】
┃  ☠ مکمل نمبر ➤ 【 {phone} 】
┃  ⏳ وخت ➤ 【 {time} 】
┃
┣━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ⚡ زر استفاده وکړئ
┃  🚫 که ناوخته شي، بل څوک به یې واخلي
╰━━━━━━━━━━━━━━━━━━━━━━━╯"""

================= FORMAT GROUP =================

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

================= MAIN JOB =================

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
        if len(referrals.get(uid, [])) >= 10:  
            try:  
                context.bot.send_message(  
                    uid,  
                    user_msg(phone, time),  
                    reply_markup=InlineKeyboardMarkup([  
                        [InlineKeyboardButton("🔑 کوډ دلته", url="https://t.me/HematOTP")],  
                        [InlineKeyboardButton("📢 معلومات", url="https://t.me/ProTech43")]  
                    ])  
                )  
            except:  
                pass  

    # GROUPS  
    for g in groups:  
        try:  
            context.bot.send_message(  
                g,  
                group_msg(app, phone, msg, time),  
                reply_markup=InlineKeyboardMarkup([  
                    [InlineKeyboardButton("📢 زموږ چینل", url="https://t.me/ProTech43")],  
                    [InlineKeyboardButton("📲 نمبرونه", url="https://t.me/HematOtp1VBot")]  
                ])  
            )  
        except:  
            pass  

    # ADMIN  
    context.bot.send_message(ADMIN_ID, f"📊 NEW NUMBER\n{phone}")

================= BROADCAST =================

def broadcast(update, context):
if update.effective_user.id != ADMIN_ID:
return

text = " ".join(context.args)  

for u in users:  
    try:  
        context.bot.send_message(u, text)  
    except:  
        pass  

update.message.reply_text("✅ Broadcast Done")

================= ADMIN =================

def admin(update, context):
if update.effective_user.id != ADMIN_ID:
return

update.message.reply_text(  
    f"👑 ADMIN PANEL\nUsers: {len(users)}\nGroups: {len(groups)}\nNumbers: {len(sent)}"  
)

================= MAIN =================

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
dp.add_handler(CommandHandler("broadcast", broadcast))  

dp.add_handler(CallbackQueryHandler(check, pattern="check"))  
dp.add_handler(CallbackQueryHandler(numbers, pattern="numbers"))  
dp.add_handler(conv)  

up.job_queue.run_repeating(job, interval=10, first=5)  

up.start_polling()  
up.idle()

if name == "main":
main()
