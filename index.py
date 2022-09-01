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

	chatters = None

	def __init__(self):
		super().__init__(token = os.environ["TOKEN"], prefix = "!", initial_channels = [streamer_name])

	async def event_ready(self):
		print(f"Logged in as {self.nick} ({self.user_id})")

	async def event_message(self, message):
		if message.echo:
			return

		self.chatters = message.channel.chatters
		chatter = message.author.name

		with open("data.json", "r") as f:
			data = json.load(f)

		if chatter not in data.keys():
			data[chatter] = { "points": 0, "total": 0 }

		data[chatter]["points"] += 10
		data[chatter]["total"] += 10

		with open("data.json", "w") as f:
			json.dump(data, f)

		await self.handle_commands(message)

	def get_chatters(self):
		return self.chatters

	def emote_spam(self, text, count):
		message = ""

		for i in range(count):
			message += text

		return message

	@commands.command()
	async def love(self, ctx: commands.Context):        
		await ctx.send(self.emote_spam("<3 ", 100))

	@commands.command()
	async def dance(self, ctx: commands.Context):
		await ctx.send(self.emote_spam("Edance", 50))

	@commands.command()
	async def pog(self, ctx: commands.Context):
		await ctx.send(self.emote_spam("Epog", 50))

	@commands.command()
	async def clip(self, ctx: commands.Context):
		partial_user = self.create_user(streamer_id, streamer_name)
		clip = await partial_user.create_clip(token = os.environ["TOKEN"])
		await ctx.send(f"Clip crée et dispo ici : {clip['edit_url'].replace('/edit', '')}")

	@commands.command()
	async def money(self, ctx: commands.Context):
		chatter = ctx.author.name

		with open("data.json", "r") as f:
			data = json.load(f)

		if chatter in data.keys():
			await ctx.send(f"{chatter}, tu as actuellement {data[chatter]['points']} ♥ et amassé un total de {data[chatter]['total']} ♥")
	
	@commands.command()
	async def give(self, ctx: commands.Context, chatter, amount):
		with open("data.json", "r") as f:
				data = json.load(f)
		
		if ctx.author.name == streamer_name:
			if chatter in data.keys():
				data[chatter]["points"] += int(amount)
				data[chatter]["total"] += int(amount)	
		else:
			if chatter in data.keys():
				data[chatter]["points"] -= int(amount)
				if data[chatter]["points"] < 0:
					data[chatter]["points"] = 0

		await ctx.send(f"{chatter}, tu as {data[chatter]['points']} ♥")

		with open("data.json", "w") as f:
				json.dump(data, f)	


bot = Bot()

@routines.routine(minutes=5)
async def points():	
	chatters = bot.get_chatters()
	
	if chatters is not None:
		with open("data.json", "r") as f:
			data = json.load(f)

		for chatter in chatters:
			if chatter.name in data.keys():
				data[chatter.name]["points"] += 50
				data[chatter.name]["total"] += 50

		with open("data.json", "w") as f:
			json.dump(data, f)

points.start()
bot.run()