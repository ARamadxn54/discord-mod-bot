import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import random
from discord_slash import SlashCommand
import json
from datetime import date
import time
import requests

def getCryptoPrices(id):
    coingecko = f'https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd'
    r = requests.get(url=coingecko)
    data = r.json()
    return data

client = commands.Bot(command_prefix='!')
slash = SlashCommand(client, sync_commands=True)

THRESHOLD = 10
m = []
time_ = time.time()

def antijoin(member):
    global m
    global time_
    m.append(member)
    if time.time() - time_ >= 15.0:
        time_ = time.time()
        if len(m) >= THRESHOLD:
            return True
        else:
            return False
        m = []

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Hello There!'))
    print('Bot is Live')

@client.event
async def on_member_join(member):
    bool_ = antijoin(member)
    print('Raid state: %s' % bool_)

#Gets Current Price of a coin from CoinGeeko API (!price {coin})
@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    if message.content.startswith('!price'):
        id = message.content.split(' ')[1]
        price = getCryptoPrices(id)
        await message.channel.send(f'The price of {id} is {price[id]["usd"]} USD')

@slash.slash(name='clear',description='clears the last 20 messages')
async def clear(ctx, amount = 20):
    if(not ctx.author.guild_permissions.manage_messages):
        await ctx.send("You Don't have permission to use this command")
        return
    await ctx.channel.purge(limit = amount)
    await ctx.send('Messages Cleared')

@slash.slash(name='kick', description='kicks a user')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, *, reason = None):
    if(not ctx.author.guild_permissions.kick_members):
        await ctx.send("You Don't have permission to use this command")
        return

    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked')

@slash.slash(name='ban', description='bans a user')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason = None):
    if(not ctx.author.guild_permissions.ban_members):
        await ctx.send("You Don't have permission to use this command")
        return

    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned')

@slash.slash(name='unban', description='unbans a user')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    if(not ctx.author.guild_permissions.ban_members):
        await ctx.send("You Don't have permission to use this command")
        return
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@slash.slash(name='mute', description='mutes the user')
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason = None):
    if(not ctx.author.guild_permissions.manage_messages):
        await ctx.send("You Don't have permission to use this command")
        return

    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name = 'Muted')

    if not mutedRole:
        mutedRole = await guild.create_role(name = 'Muted')

        for channel in guild.channels:
            await ctx.send('No muted role found. Creating Muted role...')
            await channel.set_permissions(mutedRole, speak = False, send_messages = False, read_message_history = True, read_messages = True)
        await member.add_roles(mutedRole, reason=reason)
        await ctx.send('User is muted')
        await member.send(f'You have been muted from **{guild.name}** | Reason: **{reason}**')

@slash.slash(name='unmute', description='unmutes the user')
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member, *, reason = None):
    if(not ctx.author.guild_permissions.manage_messages):
        await ctx.send("You Don't have permission to use this command")
        return

    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name = 'Muted')

    if not mutedRole:
        await ctx.send('The muted role has not been found.')
        return

    await member.remove_roles(mutedRole, reason=reason)
    await ctx.send('User is unmuted')
    await member.send(f'You have been unmuted from **{guild.name}** | Reason: **{reason}**')

@slash.slash(name='addrole', description='adds a role to a user')
@commands.has_permissions(manage_guild = True)
async def addrole(ctx, member: discord.Member, *, role: discord.Role = None):
    if member == None:
        await ctx.send('Please specify a member')

    if role == None:
        await ctx.send('Please specify a role')

    await member.add_roles(role)
    await ctx.send(f'{member} was given the {role} role')

@slash.slash(name='removerole', description='removes a role from a user')
@commands.has_permissions(manage_guild = True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role = None):
    if member == None:
        await ctx.send('Please specify a member')

    if role == None:
        await ctx.send('Please specify a role')

    await member.remove_roles(role)
    await ctx.send(f'{member} has lost the {role} role')

@slash.slash(name = 'lockdown', description='locks a channel')
@commands.has_permissions(manage_channels = True)
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send( ctx.channel.mention + " ***is now in lockdown.***")

@slash.slash(name = 'unlock', description='unlocks a channel')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(ctx.channel.mention + " ***has been unlocked.***")

@slash.slash(name='warn', description='Sends a warning embed directly to the user')
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason):
      dm = await client.fetch_user(member.id)
      embed = discord.Embed(title="Warning", description=f"Server: {ctx.guild.id}\nReason: {reason}")
      await dm.send(embed=embed)
      await ctx.send('Warning has been sent')

@slash.slash(name='nuke', description='nukes a channel')
@commands.has_permissions(ban_members=True)
async def nuke(ctx):
    embed = discord.Embed(
        colour=0x00ff00,
        title=f":boom: Channel ({ctx.channel.name}) has been nuked :boom:",
        description=f"Nuked by: {ctx.author.name}#{ctx.author.discriminator}"
    )
    embed.set_footer(text = f'{ctx.guild.name} | {date.today()}')
    await ctx.channel.delete(reason="nuke")

@slash.slash(name='report', description='reports a user')
async def report(ctx, member: discord.Member, *, report = None):
    report_channel = discord.utils.get(ctx.guild.channels, name = 'reports')

    if member is None:
        return await ctx.send('Please include a user to report')

    if report is None:
        return await ctx.send('Please include a reason')
    else:
        embed = discord.Embed(title = 'REPORT', description = f'{ctx.author.mention} has reported {member}')
        embed.set_thumbnail(url = '')
        embed.add_field(name ='More info', value=f'{report}')
        embed.set_footer(icon_url=ctx.author.avatar_url, text = 'React with the ✅ if it has been resolved')
        report_message = await report_channel.send(embed = embed)
        await report_message.add_reaction('✅')
        await ctx.reply(f'{ctx.author.mention} Your report has veen sent to the staff team')

        try:
            def check(reaction, member):
                return member == ctx.author and str(reaction.emoji) in ['✅']

            reaction,member = await client.wait_for('reaction_add', timeout=604800, check=check)

            if str(reaction.emoji) == '✅':
                await ctx.send('Your report has been resolved')

        except Exception as e:
            print(e)

client.run('OTQwNjA5MjU2MzI2MDcwMzYz.YgJ4og.VfLA1lG5vy-tjhlydLQOFz6JXgk')