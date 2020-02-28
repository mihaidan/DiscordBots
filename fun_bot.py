import discord
import urllib.request
import random
import os
import re

from google_images_download import google_images_download

TOKEN = ''

CWD = os.getcwd()

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return


    ####################
    ## Hello command
    ####################
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention} :wave:'.format(message)
        embed = discord.Embed(title='Greeting', description=msg, color=0x9925db)
        await client.send_message(message.channel, embed=embed)


    ####################
    ## Rick command
    ####################
    if message.content.startswith('!rick'):
        msg = urllib.request.urlopen('https://radiant-wildwood-67970.herokuapp.com/rick/').read()
        embed = discord.Embed(title='Rick', description=msg.decode('utf-8'), color=0x50eaa8)
        await client.send_message(message.channel, embed=embed)


    ####################
    ## Morty command
    ####################
    if message.content.startswith('!morty'):
        msg = urllib.request.urlopen('https://radiant-wildwood-67970.herokuapp.com/morty/').read()
        embed = discord.Embed(title='Morty', description=msg.decode('utf-8'), color=0x50eaa8)
        await client.send_message(message.channel, embed=embed)


    ####################
    ## Say Aloud command
    ####################
    if message.content.startswith('!sayaloud'):
        msg = message.content[len('!sayaloud'):].strip()

        if (msg != ''):
            intro = '{0.author.mention} says: '.format(message)
            new_msg = intro + '\''+ msg + '\''
            await client.send_message(message.channel, new_msg, tts=True)
        else:
            msg = 'No message to say out loud.'
            embed = discord.Embed(title='Say Aloud Error :octagonal_sign:', description=msg, color=0xe10000)
            await client.send_message(message.channel, embed=embed)


    ####################
    ## Google Pic command
    ####################
    if message.content.startswith('!pic'):
        msg = message.content[len('!pic'):].strip()

        if (msg != ''):

            response = google_images_download.googleimagesdownload()
            arguments = {'keywords':msg,'limit':1,'format':'jpg'}   #creating list of arguments
            
            response.download(arguments)

            path = CWD + '/downloads/' + msg + '/'

            for f in os.listdir(CWD + '/downloads/' + msg + '/'):
                if re.match('1.', f):
                    pic_path = path + f
                    await client.send_file(message.channel, pic_path, filename=msg+'.jpg')
                    os.remove(pic_path)
                else:
                    msg = 'Something went wrong :/'
                    embed = discord.Embed(title='Google Pic Error :octagonal_sign:', description=msg, color=0xe10000)
                    await client.send_message(message.channel, embed=embed)

            os.rmdir(path)
        else:
            msg = 'No terms to search.'
            embed = discord.Embed(title='Google Pic Error :octagonal_sign:', description=msg, color=0xe10000)
            await client.send_message(message.channel, embed=embed)


    ####################
    ## Odds command
    ####################
    if message.content.startswith('!odds'):
        num_str = message.content[len('!odds'):].strip()
        num_list = num_str.split()

        if (len(num_list) == 2):
            bot_num = int(num_list[0])
            user_num = int(num_list[1])

            if (user_num <= bot_num):
                od = random.randint(0,bot_num)
                intro = 'Odds = '+str(bot_num)+'\n'

                p1 = '{0.author.mention}: '.format(message)+str(user_num)+'\n'
                p2 = 'Bot: '+str(od)+'\n'

                if (user_num == od):
                    rest = 'You **won\'t**.'
                else:
                    rest = 'Damn.'

                msg = p1 + p2 + rest
                embed = discord.Embed(title=intro, description=msg, color=0x58b3ea)
                await client.send_message(message.channel, embed=embed)
            else:
                msg = 'Your guess cannot exceed the limit.'
                embed = discord.Embed(title='Odds Error :octagonal_sign:', description=msg, color=0xe10000)
                await client.send_message(message.channel, embed=embed)
        else:
            msg = 'Please use the correct format: \"!odds *-limit* *-guess*\"'
            embed = discord.Embed(title='Odds *Error*', description=msg, color=0xe10000)
            await client.send_message(message.channel, embed=embed)


    ####################
    ## Commands command
    ####################
    if message.content.startswith('!help'):
        intro    = 'Help'
        hello    = '!hello\n'
        rick     = '!rick\n'
        morty    = '!morty\n'
        odds     = '!odds -limit -guess\n'
        sayaloud = '!sayaloud -message\n'
        pic      = '!pic -term(s)'

        embed = discord.Embed(title=intro, description='Available commands.', color=0x58b3ea)
        embed.add_field(name=hello, value='Greeting', inline=False)
        embed.add_field(name=rick, value='Randomly generated Rick quote', inline=False)
        embed.add_field(name=morty, value='Randomly generated Morty quote', inline=False)
        embed.add_field(name=odds, value='You won\'t.', inline=False)
        embed.add_field(name=sayaloud, value='Says any message out loud', inline=False)
        embed.add_field(name=pic, value='Searches google for an image based on the input term', inline=False)

        await client.send_message(message.channel, embed=embed)


@client.event
async def on_ready():
    #await client.change_nickname(nickname='NotNotBot')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
