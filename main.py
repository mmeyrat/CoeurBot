import bot
import json
from twitchio.ext import routines

coeurbot = bot.Bot()

@routines.routine(minutes = 5)
async def points():	
	chatters = coeurbot.get_chatters()
	
	if chatters is not None:
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