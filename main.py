import os
import bot
import json
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

points.start()
coeurbot.run()
