import os
import json
import simpleobsws
from dotenv import load_dotenv
from emoji import is_emoji
from twitchio.ext import commands
from twitchio.ext import routines

load_dotenv()

class Bot(commands.Bot):

	chatters = None
	prize = 0
	is_fast = False
	ws = simpleobsws.WebSocketClient(url = os.environ["URL"], password = os.environ["PASSWORD"])
	videos = { "again": 6,
			   "borgir": 0,
			   "chika": 9,
			   "kick": 2,
			   "mario": 8,
			   "ora": 3,
			   "parrot": 4,
			   "rock": 7,
			   "what": 5,
			   "wink": 1 }


	def __init__(self):
		super().__init__(token = os.environ["TOKEN"], prefix = "!", initial_channels = [os.environ["STREAMER_NAME"]])


	async def event_ready(self):
		print(f"Logged in as {self.nick} ({self.user_id})")


	async def event_message(self, message):
		if message.echo:
			return

		self.chatters = message.channel.chatters
		chatter = message.author.name
		
		if (await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]])) and (chatter != os.environ["STREAMER_NAME"]):			
			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter not in data.keys():
				data[chatter] = { "points": 0, "total": 0 }
				self.reminder.start(message)

			data[chatter]["points"] += 10
			data[chatter]["total"] += 10

			with open("data.json", "w", encoding = "utf8") as f:
				json.dump(data, f, indent = 4)

		await self.handle_commands(message)


	def get_chatters(self):
		return self.chatters


	def set_prize(self, prize):
		self.prize = prize

	
	async def websocket(self, keyId):
		await self.ws.connect()
		await self.ws.wait_until_identified()

		data = { "keyId": keyId, "keyModifiers": { "control": True } }
		request = simpleobsws.Request(requestType = "TriggerHotkeyByKeySequence", requestData = data) 
		
		await self.ws.call(request)
		await self.ws.disconnect()


	@commands.command()
	async def love(self, ctx: commands.Context):   
		chatter = ctx.author.name
		message = ""
		
		for i in range(50):
			message += "<3 Elove "

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys():
				data[chatter]["points"] += 1
				data[chatter]["total"] += 1

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)

		await ctx.send(message)

	
	@commands.command(aliases = ["s"])
	async def spam(self, ctx: commands.Context, emote):
		max_emote_quantity = 100
		message_max_size = 500
		emote_quantity = 0
		message = ""
		
		emote = emote.split(" ")[0]

		while ((len(message) < message_max_size - len(emote)) and (emote_quantity < max_emote_quantity)):
			message += f"{emote} "
			emote_quantity += 1

		await ctx.send(message)


	@commands.command(aliases = ["l"])
	async def links(self, ctx: commands.Context):
		await ctx.send(f"Pour me suivre sur Twitter, c'est ici : https://twitter.com/{os.environ['STREAMER_NAME']} et pour rejoindre la communauté Discord c'est là : https://discord.gg/qpMzjhua7u")


	@commands.command(aliases = ["e"])
	async def extension(self, ctx: commands.Context):
		await ctx.send(f"Téléchargez mon extension Firefox pour profiter des nouvelles emotes : https://addons.mozilla.org/en/firefox/addon/twitch-emotes-extension")


	@commands.command(aliases = ["c"])
	async def clip(self, ctx: commands.Context):
		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			partial_user = self.create_user(os.environ["STREAMER_ID"], os.environ["STREAMER_NAME"])
			clip = await partial_user.create_clip(token = os.environ["TOKEN"])
			await ctx.send(f"Clip crée! Disponible ici : {clip['edit_url'].replace('/edit', '')}")


	@commands.command(aliases = ["b"])
	async def balance(self, ctx: commands.Context):
		chatter = ctx.author.name

		with open("data.json", "r", encoding = "utf8") as f:
			data = json.load(f)

		if chatter in data.keys():
			await ctx.send(f"{chatter}, tu as actuellement {data[chatter]['points']}♥ et amassé un total de {data[chatter]['total']}♥.")


	@commands.command(aliases = ["r"])
	async def rank(self, ctx: commands.Context):
		max_top_size = 10

		with open("data.json", "r", encoding = "utf8") as f:
			data = json.load(f)

		ordered_data = dict(sorted(data.items(), key = lambda item: item[1]["total"], reverse = True)[:max_top_size])
		top_size = len(ordered_data)
		top_text = f"Top {top_size} : "
		
		for i in range(top_size):
			chatter = list(ordered_data)[i]
			top_text += f"{i + 1}. {chatter} ({ordered_data[chatter]['total']}♥)"
			if i < top_size - 1:
				top_text += ", "
		
		await ctx.send(top_text)
	

	@commands.command()
	async def give(self, ctx: commands.Context, user, amount):
		chatter = ctx.author.name

		with open("data.json", "r", encoding = "utf8") as f:
			data = json.load(f)
		
		if chatter == os.environ["STREAMER_NAME"]:
			if user in data.keys():
				data[user]["points"] += int(amount)
				data[user]["total"] += int(amount)	
				
				await ctx.send(f"{user}, tu as {data[user]['points']}♥.")
		else:
			if chatter in data.keys():
				data[chatter]["points"] -= int(amount)
				if data[chatter]["points"] < 0:
					data[chatter]["points"] = 0

				await ctx.send(f"{chatter}, tu as {data[chatter]['points']}♥.")

		with open("data.json", "w", encoding = "utf8") as f:
			json.dump(data, f, indent = 4)


	@commands.command(aliases = ["g"])
	async def get(self, ctx: commands.Context):
		if self.prize > 0:
			chatter = ctx.author.name

			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys():
				data[chatter]["points"] += self.prize
				data[chatter]["total"] += self.prize

				await ctx.send(f"{chatter}, tu as gagné {self.prize}♥.")

				self.prize = 0				
 
				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)


	@commands.command(aliases = ["v"])
	async def video(self, ctx: commands.Context, name):
		cost = 50

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			chatter = ctx.author.name

			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if name in self.videos.keys() and chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)

				await self.websocket(f"OBS_KEY_NUM{self.videos[name]}")


	@commands.command(aliases = ["f"])
	async def fast(self, ctx: commands.Context):
		cost = 150

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]) and not self.is_fast:
			chatter = ctx.author.name

			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)

				await self.websocket("OBS_KEY_NUMPERIOD")
				self.is_fast = True
				self.stop_fast.start()


	@commands.command()
	async def end(self, ctx: commands.Context):
		cost = 100000

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			chatter = ctx.author.name

			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)

				await self.websocket("OBS_KEY_NUMPLUS")


	@commands.command()
	async def badge(self, ctx: commands.Context, emoji):
		cost = 500
		chatter = ctx.author.name

		if is_emoji(emoji):
			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost
				data[chatter]["badge"] = emoji

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)


	@commands.command()
	async def banner(self, ctx: commands.Context, banner):
		cost = 2000
		chatter = ctx.author.name

		for b in os.listdir("../Twitch-REST-API/banners/"):
			if b.split(".")[0] == banner:
				
				with open("data.json", "r", encoding = "utf8") as f:
					data = json.load(f)

				if chatter in data.keys() and data[chatter]["points"] > cost:
					data[chatter]["points"] -= cost
					data[chatter]["banner"] = banner

					with open("data.json", "w", encoding = "utf8") as f:
						json.dump(data, f, indent = 4)

	
	@commands.command()
	async def remove(self, ctx: commands.Context, type):
		chatter = ctx.author.name
		
		if type == "badge" or type == "banner":
			with open("data.json", "r", encoding = "utf8") as f:
				data = json.load(f)

			if chatter in data.keys() and type in data[chatter].keys():
				del data[chatter][type]

				with open("data.json", "w", encoding = "utf8") as f:
					json.dump(data, f, indent = 4)			


	@routines.routine(seconds = 30, iterations = 1, wait_first = True)
	async def stop_fast(self):
		await self.websocket("OBS_KEY_NUMPERIOD")
		self.is_fast = False


	@routines.routine(seconds = 150, iterations = 1, wait_first = True)
	async def reminder(self, message):
		ctx = await self.get_context(message)
		await ctx.send(f"N'hésitez pas à rejoindre la communauté Discord : https://discord.gg/qpMzjhua7u et à télécharger l'extension Firefox : https://addons.mozilla.org/en/firefox/addon/twitch-emotes-extension")
