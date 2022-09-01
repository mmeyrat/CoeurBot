import os
import json
import requests as rq
from twitchio.ext import commands
from twitchio.ext import routines
from dotenv import load_dotenv

load_dotenv()

streamer_id = "433976821"
streamer_name = "aruten_"

class Bot(commands.Bot):

	def __init__(self):
		super().__init__(token = os.environ["TOKEN"], prefix = "!", initial_channels = [streamer_name])

	async def event_ready(self):
		print(f"Logged in as {self.nick} ({self.user_id})")

	async def event_message(self, message):
		# Messages with echo set to True are messages sent by the bot
		if message.echo:
			return

		with open("data.json", "r") as f:
			data = json.load(f)

		if message.author.name not in data.keys():
			data[message.author.name] = { "points": 0 }

		data[message.author.name]["points"] += 10

		with open("data.json", "w") as f:
			json.dump(data, f)

		await self.handle_commands(message)

	def emoteSpam(self, text, count):
		msg = ""
		for i in range(count):
			msg += text
		return msg

	@commands.command()
	async def love(self, ctx: commands.Context):        
		await ctx.send(self.emoteSpam("<3 ", 100))

	@commands.command()
	async def dance(self, ctx: commands.Context):
		await ctx.send(self.emoteSpam("Edance", 50))

	@commands.command()
	async def pog(self, ctx: commands.Context):
		await ctx.send(self.emoteSpam("Epog", 50))

	@commands.command()
	async def clip(self, ctx: commands.Context):
		partial_user = self.create_user(streamer_id, streamer_name)
		clip = await partial_user.create_clip(token = os.environ["TOKEN"])
		await ctx.send(f"Clip crée et dispo ici : {clip['edit_url'].replace('/edit', '')}")

	@commands.command()
	async def money(self, ctx: commands.Context):
		user = ctx.author.name

		with open("data.json", "r") as f:
			data = json.load(f)

		if user in data.keys():
			await ctx.send(f"{user} tu as actuellement {data[user]['points']} ♥")


@routines.routine(minutes=5)
async def points():
	with open("data.json", "r") as f:
			data = json.load(f)

	response = rq.get(f"https://tmi.twitch.tv/group/user/{streamer_name}/chatters").json()
	chatters = response["chatters"]["broadcaster"] + response["chatters"]["moderators"] + response["chatters"]["viewers"]
	
	for name in chatters:
		if name in data.keys():
			data[name]["points"] += 50
    
	with open("data.json", "w") as f:
		json.dump(data, f)


points.start()

bot = Bot()
bot.run()