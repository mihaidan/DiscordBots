import discord
import requests
import random
import os
import re
import datetime
import matplotlib.pyplot as plt

import pandas as pd

from google_images_download import google_images_download

# CLIENT ID: 555922053040046082

TOKEN = 'NTU1OTIyMDUzMDQwMDQ2MDgy.D2yOyg.1rBqZUrXQ183is4SH5Yao5oUR88'

base_url = 'https://api.iextrading.com/1.0'

CWD = os.getcwd()

client = discord.Client()

def get_symbol_by_period(ticker, period='1y'):
    url =  f'{base_url}/stock/{ticker}/chart/{period}'
    return requests.get(url)

def get_market():
    return requests.get(f'{base_url}/market')

def chart(ticker, period='1d'):
    cols = ['date', 'high', 'low', 'close', 'open']
    cols1 = ['minute', 'marketAverage', 'marketHigh', 'marketLow']
    url =  f'{base_url}/stock/{ticker}/chart/{period}'

    res = requests.get(url)

    if period == '1d':
        df = pd.read_json(res.content)[cols1]
        x = df['minute']
        df = df[df[cols1] > 0]
        avg = df['marketAverage']
        high = df['marketHigh']
        low = df['marketLow']

        fig, ax = plt.subplots()
        plt.plot(x, avg, label='average', color='blue')
        plt.xlabel('minute')
        plt.ylabel('price')
        plt.title(f'{ticker} average price over today')
        plt.legend()
        plt.xticks(rotation=45)
        for n, label in enumerate(ax.xaxis.get_ticklabels()):
            if n % 30 != 0:
                label.set_visible(False)
        plt.savefig(f'{CWD}/downloads/{ticker}.jpg')

        fig, ax = plt.subplots()
        plt.plot(x, high, label='high', color='green')
        plt.plot(x, low, label='low', color='red')
        plt.xlabel('minute')
        plt.ylabel('price')
        plt.title(f'{ticker} price over today')
        plt.legend()
        plt.xticks(rotation=45)
        for n, label in enumerate(ax.xaxis.get_ticklabels()):
            if n % 30 != 0:
                label.set_visible(False)
        plt.savefig(f'{CWD}/downloads/{ticker}hl.jpg')

    else:
        df = pd.read_json(res.content)[cols]
        x = df['date']

        c = ['high', 'low', 'close', 'open']
        df = df[df[c] > 0]
        high = df['high']
        low = df['low']
        open_ = df['open']
        close = df['close']

        plt.plot(x, close, label='close', color='blue')
        plt.plot(x, open_, label='open', color='orange')
        plt.xlabel('date')
        plt.ylabel('price')
        plt.title(f'{ticker} price over {period}')
        plt.legend()
        plt.xticks(rotation=45)
        plt.savefig(f'{CWD}/downloads/{ticker}.jpg')

        fig, ax = plt.subplots()
        plt.plot(x, high, label='high', color='green')
        plt.plot(x, low, label='low', color='red')
        plt.xlabel('date')
        plt.ylabel('price')
        plt.title(f'{ticker} price over {period}')
        plt.legend()
        plt.xticks(rotation=45)
        plt.savefig(f'{CWD}/downloads/{ticker}hl.jpg')


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
    ## Charts
    ####################
    if message.content.startswith('!chart'):
        info_str = message.content[len('!chart'):].strip()
        info_list = info_str.split()

        ticker = info_list[0]
        if (len(info_list) == 2):
            period = info_list[1]
        else:
            period = '1d'

        chart(ticker, period)

        path = CWD + '/downloads/'

        for f in os.listdir(CWD + '/downloads/'):
            if re.match(f'{ticker}.', f):
                pic_path = path + f
                await client.send_file(message.channel, pic_path, filename=ticker+'.jpg')
                os.remove(pic_path)
            elif re.match(f'{ticker}hl.', f):
                pic_path = path + f
                await client.send_file(message.channel, pic_path, filename=ticker+'hl.jpg')
                os.remove(pic_path)
            else:
                msg = 'Something went wrong :/'
                embed = discord.Embed(title='Google Pic Error :octagonal_sign:', description=msg, color=0xe10000)
                await client.send_message(message.channel, embed=embed)

        #os.rmdir(path)




    ####################
    ## ShowDiff
    ####################
    if message.content.startswith('!showdiff'):
        info_str = message.content[len('!showdiff'):].strip()
        info_list = info_str.split()

        cols_ = ['date', 'high', 'close', 'open', 'changePercent', 'vwap']
        cols_1 = ['date', 'high', 'close', 'open']
        calc_ = ['high', 'close', 'open']

        if (len(info_list) == 1):
            ticker = info_list[0]

            r_ = get_symbol_by_period(ticker, '1d')
            df_ = pd.read_json(r_.content)[cols_1].head(2)
            dic_ = df_.head(1).transpose().to_dict()[0]

            r = get_symbol_by_period(ticker)
            df = pd.read_json(r.content)[cols_].head(2)


        if (len(info_list) == 2):
            ticker, period = info_list[0], info_list[1]

            if period == '1d':
                cols_ = cols_1
                calc_ = ['high', 'close', 'open']

            r_ = get_symbol_by_period(ticker, '1d')
            df_ = pd.read_json(r_.content)[cols_1].head(2)
            dic_ = df_.head(1).transpose().to_dict()[0]

            r = get_symbol_by_period(ticker, period)
            df = pd.read_json(r.content)[cols_].head(2)

        dic = df.head(1).transpose().to_dict()[0]

        embed = discord.Embed(title=ticker, description='Stock info.', color=0x58b3ea)
        for i in cols_:
            if i in calc_:
                d = dic['date'].strftime('%Y/%m/%d')
                name_out = f'change in {i} since {d}'
                value_out = f'diff: {dic_[i]-dic[i]}' + '\n' + f'today: {dic_[i]}'
                embed.add_field(name=name_out, value=value_out, inline=False)
            else:
                embed.add_field(name=i, value=dic[i], inline=False)

        await client.send_message(message.channel, embed=embed)


    ####################
    ## Market
    ####################
    if message.content.startswith('!market'):
            market = pd.read_json(get_market().content).head(2).to_csv()
            embed = discord.Embed(title='Info', description=market, color=0x9925db)
            await client.send_message(message.channel, embed=embed)


    ####################
    ## Insult command
    ####################
    if message.content.startswith('!insult'):
        name = message.content[len('!insult'):].strip()

        if (name != ''):
            possible_responses = [
                'Fuck {}.'.format(name),
                '{} is a bitch.'.format(name),
                '{}? Total brown pants.'.format(name),
                '{} is a cuck lord.'.format(name),
                '{} is worse than Hitler.'.format(name),
            ]

            msg = random.choice(possible_responses)
            embed = discord.Embed(title='Insult', description=msg, color=0xf4126d)
            await client.send_message(message.channel, embed=embed)
        else:

            msg = 'You didn\'t say whom to insult :/'
            embed = discord.Embed(title='Insult Error :octagonal_sign:', description=msg, color=0xe10000)
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
        #rick     = '!rick\n'
        #morty    = '!morty\n'
        odds     = '!odds -limit -guess\n'
        insult   = '!insult -name\n'
        sayaloud = '!sayaloud -message\n'
        pic      = '!pic -term(s)'

        embed = discord.Embed(title=intro, description='Available commands.', color=0x58b3ea)
        embed.add_field(name=hello, value='Greeting', inline=False)
        #embed.add_field(name=rick, value='Randomly generated Rick quote', inline=False)
        #embed.add_field(name=morty, value='Randomly generated Morty quote', inline=False)
        embed.add_field(name=odds, value='You won\'t.', inline=False)
        embed.add_field(name=insult, value='We all know someone...', inline=False)
        #embed.add_field(name=sayaloud, value='Says any message out loud', inline=False)
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