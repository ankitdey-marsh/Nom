import os
import discord
from discord.ext import commands,tasks
from dotenv import load_dotenv
import requests
from discord import app_commands
from datetime import datetime
from logs import log_writer,error_logs
import google.generativeai as genai
from random import choice,randint
from itertools import cycle
import asyncio
from discord.ui import View, Button  
from newsapi import NewsApiClient

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

genai.configure(api_key=os.getenv('GENAI')) 
generation_config={"temperature":0.9,"top_p":1,"top_k":1,"max_output_tokens":300} 
model=genai.GenerativeModel("gemini-1.5-pro",generation_config=generation_config)

bot_statuses=cycle(["with my food","with my meow","with your heart","and nomnoming"])

@tasks.loop(seconds=60)
async def change_status()->None:
    await bot.change_presence(activity=discord.Game(next(bot_statuses)),status=discord.Status.online)
    
channel_counters = {}
@bot.event
async def on_message(message:str)->None:
    if message.author == bot.user:
        return

    if message.channel not in channel_counters:
        channel_counters[message.channel] = 0

    channel_counters[message.channel] += 1
    if channel_counters[message.channel] == 10:
        await message.channel.send("Oho i'm enjoying this!")
        channel_counters[message.channel] = 0

    await bot.process_commands(message)


@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction)->None:
    try:
        greets=[f"Hello there {interaction.user.mention}!",f"{interaction.user.mention} Still alive? 🤭",f"Nom was just thinking about you {interaction.user.mention} 🤗"]
        await interaction.response.send_message(greets[randint(0,2)])
        log_writer(interaction)
        print('Hello Success')
    except Exception as e:
        log_writer(interaction)
        print('Hello failed')


@bot.tree.command(name="weather",description="Get a quick weather update.")
@app_commands.describe(location="Enter your Location: ")
async def weather(interaction: discord.Integration,location:str)->None:
    weather=os.getenv('WEATHER_API')
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    url = BASE_URL + "appid=" + weather + "&q=" + location
    try:
        response = requests.get(url).json()
        temp = response['main']['temp']
        temp = temp-273.15
        f_temp="The temperature is {:.0f}°C".format(temp)
        humidity = response['main']['humidity']
        humid="Humidity is "+ str(humidity)+"%"
        feels_like="it feels like "+f"{response['main']['feels_like']-273.15:.0f}°C"
        await interaction.response.send_message(f"{interaction.user.mention} {f_temp} and {feels_like} . {humid} .", ephemeral=True)
        log_writer(interaction)
        print("Weather success.")
    except Exception as e:
        log_writer(interaction)
        error_logs(response)
        print("Weather failed.")
        await interaction.response.send_message(f"{interaction.user.mention} Invalid city name.", ephemeral=True)

@bot.tree.command(name="business_news",description="Get latest business updates.")
@app_commands.describe(country_code="Enter your country code: ")
async def news(interaction: discord.Integration,country_code:str)->None:
    try:
        api_endpoint="https://newsapi.org/v2/top-headlines"
        params={
            "country":{country_code},
            "apiKey": os.getenv('NEWS_API'),
            "category":"business"
        }
        response = requests.get(api_endpoint,params=params)
        response=response.json()
        embed=discord.Embed(colour=discord.Colour.dark_orange(),title="Latest Business News")
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        urls=[]
        for i in range(0,5):
            x=response["articles"][i]["description"]
            if x==None:
                x=""
            if response["articles"][i]["title"]=="[Removed]":
                continue
            embed.add_field(name=f'{i+1}) {response["articles"][i]["title"]}', value=f'{x}\n\n', inline=False)
            urls.append(response["articles"][i]["url"])
            
            view1 = MyView4(urls)

        await interaction.response.send_message(embed=embed,view=view1)
        log_writer(interaction)
        print('News fetch successful')
    except Exception as e:
        await interaction.response.send_message("News fetch unsuccessful",ephemeral=True)
        log_writer(interaction)
        print('News fetch successful')
        error_logs(f"Error: {e}")


class MyView4(View):
    def __init__(self,urls):
        super().__init__()
        num=["1st","2nd","3rd","4th","5th"]
        for i in range(0,len(urls)):
            self.add_item(Button(label=f"{num[i]}", style=discord.ButtonStyle.link, url=f'{urls[i]}', emoji="💼"))


@bot.tree.command(name="sports_news",description="Get latest sports updates.")
@app_commands.describe(country_code="Enter your country code: ")
async def news(interaction: discord.Integration,country_code:str)->None:
    try:
        api_endpoint="https://newsapi.org/v2/top-headlines"
        params={
            "country":{country_code},
            "apiKey": os.getenv('NEWS_API'),
            "category":"sports"
        }
        response = requests.get(api_endpoint,params=params)
        response=response.json()
        embed=discord.Embed(colour=discord.Colour.dark_orange(),title="Latest Sports News")
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        urls=[]
        for i in range(0,5):
            x=response["articles"][i]["description"]
            if x==None:
                x=""
            if response["articles"][i]["title"]=="[Removed]":
                continue
            embed.add_field(name=f'{i+1}) {response["articles"][i]["title"]}', value=f'{x}\n\n', inline=False)
            urls.append(response["articles"][i]["url"])
            
            view1 = MyView3(urls)

        await interaction.response.send_message(embed=embed,view=view1)
        log_writer(interaction)
        print('News fetch successful')
    except Exception as e:
        await interaction.response.send_message("News fetch unsuccessful",ephemeral=True)
        log_writer(interaction)
        print('News fetch unsuccessful')
        error_logs(f"Error: {e}")
        


class MyView3(View):
    def __init__(self,urls):
        super().__init__()
        num=["1st","2nd","3rd","4th","5th"]
        for i in range(0,len(urls)):
            self.add_item(Button(label=f"{num[i]}", style=discord.ButtonStyle.link, url=f'{urls[i]}', emoji="⚽"))



@bot.tree.command(name="news",description="Get latest news updates.")
@app_commands.describe(country_code="Enter your country code: ")
async def news(interaction: discord.Integration,country_code:str)->None:
    try:
        api_endpoint="https://newsapi.org/v2/top-headlines"
        params={
            "country":{country_code},
            "apiKey": os.getenv('NEWS_API')
        }
        response = requests.get(api_endpoint,params=params)
        response=response.json()
        embed=discord.Embed(colour=discord.Colour.dark_orange(),title="Breaking News")
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        urls=[]
        for i in range(0,5):
            x=response["articles"][i]["description"]
            if x==None:
                x=""
            if response["articles"][i]["title"]=="[Removed]":
                continue
            embed.add_field(name=f'{i+1}) {response["articles"][i]["title"]}', value=f'{x}\n\n', inline=False)
            urls.append(response["articles"][i]["url"])
            
            view1 = MyView2(urls)

        await interaction.response.send_message(embed=embed,view=view1)
        log_writer(interaction)
        print('News fetch successful')
    except Exception as e:
        await interaction.response.send_message("News fetch unsuccessful",ephemeral=True)
        error_logs(f"Error: {e}")
        log_writer(interaction)
        print('News fetch unsuccessful')


class MyView2(View):
    def __init__(self,urls):
        super().__init__()
        num=["1st","2nd","3rd","4th","5th"]
        for i in range(0,len(urls)):
            self.add_item(Button(label=f"{num[i]}", style=discord.ButtonStyle.link, url=f'{urls[i]}', emoji="🗞️"))



@bot.tree.command(name="search",description="Search in Gemini.")
@app_commands.describe(search="Enter your prompt: ")
async def search(interaction: discord.Integration,search:str)->None:
    await interaction.response.defer(ephemeral=True)
    response= model.generate_content(["Never give answers in form of points or bullets."+search])
    try:
        s=response.text
        last_dot_index = s.rfind(".")
        if last_dot_index != -1:
            s = s[:last_dot_index+1]
        response = s
        await interaction.followup.send(f"{response}", ephemeral=True)

        log_writer(interaction)
        print('Search successful')
    except:
        log_writer(interaction)
        print('Search unsuccessful')
        error_logs(response)
        await interaction.response.send_message(f"{interaction.user.mention} Search unsuccessful .", ephemeral=True)

@bot.tree.command(name="score_matchday",description="Get all matchday updates.")
@app_commands.describe(league="Enter league code: ")
async def league_tables(interaction: discord.Integration,league:str)->None:
    api_endpoint = f"https://api.football-data.org/v4/competitions/{league.upper()}/matches"
    params = {
        "season":2024
    }
    api_key = os.getenv('SCORES_API') 
    headers = {
        "X-Auth-Token": api_key 
    }
    response = requests.get(api_endpoint, headers=headers,params=params)
    y=""
    try:
        data = response.json()
        x=len(data["matches"])
        y+=f' {data["competition"]["name"]}\n\n'
        y+=f' Match Day - {data["matches"][0]["season"]["currentMatchday"]} - {data["matches"][data["resultSet"]["played"]]["stage"]}\n\n'
        for i in range(0,x):
            current_matchday=data["matches"][i]["matchday"]
            if data["matches"][i]['season']['currentMatchday']==data["matches"][i]["matchday"]:
                home_score=data["matches"][i]["score"]["fullTime"]["home"]
                away_score=data["matches"][i]["score"]["fullTime"]["away"]
                if home_score==None:
                    home_score='TBP'
                    away_score='TBP'
                y = y + f'\t{data["matches"][i]["homeTeam"]["tla"]}    {home_score:3} - {away_score:<3}'
                if data["matches"][i]["score"]["duration"]=="PENALTY_SHOOTOUT":
                    y+="(P)"
                    y+=f' {data["matches"][i]["awayTeam"]["tla"]}\n\n'
                else:
                    y+=f'    {data["matches"][i]["awayTeam"]["tla"]}\n\n'
        await interaction.response.send_message(f'```{y}```')
        log_writer(interaction)
        print('Score fetch successful')
    except:
        log_writer(interaction)
        print("Score fetch failed.")
        error_logs(f"Error: {response.status_code}")
        await interaction.response.send_message('Failed to fetch',ephemeral=True)


@bot.tree.command(name="score_league",description="Get football league tables and group tables.")
@app_commands.describe(league="Enter league code: ")
async def league_tables(interaction: discord.Integration,league:str)->None:
    api_endpoint = f"https://api.football-data.org/v4/competitions/{league.upper()}/standings"
    api_key = os.getenv('SCORES_API') 

    headers = {
        "X-Auth-Token": os.getenv('SCORES_API')  
    }
    response = requests.get(api_endpoint, headers=headers)
    x=''
    try:
        data = response.json()
        number_of_teams=len(data["standings"][0]["table"])
        number_of_groups=len(data["standings"])
        x=x+f' {data["competition"]["name"]} - {data["filters"]["season"]}\n\n'
        for j in range(0,number_of_groups):
            if data["standings"][j]["group"]!=None:
                x=x+f'\n{data["standings"][j]["group"]}\n\n'
            else:
                pass
            x=x+' Std   Team   P   W   D   L  Pt\n\n'
            for i in range(0,int(number_of_teams)):
                team_name = data["standings"][j]["table"][i]["team"]["tla"]
                padded_name = team_name.split()[0][:12]
                x=x+f' {data["standings"][j]["table"][i]["position"]:2}    {padded_name:5}{data["standings"][j]["table"][i]["playedGames"]:3} {data["standings"][j]["table"][i]["won"]:3}  {data["standings"][j]["table"][i]["draw"]:2}  {data["standings"][j]["table"][i]["lost"]:2}  {data["standings"][j]["table"][i]["points"]:2}\n'
            
        await interaction.response.send_message(f'```{x}```')
        log_writer(interaction)
        print('Score fetch successful')
              
    except:
        log_writer(interaction)
        print("Score fetch failed.")
        error_logs(f"Error: {response.status_code}")
        await interaction.response.send_message('Failed to fetch',ephemeral=True)



@bot.tree.command(name="help",description="Get a list of all commands.")
async def help(interaction: discord.Integration)->None:
    try:
        embed=discord.Embed(colour=discord.Colour.dark_orange(),title="Powers of Nom.")
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        # embed.add_field(name="**Hi**", value="\t**/info:** Info about Nom.\n **/hello:** Greets the user.\n **/weather:** Gives a quick weather forecast.\n **/search:** Search up anything.\n **/score_league:** Shows league tables and group stages.\n **/score_matchday:** Shows latest matchday game updates.\n **/score_help:** Scores help for competition codes.\n", inline=False)
        embed.add_field(name='**General:**', value='''
        **`/info`**: Info about Nom.
        **`/hello`**: Greets the user.
        **`/weather`**: Gives a quick weather forecast.
        **`/search`**: Search up anything.
        ''', inline=False)  
        embed.add_field(name='**Football:**', value='''
        **`/score_league:`**: Shows league tables and group stages.
        **`/score_matchday:`**: Shows latest matchday game updates.
        **`/score_help:`**: Scores help for competition codes.
        **`/search`**: Search up anything.
        ''', inline=False) 
        embed.add_field(name='**News:**', value='''
        **`/news:`**: Shows breaking news from desired country.
        **`/sports_news:`**: Shows latest sports news from desired country.
        **`/business_news:`**: Scores latest business related news.
        ''', inline=False) 
        view=MyView5()
        await interaction.response.send_message(embed=embed,view=view)
        log_writer(interaction)
        print('Help Success')
    except Exception as e:
        log_writer(interaction)
        print('Help failed')
        error_logs(e)
        await interaction.response.send_message('Help failed',ephemeral=True)

class MyView5(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label=f"News Country codes", style=discord.ButtonStyle.link, url=f'https://newsapi.org/docs/endpoints/top-headlines'))



class MyView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="GitHub Repository", style=discord.ButtonStyle.link, url="https://github.com/ankitdey-marsh/Nom", emoji="🐙"))
        

@bot.tree.command(name="info",description="Get Nom info")
async def info(interaction: discord.Integration)->None:
    try:
        total_members = 0
        for guild in bot.guilds:
            total_members += guild.member_count
        total_members-=len(bot.guilds)
        embed=discord.Embed(colour=discord.Colour.dark_orange())
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        embed.add_field(name="",value="A multi-purpose Discord bot with gemini integration, football news,fetch weather report, and much more.",inline=False)
        embed.add_field(name="Bot User",value=f"{bot.user}",inline=True)
        embed.add_field(name="Guilds",value=f"{len(bot.guilds)}",inline=True)
        embed.add_field(name="Members",value=f"{total_members}",inline=True)
        embed.add_field(name="Prefix",value=f"/",inline=True)
        embed.add_field(name="Webpage",value=f"[Official Nom](https://dub.sh/officialnom)",inline=True)
        embed.add_field(name="Developer",
                        value="[Ankit Dey](https://dub.sh/ankitdey)",
                        inline=True)
        embed.set_footer(text=f"© 2022-2024 Ankit Dey | Code licensed under the MIT License")
        embed.set_image(
            url="https://i.pinimg.com/736x/55/57/2a/55572a00eff9b0f0b4b836446d6ec476.jpg")
        
        view = MyView()
        await interaction.response.send_message(embed=embed, view=view)
        log_writer(interaction)
        print('Help Success')
    except Exception as e:
        log_writer(interaction)
        print('Help failed')
        error_logs(e)
        await interaction.response.send_message('Help failed',ephemeral=True)   

@bot.tree.command(name="score_help",description="Competition codes for scores.")
async def help(interaction: discord.Integration)->None:
    try:
        embed=discord.Embed(colour=discord.Colour.dark_orange(),title="Competition Codes.")
        embed.set_author(icon_url="https://i.pinimg.com/564x/9a/bf/a0/9abfa0dc5ae0442470e9214453c3d7d2.jpg",name="Nom")
        embed.add_field(name="", value="**World Cup** : **WC**\n**Premier League** : **PL**\n**La Liga** : **PD**\n**Ligue 1** : **FL1**\n**Bundesliga** : **BL1**\n**Serie A** : **SA**\n**Euro Cup** : **EC**\n**Eredivisie** : **DED**\n**Copa Libertadores** : **CLI**\n**Championship** : **ELC**\n**Campeonato Brasileiro Série A** : **BSA**\n", inline=False)
        await interaction.response.send_message(embed=embed)
        log_writer(interaction)
        print('Help Success')
    except Exception as e:
        log_writer(interaction)
        print('Help failed')
        error_logs(e)
        await interaction.response.send_message('Help failed',ephemeral=True)

@bot.event
async def on_ready()->None:
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()
    change_status.start()

def main()->None:
    bot.run(token)

if __name__=='__main__':
    main()

