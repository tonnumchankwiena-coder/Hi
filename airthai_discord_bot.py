import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import logging

# ===== ตั้งค่า =====
BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"

LOG_CHANNEL_ID = 1477605018008817736
SPECIAL_ROLE_ID = 1477602425190879345

# ===== intents =====
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

pending = {}

# ===== rules =====
@bot.tree.command(name="rules", description="แสดงกฎของเซิร์ฟเวอร์ AIRTHAI")
async def rules(interaction: discord.Interaction):

    embed = discord.Embed(
        title="กฎของเซิร์ฟเวอร์ AIRTHAI",
        color=0x2b6cff
    )

    embed.add_field(
        name="กฎ",
        value=
        "1. ห้ามด่าหรือเหยียดสมาชิก\n"
        "2. ห้ามสแปม\n"
        "3. ห้ามโฆษณา\n"
        "4. ฟังคำสั่งแอดมิน\n"
        "5. เคารพสมาชิกทุกคน",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# ===== tiktok =====
@bot.tree.command(name="tiktok", description="แจ้งลงคลิป TikTok")
async def tiktok(interaction: discord.Interaction, link: str, image: str):

    role_ping = f"<@&{SPECIAL_ROLE_ID}>"

    embed = discord.Embed(
        title="🎬 คลิปใหม่จาก AIRTHAI",
        description=f"[กดดูคลิป]({link})",
        color=0xff0050
    )

    embed.set_image(url=image)
    embed.set_footer(text=f"โพสต์โดย {interaction.user}")

    await interaction.channel.send(role_ping, embed=embed)
    await interaction.response.send_message("ประกาศคลิปแล้ว", ephemeral=True)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        log = discord.Embed(title="TIKTOK LOG", color=0xaaaaaa)
        log.add_field(name="User", value=str(interaction.user))
        log.add_field(name="Link", value=link)

        await log_channel.send(embed=log)

# ===== สมัคร =====
class RegisterView(View):

    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="เพราะชอบเซิร์ฟเวอร์", style=discord.ButtonStyle.primary)
    async def answer1(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message("ไม่ใช่ปุ่มของคุณ", ephemeral=True)
            return

        pending[self.user_id] = ["ชอบเซิร์ฟเวอร์"]

        view = RegisterView2(self.user_id)

        await interaction.response.send_message(
            "คำถามที่ 2 : ยอมรับกฎของเซิร์ฟเวอร์ไหม",
            view=view,
            ephemeral=True
        )


class RegisterView2(View):

    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="ยอมรับ", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message("ไม่ใช่ปุ่มของคุณ", ephemeral=True)
            return

        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(SPECIAL_ROLE_ID)

        pending[self.user_id].append("ยอมรับกฎ")

        if role:
            await member.add_roles(role)

        await interaction.response.send_message(
            "คุณได้รับบทบาท 👑สมาชิกพิเศษ👑 แล้ว",
            ephemeral=True
        )

        answers_text = "\n".join(pending[self.user_id])

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            embed = discord.Embed(title="REGISTER LOG", color=0xffd700)

            embed.add_field(
                name="User",
                value=f"{member} ({member.id})",
                inline=False
            )

            embed.add_field(
                name="Answers",
                value=answers_text,
                inline=False
            )

            await log_channel.send(embed=embed)

        del pending[self.user_id]


# ===== command สมัคร =====
@bot.tree.command(name="สมัคร", description="สมัครสมาชิกพิเศษ")
async def register(interaction: discord.Interaction):

    view = RegisterView(interaction.user.id)

    await interaction.response.send_message(
        "คำถามที่ 1 : ทำไมอยากเป็นสมาชิกพิเศษ",
        view=view,
        ephemeral=True
    )


# ===== start =====
@bot.event
async def on_ready():

    print(f"Bot Online : {bot.user}")

    await bot.tree.sync()


bot.run(BOT_TOKEN)
