# CoeurBot

CoeurBot is a Twitch chat application made with Python 3 and based on[TwitchIO](https://github.com/TwitchIO/TwitchIO). It responds to specific commands in order to animate a Twitch stream. To do so, it includes a points system and the implementation of websockets to connect with OBS.


## Installation Guide


### Requirements

To correctly install this project, it is essential to have completed the following steps:

1. Install Python 3.10 or higher.
2. Install python-dotenv 0.20 or higher.
3. Install twitchio 2.4 or higher.
4. Install simpleobsws 1.3 or higher.
5. Add a `.env` file to the root of the project. 
  
Body of the `.env` file:
```py
# Streamer
STREAMER_NAME = ...
STREAMER_ID = ...

# Twitch
TOKEN = ...
CLIENT_ID = ...

# OBS (websocket)
URL = ... 
PASSWORD = ...
```

### Installation

After completing the requirements, it is necessary to follow each of these steps:

1. Clone the project,  
```git clone https://github.com/mmeyrat/CoeurBot.git```
2. Add the `.env` file to the root of the project.
3. Run the project,  
```python main.py```

----

Meyrat Maxime
