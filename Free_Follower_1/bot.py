from difflib import SequenceMatcher
from discord.ext import commands
import subprocess
import threading
import aiofiles
import discord
import asyncio
import aiohttp
import random
import ctypes
import re
import os


ctypes.windll.kernel32.SetConsoleTitleW('follower')
token = ''   # Token
prefix = ';'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

administrators = [534743606976577547]   # Here the admin ids
privileged = [633472131052732446, 809108509928456232]
chat_channel = 842628663060987924   # Main chat
bots_channel = 842734484196687912   # Bot/Cmd chat
welcome_channel = 839440635001176096 #Welcome Channel
queue = []



def follower():
    while True:
        try:
            task, arg1, arg2 = queue.pop(0).split('-')
            subprocess.run([f'{task}', f'{arg1}', f'{arg2}'])
        except:
            pass

threading.Thread(target=follower).start()

@bot.event
async def on_ready():

    print(f'Servers: {len(bot.guilds)}')
    for guild in bot.guilds:
        print(guild.name)
        print(guild.id)
        print('Bot made by: ! €lean_$nipes#2272')
    print()
    # bot.loop.create_task(status())
    while True:
        members = sum([guild.member_count for guild in bot.guilds])
        activity = discord.Activity(type=discord.ActivityType.watching, name=f'{members} users! | ;help')
        await bot.change_presence(activity=activity)
        await asyncio.sleep(60)

@bot.event
async def on_member_join(member):
    channel = await bot.fetch_channel(welcome_channel)
    await channel.send(f'{member.mention} **Read this!**', delete_after=3)
    await member.send(f'{member.mention}\nEnjoy your stay at **Free Follower.**\n\nAfter you have **automatically been given access,** you can use my commands in `#bot`.\nMy prefix is: **;**.')


@bot.event
async def on_command_error(ctx, error: Exception):
    await ctx.message.delete()
    if ctx.channel.id == bots_channel:
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(color=16379747, description=f'{error}')
            await ctx.send(embed=embed, delete_after=30)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=16379747, description='You are missing arguments required to run this command!')
            await ctx.send(embed=embed, delete_after=30)
            ctx.command.reset_cooldown(ctx)
        elif 'You do not own this bot.' in str(error):
            embed = discord.Embed(color=16379747, description='You do not have permission to run this command!')
            await ctx.send(embed=embed, delete_after=30)
        else:
            print(str(error))
    else:
        try:
            await ctx.message.delete()
        except:
            pass


@bot.command()
async def help(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> ;help')
    await ctx.message.delete()
    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(color=16731983)
        embed.add_field(name='Help Menu', value='`;help` ```ini\n[+] Shows all accessible commands.```', inline=True)
        embed.add_field(name='Open Ticket', value='`;ticket` ```ini\n[+] Opens a private ticket.```', inline=True)
        embed.add_field(name='Close Ticket', value='`;close` ```ini\n[+] Closes your ticket```', inline=True)
        embed.add_field(name='Tasks', value='`;tasks` ```ini\n[+] Shows you the queue of tasks.```', inline=True)
        embed.add_field(name='Twitch Followers', value='`;tfollow [CHANNEL]` ```ini\n[+] Sends twitch followers to the specified channel.```', inline=True)
        embed.add_field(name='Roblox Templates', value='`;rget [Asset ID]` ```ini\n[+] Gets the template of the asset.```', inline=True)
        await ctx.send(embed=embed, delete_after=20)

@bot.command()
async def ticket(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> ;ticket')
    await ctx.message.delete()
    if ctx.channel.type != discord.ChannelType.private:
        channels = [str(x) for x in bot.get_all_channels()]
        if f'ticket-{ctx.author.id}' in str(channels):
            embed = discord.Embed(color=16731983, description='You already have a ticket open!')
            await ctx.send(embed=embed, delete_after=30)
        else:
            ticket_channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.id}')
            await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)
            await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
            embed = discord.Embed(color=16227196, description='Please enter the reason for this ticket, type `;close` if you want to close this ticket.')
            await ticket_channel.send(f'{ctx.author.mention}', embed=embed)
            await ctx.message.delete()

@bot.command()
async def close(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> ;close')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.name == f'ticket-{ctx.author.id}':
            await ctx.channel.delete()
        elif ctx.author.id in administrators and 'ticket' in ctx.channel.name:
            await ctx.channel.delete()
        else:
            embed = discord.Embed(color=16731983, description=f'You do not have permission to run this command!')
            await ctx.send(embed=embed, delete_after=30)

@bot.command()
async def tasks(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> ;tasks')
    await ctx.message.delete()
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            embed = discord.Embed(color=16227196, description=f'`{len(queue)}` tasks in the queue!')
            await ctx.send(embed=embed, delete_after=30)
        else:
            await ctx.message.delete()

tfollow_cooldown = [300]

@bot.command()
@commands.cooldown(1, 300, type=commands.BucketType.user)
async def tfollow(ctx, channel, amount: int=None):
    print(f'{ctx.author} | {ctx.author.id} -> ;tfollow {channel}')
    await ctx.message.delete()
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel or ctx.author.id in administrators:
            if str(channel.lower()) in tfollow_cooldown and ctx.author.id not in administrators:
                try:
                    await ctx.message.delete()
                except:
                    pass
            else:
                try:
                    if '-' in str(channel):
                        raise Exception

                    max_amount = 0
                    if ctx.author.id in administrators:
                        tfollow.reset_cooldown(ctx)
                        max_amount += 500
                    Beginner = discord.utils.get(ctx.guild.roles, name='Beginner Twitch')
                    if Beginner in ctx.author.roles:
                        max_amount += 100
                    Adv = discord.utils.get(ctx.guild.roles, name='Advanced Twitch')
                    if Adv in ctx.author.roles:
                        max_amount += 150
                    Expert = discord.utils.get(ctx.guild.roles, name='Expert Twitch')
                    if Expert in ctx.author.roles:
                        max_amount += 200

                    booster = discord.utils.get(ctx.guild.roles, name='Boosters')
                    if booster in ctx.author.roles:
                        max_amount += 200

                        max_amount += 225
                    _100 = discord.utils.get(ctx.guild.roles, name='+100')
                    if _100 in ctx.author.roles:
                        max_amount += 100
                    lvl300 = discord.utils.get(ctx.guild.roles, name='[LVL] +300')
                    if lvl300 in ctx.author.roles:
                        max_amount += 300
                    lvl200 = discord.utils.get(ctx.guild.roles, name='[LVL] +200')
                    if lvl200 in ctx.author.roles:
                        max_amount += 200
                    lvl100 = discord.utils.get(ctx.guild.roles, name='[LVL] +100')
                    if lvl100 in ctx.author.roles:
                        max_amount += 100
                    max_amount += 25
                    if amount is None:
                        amount = max_amount
                    elif amount > max_amount:
                        amount = max_amount
                    if amount <= max_amount:
                        premium = discord.utils.get(ctx.guild.roles, name='Premium')
                        if premium in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`1/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[+]** Sending `{amount}` followers to `{channel}`! (`1/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.insert(0, f'tfollow-{channel}-{amount}')
                        elif Beginner in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[BEGINNER]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        elif Adv in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[ADVANCED]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        elif Expert in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[EXPERT]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')

                        elif booster in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[BOOST]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')

                        elif _100 in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[+100]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        elif lvl300 in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[LVL BOOST] [+300]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        elif lvl200 in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[LVL BOOST] [+200]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        elif lvl100 in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[LVL BOOST] [+100]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                        else:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=10313212, description=f'**[+]** Sending `{amount}` followers to `{channel}`! (`{position}/{position}`)```ini\n[+] You can get EXTRA followers per command by inviting people, purchasing a plan or boosting the server!```', delete_after=3)
                            await ctx.send(embed=embed, delete_after=30)
                            queue.append(f'tfollow-{channel}-{amount}')
                        if ctx.author.id not in administrators:
                            tfollow_cooldown.append(str(channel.lower()))
                            await asyncio.sleep(600)
                            tfollow_cooldown.remove(str(channel.lower()))
                except:
                    embed = discord.Embed(color=16731983, description='**[-]** An unexpected error has been encountered. Please try this command again. If the issue persists, contact Inertia.', delete_after=3)
                    await ctx.send(embed=embed, delete_after=30)
                    tfollow.reset_cooldown(ctx)
        else:
            await ctx.message.delete()
            tfollow.reset_cooldown(ctx)


@bot.command()
async def rget(ctx, asset_id):
    print(f'{ctx.author} | {ctx.author.id} -> /rget {asset_id}')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}') as r:
                        r = await r.text()
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id=' + re.search('id=(.*)</url>', r).group(1)) as r:
                        r = await r.read()
                try:
                    f = await aiofiles.open(f'{asset_id}.png', mode='wb')
                    await f.write(r)
                    await f.close()
                    embed = discord.Embed(color=16379747)
                    file = discord.File(f'{asset_id}.png')
                    embed.set_image(url=f'attachment://{asset_id}.png')
                    await ctx.send(embed=embed, file=file, delete_after=30)
                finally:
                    try:
                        os.remove(f'{asset_id}.png')
                    except:
                        pass
            except:
                embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!', delete_after=3)
                await ctx.send(embed=embed, delete_after=30)
        else:
            await ctx.message.delete()


@bot.command()
@commands.cooldown(1, 600, type=commands.BucketType.user)
async def tspam(ctx, channel, *, msg):
    print(f'{ctx.author} | {ctx.author.id} -> ;tspam {channel} {msg}')
    if ctx.channel.type != discord.ChannelType.private:
        plat = discord.utils.get(ctx.guild.roles, name='Platin')
        if plat in ctx.author.roles:
            if ctx.channel.id == bots_channel:
                try:
                    max_amount = 1
                    if ctx.author.id in administrators:
                        tspam.reset_cooldown(ctx)
                    max_amount += 10
                    amount = None
                    if amount is None:
                        amount = max_amount
                    if amount <= max_amount:
                        position = len(queue) + 1
                        embed = discord.Embed(color=16379747, description=f'Added `tspam-{channel}-{msg}` to queue! (`1/{position}`)')
                        await ctx.send(embed=embed, delete_after=30)
                        queue.insert(0, f'tspam-{channel}-{msg}')
                except:
                    embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed, delete_after=30)
                    tspam.reset_cooldown(ctx)
            else:
                await ctx.message.delete()
                tspam.reset_cooldown(ctx)
        else:
            embed = discord.Embed(color=16379747, description='You do not have permission to run this command!', delete_after=3)
            await ctx.send(embed=embed, delete_after=30)




bot.run(token)
