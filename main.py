import requests
import time
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import re

# ---------------- CONFIG ----------------
API_URL = "http://147.135.212.197/crapi/st/viewstats"
TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="
params = {"token": TOKEN, "records": ""}

TELEGRAM_BOT_TOKEN = "8628239633:AAG0SNJDxLzVrA6-tnb9hvA-HlwrqQ8NCtk"
TELEGRAM_GROUP_ID = -1003819384817

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ---------------- FUNCTIONS ----------------

def escape_v2(text):
    chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in chars else c for c in str(text)])

def fetch_sms():
    try:
        r = requests.get(API_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print("API ERROR:", e)
        return []

def parse_time(t):
    try:
        return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    except:
        return None

# ---------------- FULL COUNTRY MAP ----------------

country_map = {
    "1": ("United States", "🇺🇸"),
    "7": ("Russia", "🇷🇺"),
    "20": ("Egypt", "🇪🇬"),
    "27": ("South Africa", "🇿🇦"),
    "30": ("Greece", "🇬🇷"),
    "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"),
    "33": ("France", "🇫🇷"),
    "34": ("Spain", "🇪🇸"),
    "36": ("Hungary", "🇭🇺"),
    "39": ("Italy", "🇮🇹"),
    "40": ("Romania", "🇷🇴"),
    "41": ("Switzerland", "🇨🇭"),
    "43": ("Austria", "🇦🇹"),
    "44": ("United Kingdom", "🇬🇧"),
    "45": ("Denmark", "🇩🇰"),
    "46": ("Sweden", "🇸🇪"),
    "47": ("Norway", "🇳🇴"),
    "48": ("Poland", "🇵🇱"),
    "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"),
    "52": ("Mexico", "🇲🇽"),
    "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"),
    "55": ("Brazil", "🇧🇷"),
    "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"),
    "58": ("Venezuela", "🇻🇪"),
    "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"),
    "62": ("Indonesia", "🇮🇩"),
    "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"),
    "65": ("Singapore", "🇸🇬"),
    "66": ("Thailand", "🇹🇭"),
    "81": ("Japan", "🇯🇵"),
    "82": ("South Korea", "🇰🇷"),
    "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"),
    "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"),
    "93": ("Afghanistan", "🇦🇫"),
    "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"),
    "98": ("Iran", "🇮🇷"),
    "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco", "🇲🇦"),
    "213": ("Algeria", "🇩🇿"),
    "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"),
    "220": ("Gambia", "🇬🇲"),
    "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"),
    "223": ("Mali", "🇲🇱"),
    "224": ("Guinea", "🇬🇳"),
    "225": ("Ivory Coast", "🇨🇮"),
    "226": ("Burkina Faso", "🇧🇫"),
    "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"),
    "229": ("Benin", "🇧🇯"),
    "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"),
    "232": ("Sierra Leone", "🇸🇱"),
    "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"),
    "235": ("Chad", "🇹🇩"),
    "236": ("Central African Republic", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"),
    "238": ("Cape Verde", "🇨🇻"),
    "239": ("Sao Tome and Principe", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"),
    "241": ("Gabon", "🇬🇦"),
    "242": ("Congo", "🇨🇬"),
    "243": ("DR Congo", "🇨🇩"),
    "244": ("Angola", "🇦🇴"),
    "248": ("Seychelles", "🇸🇨"),
    "249": ("Sudan", "🇸🇩"),
    "250": ("Rwanda", "🇷🇼"),
    "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"),
    "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"),
    "256": ("Uganda", "🇺🇬"),
    "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"),
    "261": ("Madagascar", "🇲🇬"),
    "262": ("Reunion", "🇷🇪"),
    "263": ("Zimbabwe", "🇿🇼"),
    "264": ("Namibia", "🇳🇦"),
    "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"),
    "267": ("Botswana", "🇧🇼"),
    "268": ("Eswatini", "🇸🇿"),
    "269": ("Comoros", "🇰🇲"),
    "290": ("Saint Helena", "🇸🇭"),
    "291": ("Eritrea", "🇪🇷"),
    "297": ("Aruba", "🇦🇼"),
    "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"),
    "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"),
    "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"),
    "356": ("Malta", "🇲🇹"),
    "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"),
    "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"),
    "372": ("Estonia", "🇪🇪"),
    "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"),
    "376": ("Andorra", "🇦🇩"),
    "377": ("Monaco", "🇲🇨"),
    "378": ("San Marino", "🇸🇲"),
    "380": ("Ukraine", "🇺🇦"),
    "381": ("Serbia", "🇷🇸"),
    "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"),
    "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia and Herzegovina", "🇧🇦"),
    "389": ("North Macedonia", "🇲🇰"),
    "420": ("Czech Republic", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"),
    "423": ("Liechtenstein", "🇱🇮"),
    "500": ("Falkland Islands", "🇫🇰"),
    "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"),
    "503": ("El Salvador", "🇸🇻"),
    "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"),
    "506": ("Costa Rica", "🇨🇷"),
    "507": ("Panama", "🇵🇦"),
    "509": ("Haiti", "🇭🇹"),
    "590": ("Guadeloupe", "🇬🇵"),
    "591": ("Bolivia", "🇧🇴"),
    "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"),
    "594": ("French Guiana", "🇬🇫"),
    "595": ("Paraguay", "🇵🇾"),
    "596": ("Martinique", "🇲🇶"),
    "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"),
    "670": ("Timor-Leste", "🇹🇱"),
    "673": ("Brunei", "🇧🇳"),
    "674": ("Nauru", "🇳🇷"),
    "675": ("Papua New Guinea", "🇵🇬"),
    "676": ("Tonga", "🇹🇴"),
    "677": ("Solomon Islands", "🇸🇧"),
    "678": ("Vanuatu", "🇻🇺"),
    "679": ("Fiji", "🇫🇯"),
    "680": ("Palau", "🇵🇼"),
    "681": ("Wallis and Futuna", "🇼🇫"),
    "682": ("Cook Islands", "🇨🇰"),
    "685": ("Samoa", "🇼🇸"),
    "686": ("Kiribati", "🇰🇮"),
    "687": ("New Caledonia", "🇳🇨"),
    "688": ("Tuvalu", "🇹🇻"),
    "689": ("French Polynesia", "🇵🇫"),
    "691": ("Micronesia", "🇫🇲"),
    "692": ("Marshall Islands", "🇲🇭"),
    "850": ("North Korea", "🇰🇵"),
    "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"),
    "856": ("Laos", "🇱🇦"),
    "880": ("Bangladesh", "🇧🇩"),
    "886": ("Taiwan", "🇹🇼"),
    "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"),
    "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"),
    "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"),
    "971": ("UAE", "🇦🇪"),
    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"),
    "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"),
    "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
}

# ---------------- LOOP ----------------

last_seen_time = None
print("✅ BOT RUNNING...")

while True:
    entries = fetch_sms()

    if not entries:
        time.sleep(40)
        continue

    new_entries = []

    if last_seen_time is None:
        new_entries = entries[:5]
        if new_entries:
            last_seen_time = parse_time(new_entries[0][3])
    else:
        for e in entries:
            t = parse_time(e[3])
            if t and t > last_seen_time:
                new_entries.append(e)

    for entry in new_entries[::-1]:
        app, phone, msg, t = entry

        clean = phone.replace("+", "")
        code = ""

        for c in sorted(country_map.keys(), key=len, reverse=True):
            if clean.startswith(c):
                code = c
                break

        country, flag = country_map.get(code, ("Unknown", "🌍"))

        otp = "N/A"
        m = re.search(r'\b(\d{4,8})\b', msg)
        if m:
            otp = m.group(1)

        text = f"📩 {app}\n🌍 {country} {flag}\n📱 {phone}\n🔑 OTP: {otp}\n📝 {msg}"

        try:
            bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=text)
            print("Sent:", otp)
        except Exception as e:
            print("Error:", e)

    time.sleep(40) 
