import os
import json
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()

streamer_id = "433976821"
streamer_name = "aruten_"

class Bot(commands.Bot):

	def __init__(self):
		super().__init__(token = os.environ["TOKEN"], prefix = "!", initial_channels = [streamer_name])

	async def event_ready(self):
		print(f"Logged in as {self.nick}")
		print(f"User id is {self.user_id}")

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

bot = Bot()
bot.run()