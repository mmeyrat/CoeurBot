import os
import bot
import json
import numpy as np
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


@routines.routine(seconds = 10, wait_first = True)
async def lottery():
	coeurbot.set_prize(50)
	await coeurbot.get_channel(os.environ["STREAMER_NAME"]).send("test")

	#if (await coeurbot.fetch_streams(user_ids = [os.environ["STREAMER_ID"]])):


points.start()
lottery.start()
coeurbot.run()
