# py_DiscordBot
# Discord bot in Python. It contains several commands: moderation, fun and management.
# https://t.me/iiYuzio | https://t.me/iiYuzioWorks

import discord
import random
import requests
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("» Bot Online Correctly!")

# Moderation Package - V1

# Ban Command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.author.top_role <= member.top_role:
        await ctx.send(embed=discord.Embed(description="» You do not have permission to ban this user.", color=discord.Color.red()))
        return
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title=f"Member Banned: {member}", color=discord.Color.red())
        embed.add_field(name="Moderator", value=ctx.author)
        if reason:
            embed.add_field(name="Reason", value=reason)
        await ctx.send(embed=embed)
    except discord.errors.Forbidden:
        await ctx.send(embed=discord.Embed(description="» I do not have permission to ban this user.", color=discord.Color.red()))

# Mute Command
@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    if ctx.author.top_role <= member.top_role:
        return await ctx.send("» You do not have permission to mute this user.")
        
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
            
    await member.add_roles(muted_role, reason=reason)

    embed = discord.Embed(
        title=f"{member} has been muted from the server.",
        colour=discord.Colour.orange(),
        description=f"Reason: {reason}"
    )

    await ctx.send(embed=embed)

# Tempban Command
@bot.command()
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: discord.Member, time: int, unit: str, *, reason=None):
    units = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
        "months": 2592000
    }
    
    if unit not in units:
        await ctx.send(f"» Invalid time unit. Please choose one of the following: {', '.join(units.keys())}")
        return

    duration = units[unit] * time
    end_time = datetime.utcnow() + timedelta(seconds=duration)

    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned for {time} {unit} for {reason or 'no reason specified'}")

    embed = discord.Embed(title=f"{member} has been banned", description=f"Reason: {reason or 'no reason specified'}", color=0xff0000)
    embed.add_field(name="Duration", value=f"{time} {unit}")
    embed.add_field(name="End Time (UTC)", value=end_time.strftime("%Y-%m-%d %H:%M:%S"))

    await ctx.send(embed=embed)

    await asyncio.sleep(duration)
    await member.unban(reason="Temporary ban expired")

# Tempmute Command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, duration: int, duration_type: str, *, reason=None):
    if duration_type not in ["seconds", "minutes", "hours", "days"]:
        await ctx.send("» Invalid duration type! Please use seconds, minutes, hours, or days.")
        return

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)

    await member.add_roles(mute_role, reason=reason)

    if duration_type == "seconds":
        await asyncio.sleep(duration)
    elif duration_type == "minutes":
        await asyncio.sleep(duration * 60)
    elif duration_type == "hours":
        await asyncio.sleep(duration * 60 * 60)
    elif duration_type == "days":
        await asyncio.sleep(duration * 60 * 60 * 24)

    await member.remove_roles(mute_role, reason="Tempmute expired.")
    await ctx.send(embed=discord.Embed(title="Member Tempmuted", description=f"{member.mention} has been temporarily muted for {duration} {duration_type}. Reason: {reason}", color=discord.Color.blue()))

# Kick Command
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.kick_members:
        if member.top_role.position < ctx.author.top_role.position:
            if reason is not None:
                embed = discord.Embed(title=f"{member} kicked", description=f"Reason: {reason}", color=0xFF5733)
            else:
                embed = discord.Embed(title=f"{member} kicked", description="No reason provided", color=0xFF5733)
            await member.kick(reason=reason)
            await ctx.send(embed=embed)
        else:
            await ctx.send("» You cannot kick someone with a higher or equal role.")
    else:
        await ctx.send("» You don't have permission to use this command.")

# Clear Command
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"Deleted {amount} messages", delete_after=5)

# Fun Package - V1

# Coinflip Command
@bot.command()
async def coinflip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    embed = discord.Embed(title="Coinflip", description=f"The coin landed on **{coin}**!", color=0x00ff00)
    await ctx.send(embed=embed)

# Roll Command
@bot.command(name='roll')
async def roll(ctx, faces: int):
    if faces < 2:
        await ctx.send("The dice must have at least 2 faces.")
    else:
        roll_result = random.randint(1, faces)
        await ctx.send(f"You rolled a {roll_result} out of {faces} possible faces.")

# Roasts Command
roasts = [
    "I'd call you a tool, but even they serve a purpose.",
    "I'm not saying you're dumb, but you have a lot of bad luck when it comes to thinking.",
    "I'd give you a nasty look, but you've already got one.",
    "You're the reason they invented the word \"idiot.\"",
    "I'd like to help you out, which way did you come in?",
    "You're not pretty enough to be this stupid.",
    "I'm not insulting you, I'm describing you.",
    "You're so dense, light bends around you.",
    "You're the human equivalent of a participation award.",
    "I'd tell you to go to hell, but I work there and don't want to see you every day."
]

@bot.command(name='roast')
async def roast_command(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send('Please specify a user to roast.')
    else:
        roast = random.choice(roasts)
        await ctx.send(f"{user.mention}, {roast}")

# Meme Command
@bot.command(name='meme')
async def meme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    data = response.json()
    embed = discord.Embed(title='Meme', color=0xff8000)
    embed.set_image(url=data['image'])
    await ctx.send(embed=embed)


bot.run('YOUR_TOKEN_BOT')
