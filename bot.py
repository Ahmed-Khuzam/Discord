import discord
from discord.ext import commands, tasks
from datetime import datetime

TOKEN = "MTM2MDMyNTMwNDc2MTE4ODY4NA.G0cQ8p.io66f3UV3rQOyg-t-lDkvCmR-6hh7lzsA78OQ0"
PREFIX = "!"
BOT_OWNER_ID = 866442447689089095

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

whitelist = {}
mods = set()
user_status = {}
control_panel_msg = None

design = {
    "colors": {
        "primary": 0x5865F2,
        "success": 0x57F287,
        "error": 0xED4245,
        "warning": 0xFEE75C
    },
    "emojis": {
        "online": "🟢",
        "offline": "🔴",
        "idle": "🌙",
        "dnd": "⛔️",
        "settings": "⚙️",
        "Ag": "❕",
        "og": "✔️"
    }
}

@bot.event
async def on_ready():
    print(f"{design['emojis']['settings']} {bot.user} يعمل الآن!")
    update_statuses.start()

@tasks.loop(minutes=1)
async def update_statuses():
    guild = bot.guilds[0]
    await guild.chunk()
    for user_id in whitelist:
        member = guild.get_member(user_id)
        if member:
            status = str(member.status)
            emoji = design["emojis"].get(status, design["emojis"]["offline"])
            user_status[user_id] = f"{emoji} {status}"
    await update_control_panel()

async def update_control_panel():
    global control_panel_msg
    guild = bot.guilds[0]
    description = f"**{design['emojis']['settings']} السجل: ({len(whitelist)})**\n\n"
    for user_id in whitelist:
        member = guild.get_member(user_id)
        if member:
            status = user_status.get(user_id, f"{design['emojis']['offline']} غير متصل")
            display_name = member.nick or member.name
            description += f"**{display_name}:** {status}\n"
    embed = discord.Embed(
        title=f"{design['emojis']['settings']} سجل البيانات",
        description=description,
        color=design["colors"]["primary"]
    )
    embed.set_footer(text=f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if control_panel_msg:
        await control_panel_msg.edit(embed=embed)

@bot.command()
async def send(ctx):
    if not is_admin(ctx.author):
        return await error_reply(ctx, "صلاحيات غير كافية", "هذا الأمر متاح فقط للمشرفين")
    guild = ctx.guild
    description = f"**{design['emojis']['Ag']} السجل: ({len(whitelist)})**\n\n"
    for user_id in whitelist:
        member = guild.get_member(user_id)
        if member:
            status = user_status.get(user_id, f"{design['emojis']['offline']} غير متصل")
            display_name = member.nick or member.name
            description += f"**{display_name}:** {status}\n"
    embed = discord.Embed(
        title=f"{design['emojis']['settings']} لوحة البيانات",
        description=description,
        color=design["colors"]["primary"]
    )
    embed.set_footer(text=f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    global control_panel_msg
    control_panel_msg = await ctx.send(embed=embed)

@bot.command()
async def mod(ctx, member: discord.Member = None):
    if not (ctx.author.id == BOT_OWNER_ID or ctx.author.id == ctx.guild.owner_id):
        return await error_reply(ctx, "صلاحيات غير كافية", "هذا الأمر متاح فقط للمالك أو مالك السيرفر")
    if not member:
        return await error_reply(ctx, "مستخدم غير محدد", "الاستخدام: `!mod @المستخدم`")
    mods.add(member.id)
    await success_reply(ctx, "ترقية مشرف", f"تم منح {member.mention} صلاحيات المشرف")

@bot.command()
async def unmod(ctx, member: discord.Member = None):
    if not (ctx.author.id == BOT_OWNER_ID or ctx.author.id == ctx.guild.owner_id):
        return await error_reply(ctx, "صلاحيات غير كافية", "هذا الأمر متاح فقط للمالك أو مالك السيرفر")
    if not member:
        return await error_reply(ctx, "مستخدم غير محدد", "الاستخدام: `!unmod @المستخدم`")
    mods.discard(member.id)
    await success_reply(ctx, "إزالة صلاحيات", f"تم إزالة صلاحيات المشرف من {member.mention}")

@bot.command()
async def add(ctx, member: discord.Member = None):
    if not (ctx.author.id == BOT_OWNER_ID or ctx.author.id == ctx.guild.owner_id or ctx.author.id in mods):
        return await error_reply(ctx, "صلاحيات غير كافية", "هذا الأمر متاح فقط للمشرفين")
    if not member:
        return await error_reply(ctx, "مستخدم غير محدد", "الاستخدام: `!add @المستخدم`")
    whitelist[member.id] = {"added_by": ctx.author.id, "date": datetime.now()}
    await success_reply(ctx, "إضافة عضو", f"تم إضافة {member.mention} إلى النظام")
    await update_control_panel()

@bot.command()
async def delete(ctx, member: discord.Member = None):
    target = member or ctx.author
    if target.id not in whitelist:
        return await error_reply(ctx, "غير مسجل", f"{target.mention} غير موجود في النظام")
    del whitelist[target.id]
    user_status.pop(target.id, None)
    await success_reply(ctx, "حذف عضو", f"تم حذف {target.mention} من النظام")
    await update_control_panel()

def is_admin(user):
    return user.id in mods or user.id == BOT_OWNER_ID

async def success_reply(ctx, title, description):
    embed = discord.Embed(title=title, description=description, color=design["colors"]["success"])
    await ctx.send(embed=embed)

async def error_reply(ctx, title, description):
    embed = discord.Embed(title=title, description=description, color=design["colors"]["error"])
    await ctx.send(embed=embed)

bot.run(TOKEN)
