import os
import json
import simpleobsws
from dotenv import load_dotenv
from twitchio.ext import commands

load_dotenv()

class Bot(commands.Bot):

	chatters = None
	ws = simpleobsws.WebSocketClient(url = os.environ["URL"], password = os.environ["PASSWORD"])


	def __init__(self):
		super().__init__(token = os.environ["TOKEN"], prefix = "!", initial_channels = [os.environ["STREAMER_NAME"]])


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
			json.dump(data, f, indent = 4)

		await self.handle_commands(message)


	def get_chatters(self):
		return self.chatters


	def emote_spam(self, text, count):
		message = ""

		for i in range(count):
			message += text

		return message


	@commands.command(aliases = ["el"])
	async def love(self, ctx: commands.Context):        
		await ctx.send(self.emote_spam("<3 ", 100))


	@commands.command(aliases = ["ed"])
	async def dance(self, ctx: commands.Context):
		await ctx.send(self.emote_spam("Edance", 50))


	@commands.command(aliases = ["ep"])
	async def pog(self, ctx: commands.Context):
		await ctx.send(self.emote_spam("Epog", 50))


	@commands.command(aliases = ["c"])
	async def clip(self, ctx: commands.Context):
		partial_user = self.create_user(os.environ["STREAMER_ID"], os.environ["STREAMER_NAME"])
		clip = await partial_user.create_clip(token = os.environ["TOKEN"])
		await ctx.send(f"Clip crée et dispo ici : {clip['edit_url'].replace('/edit', '')}")


	@commands.command(aliases = ["b"])
	async def balance(self, ctx: commands.Context):
		chatter = ctx.author.name

		with open("data.json", "r") as f:
			data = json.load(f)

		if chatter in data.keys():
			await ctx.send(f"{chatter}, tu as actuellement {data[chatter]['points']} ♥ et amassé un total de {data[chatter]['total']} ♥")


	@commands.command(aliases = ["r"])
	async def rank(self, ctx: commands.Context):
		max_top_size = 10

		with open("data.json", "r") as f:
			data = json.load(f)

		ordered_data = dict(sorted(data.items(), key = lambda item: item[1]["total"], reverse = True)[:max_top_size])
		top_size = len(ordered_data)
		top_text = f"Top {top_size} : "
		
		for i in range(top_size):
			chatter = list(ordered_data)[i]
			top_text += f"{i + 1}. {chatter} ({ordered_data[chatter]['total']} ♥)"
			if i < top_size - 1:
				top_text += ", "
		
		await ctx.send(top_text)
	

	@commands.command(aliases = ["g"])
	async def give(self, ctx: commands.Context, chatter, amount):
		with open("data.json", "r") as f:
				data = json.load(f)
		
		if ctx.author.name == os.environ["STREAMER_NAME"]:
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
				json.dump(data, f, indent = 4)	


	@commands.command()
	async def test(self, ctx: commands.Context, number):
		await self.ws.connect()
		await self.ws.wait_until_identified()

		data = {"keyId": f"OBS_KEY_NUM{number}", "keyModifiers": { "control": True}}
		request = simpleobsws.Request(requestType = "TriggerHotkeyByKeySequence", requestData = data) 
		
		await self.ws.call(request)
		await self.ws.disconnect()