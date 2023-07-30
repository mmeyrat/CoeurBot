import os
import time
import json
import random
import datetime
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
	poll_data = {}
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

	def load_data(self):
		with open("data.json", "r", encoding = "utf8") as f:
			data = json.load(f)
		return data
	
	def save_data(self, data):
		with open("data.json", "w", encoding = "utf8") as f:
			json.dump(data, f, indent = 4)

	async def event_ready(self):
		print(f"Logged in as {self.nick} ({self.user_id})")

	async def event_message(self, message):
		if message.echo:
			return

		self.chatters = message.channel.chatters
		chatter = message.author.name
		
		if (await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]])) and (chatter != os.environ["STREAMER_NAME"]):			
			data = self.load_data()

			if chatter not in data.keys():
				data[chatter] = { "points": 0, "total": 0 }
				self.reminder.start(message)

			data[chatter]["points"] += 10
			data[chatter]["total"] += 10
			self.save_data(data)

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
			data = self.load_data()

			if chatter in data.keys():
				data[chatter]["points"] += 1
				data[chatter]["total"] += 1

				self.save_data(data)

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
		await ctx.send(f"Pour rejoindre la communauté Discord : https://discord.gg/qpMzjhua7u, pour me suivre sur TikTok : https://www.tiktok.com/@{os.environ['STREAMER_NAME']} et pour voir les VOD : https://www.youtube.com/@{os.environ['STREAMER_NAME']}.")

	@commands.command(aliases = ["e"])
	async def extension(self, ctx: commands.Context):
		await ctx.send(f"Téléchargez mon extension Firefox pour profiter des nouvelles emotes et autres cosmétiques : https://addons.mozilla.org/en/firefox/addon/twitch-emotes-extension")

	@commands.command(aliases = ["c"])
	async def clip(self, ctx: commands.Context):
		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			partial_user = self.create_user(os.environ["STREAMER_ID"], os.environ["STREAMER_NAME"])
			clip = await partial_user.create_clip(token = os.environ["TOKEN"])
			await ctx.send(f"Clip crée! Disponible ici : {clip['edit_url'].replace('/edit', '')}")

	@commands.command(aliases = ["b"])
	async def balance(self, ctx: commands.Context):
		chatter = ctx.author.name
		data = self.load_data()

		if chatter in data.keys():
			await ctx.send(f"{chatter}, tu as actuellement {data[chatter]['points']}♥ et amassé un total de {data[chatter]['total']}♥.")

	@commands.command(aliases = ["r"])
	async def rank(self, ctx: commands.Context):
		max_top_size = 10
		data = self.load_data()

		ordered_data = dict(sorted(data.items(), key = lambda item: item[1]["total"], reverse = True)[:max_top_size])
		top_size = len(ordered_data)
		top_text = f"Top {top_size} :"
		
		for i in range(top_size):
			chatter = list(ordered_data)[i]
			top_text += f" {i + 1}. {chatter} ({ordered_data[chatter]['total']}♥),"
		
		await ctx.send(top_text[:-1])
	
	@commands.command()
	async def give(self, ctx: commands.Context, user, amount):
		chatter = ctx.author.name	
		data = self.load_data()
		
		if chatter == os.environ["STREAMER_NAME"]:
			user = user.lower()

			if user in data.keys():
				data[user]["points"] += int(amount)
				data[user]["total"] += int(amount)	
				
				await ctx.send(f"{user}, tu as {data[user]['points']}♥.")
		else:
			if chatter in data.keys():
				data[chatter]["points"] -= abs(int(amount))

				if data[chatter]["points"] < 0:
					data[chatter]["points"] = 0

				await ctx.send(f"{chatter}, tu as {data[chatter]['points']}♥.")
		self.save_data(data)

	@commands.command()
	async def poll(self, ctx: commands.Context, action, *options):
		chatter = ctx.author.name	

		if chatter == os.environ["STREAMER_NAME"]:
			match action:
				case "start":
					poll_message = "Veuillez voter pour les choix suivants (avec la commande !vote) :"

					for option in options:
						self.poll_data[option] = []
						poll_message += f" [{option}]"

					await ctx.send(poll_message)			
				case "stop":
					total = 0
					winners_total = 0

					for option in self.poll_data:
						for voter in self.poll_data[option]:
							print(voter)
							total += int(voter[1])
							if option == options[0]:
								winners_total += int(voter[1])

					if total > 0:
						data = self.load_data()
						win_message = ""

						for winner in self.poll_data[options[0]]:
							if winner[0] in data.keys():
								profit = round(total * (int(winner[1]) / winners_total))
								data[winner[0]]["points"] += profit
								data[winner[0]]["total"] += profit
								win_message += f" {winner[0]} gagne {profit}♥,"

						win_message = win_message[:-1] if win_message != "" else "Aucun gagnant."
						await ctx.send( win_message)
						self.save_data(data)

					self.poll_data = {}
				case "cancel":
					self.poll_data = {}
					data = self.load_data()

					for option in self.poll_data:
						for voter in self.poll_data[option]:
							data[voter[0]]["points"] += voter[1]

					await ctx.send("Sondage annulé, les mises sont rendues.")
					self.save_data(data)
				case _:
					print("Wrong action")
	
	@commands.command()
	async def vote(self, ctx: commands.Context, choice, amount):
		if choice in self.poll_data and int(amount) > 0:
			chatter = ctx.author.name

			for option in self.poll_data:
				for voter in self.poll_data[option]:
					if voter[0] == chatter:
						return

			data = self.load_data()

			if chatter in data.keys() and data[chatter]["points"] > int(amount):
				data[chatter]["points"] -= int(amount)
				self.save_data(data)
				self.poll_data[choice].append([chatter, int(amount)])

				status_message = ""

				for option in self.poll_data:
					total = 0
					for voter in self.poll_data[option]:
						total += int(voter[1])
					status_message += f" [{option}] {total}♥ avec {len(self.poll_data[option])} vote(s),"

				await ctx.send(status_message[:-1])

	@commands.command(aliases = ["g"])
	async def get(self, ctx: commands.Context):
		if self.prize != 0:
			chatter = ctx.author.name
			data = self.load_data()

			if chatter in data.keys():				
				data[chatter]["points"] += self.prize
				message = f"{chatter}, tu as perdu {self.prize * -1}♥."

				if self.prize > 0:
					data[chatter]["total"] += self.prize
					message = f"{chatter}, tu as gagné {self.prize}♥."

				await ctx.send(message)
				self.prize = 0
				self.save_data(data)

	@commands.command()
	async def send(self, ctx: commands.Context, user, amount):
		chatter = ctx.author.name		
		data = self.load_data()

		if chatter in data.keys() and user in data.keys() and amount > 0:
			data[user]["points"] += int(amount)
			data[user]["total"] += int(amount)

			data[chatter]["points"] -= int(amount)

			if data[chatter]["points"] < 0:
				data[chatter]["points"] = 0

			await ctx.send(f"{user} a reçu {amount}♥ de la part de {chatter}.")
			self.save_data(data)

	@commands.command()
	async def spin(self, ctx: commands.Context):
		chatter = ctx.author.name		
		data = self.load_data()
		now = datetime.datetime.now()

		if "lastSpin" not in data[chatter].keys() or now >= datetime.timedelta(hours=24) + datetime.datetime.strptime(data[chatter]["lastSpin"], '%Y-%m-%d %H:%M:%S'):
			id = random.randint(0, 9)
		
			with open('spin.txt', 'w') as f:
				f.write(str(id))

			match(id):
				case 0:
					if chatter in data.keys():
						data[chatter]["points"] += 500
						data[chatter]["total"] += 500
				case 1:
					print("")
				case 2:
					if chatter in data.keys():
						data[chatter]["points"] += 50000
						data[chatter]["total"] += 50000
				case 3:
					if chatter in data.keys():
						data[chatter]["banner"] = "heart"
				case 4:
					if chatter in data.keys():
						data[chatter]["points"] -= 500
				case 5:
					if chatter in data.keys():
						data[chatter]["points"] += 5000
						data[chatter]["total"] += 5000
				case 6:
					self.fast()
				case 7:
					self.end()
				case 8:
					if chatter in data.keys():
						data[chatter]["banner"] = "gold"
				case 9:
					if chatter in data.keys():
						data[chatter]["points"] -= 50
				case _:
					print("")

			data[chatter]["lastSpin"] = now.strftime("%Y-%m-%d %H:%M:%S")

			self.save_data(data)
			await self.websocket("OBS_KEY_NUMASTERISK")
			time.sleep(10)
			await self.websocket("OBS_KEY_NUMASTERISK")

	@commands.command(aliases = ["v"])
	async def video(self, ctx: commands.Context, name):
		cost = 70

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			chatter = ctx.author.name
			data = self.load_data()

			if name in self.videos.keys() and chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost
				self.save_data(data)

				await self.websocket(f"OBS_KEY_NUM{self.videos[name]}")

	@commands.command(aliases = ["f"])
	async def fast(self, ctx: commands.Context):
		cost = 150

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]) and not self.is_fast:
			chatter = ctx.author.name
			data = self.load_data()

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost
				self.save_data(data)

				await self.websocket("OBS_KEY_NUMPERIOD")
				self.is_fast = True
				self.stop_fast.start()

	@commands.command()
	async def end(self, ctx: commands.Context):
		cost = 120000

		if await self.fetch_streams(user_ids = [os.environ["STREAMER_ID"]]):
			chatter = ctx.author.name			
			data = self.load_data()

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost
				self.save_data(data)

				await self.websocket("OBS_KEY_NUMPLUS")

	@commands.command()
	async def badge(self, ctx: commands.Context, emoji):
		cost = 700
		chatter = ctx.author.name

		if is_emoji(emoji):			
			data = self.load_data()

			if chatter in data.keys() and data[chatter]["points"] > cost:
				data[chatter]["points"] -= cost
				data[chatter]["badge"] = emoji
				self.save_data(data)

	@commands.command()
	async def banner(self, ctx: commands.Context, banner):
		cost = 4500
		chatter = ctx.author.name

		for b in os.listdir("../Twitch-REST-API/banners/"):
			if b.split(".")[0] == banner:		
				data = self.load_data()

				if chatter in data.keys() and data[chatter]["points"] > cost:
					data[chatter]["points"] -= cost
					data[chatter]["banner"] = banner
					self.save_data(data)

	@commands.command()
	async def remove(self, ctx: commands.Context, type):
		chatter = ctx.author.name
		
		if type == "badge" or type == "banner":
			data = self.load_data()

			if chatter in data.keys() and type in data[chatter].keys():
				del data[chatter][type]
				self.save_data(data)			

	@routines.routine(seconds = 30, iterations = 1, wait_first = True)
	async def stop_fast(self):
		await self.websocket("OBS_KEY_NUMPERIOD")
		self.is_fast = False

	@routines.routine(seconds = 150, iterations = 1, wait_first = True)
	async def reminder(self, message):
		ctx = await self.get_context(message)
		await ctx.send(f"N'hésitez pas à rejoindre la communauté Discord : https://discord.gg/qpMzjhua7u et à télécharger l'extension Firefox : https://addons.mozilla.org/en/firefox/addon/twitch-emotes-extension")
