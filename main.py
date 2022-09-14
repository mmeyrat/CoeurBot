import os
import bot
import json
import random
from dotenv import load_dotenv
from twitchio.ext import routines

load_dotenv()

coeurbot = bot.Bot()

@routines.routine(minutes = 5)
async def points():	
	chatters = coeurbot.get_chatters()
	
	if (await coeurbot.fetch_streams(user_ids = [os.environ["STREAMER_ID"]])) and (chatters is not None):
		with open("data.json", "r") as f:
			data = json.load(f)

		for chatter in chatters:
			if chatter.name in data.keys():
				data[chatter.name]["points"] += 50
				data[chatter.name]["total"] += 50

		with open("data.json", "w") as f:
			json.dump(data, f, indent = 4)


@routines.routine(minutes = 15, wait_first = True)
async def lottery():
	probability = random.randint(0, 2)

	if (await coeurbot.fetch_streams(user_ids = [os.environ["STREAMER_ID"]])) and (probability == 0):
		size = 99
		scale = 10**4

		numbers = [j for j in range(1, size + 1)]

		weights = [0, scale] + random.sample(range(1, scale), size - 1)
		weights.sort()
		sorted_weights = sorted([(weights[i] - weights[i - 1]) / scale for i in range(1, size + 1)], reverse = True)

		prize = random.choices(numbers, weights = sorted_weights, k = 1)[0] * 10

		coeurbot.set_prize(prize)
		await coeurbot.get_channel(os.environ["STREAMER_NAME"]).send(f"⚠ Offre de {prize}♥, !get pour les récupérer en premier.")


points.start()
lottery.start()
coeurbot.run()
