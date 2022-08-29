import os
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Bot(commands.Bot):

	def __init__(self):
		super().__init__(token=os.environ["TOKEN"], prefix="!", initial_channels=["aruten_"])

	async def event_ready(self):
		print(f"Logged in as {self.nick}")
		print(f"User id is {self.user_id}")

	async def event_message(self, message):
		# Messages with echo set to True are messages sent by the bot
		if message.echo:
			return

		print(message.content)

		await self.handle_commands(message)

	def emote(self, text, count):
		msg = ""

		for i in range(count):
			msg += text

		return msg

	@commands.command()
	async def love(self, ctx: commands.Context):        
		await ctx.send(self.emote("<3 ", 100))

	@commands.command()
	async def dance(self, ctx: commands.Context):
		await ctx.send(self.emote("Edance", 50))

	@commands.command()
	async def pog(self, ctx: commands.Context):
		await ctx.send(self.emote("Epog", 50))


bot = Bot()
bot.run()