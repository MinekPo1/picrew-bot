import os
from re import search
from typing import Union, cast, overload
import discord
from discord.embeds import Embed
import requests
import sys

dc = discord.Client()


@dc.event
async def on_ready():
	if dc.user is None:
		print("Failed to login.")
		sys.exit(1)
	channel = dc.get_channel(805214055643349003)
	if channel is not None:
		await channel.send("Bot is online!")
	else:
		print("Unable to access channel!")
	await dc.change_presence(activity=discord.Activity(
				type=discord.ActivityType.listening,
				name=" to get a picrew link requests!"
	))
	print("logged in as {}".format(dc.user))
	if "i" in sys.argv:
		print(
			"invite: {}".format(
				discord.utils.oauth_url(dc.user.id, discord.Permissions(68608))
			)
		)


@overload
async def scan(
		message:discord.Message,
		channel:discord.TextChannel,
		always_delete:bool = False,
		reply:bool = False
	) -> None:
	...


@overload
async def scan(
		message:str,
		channel:discord.TextChannel,
		always_delete:bool = False,
	) -> None:
	...


async def scan(
			message:Union[discord.Message,str],
			channel:discord.TextChannel,
			always_delete:bool = False,
			reply:bool = False
		):
	id:str = ""
	if isinstance(message,str) or message.attachments is None:
		if not(isinstance(message,str)):
			message = cast(str,message.content)
		elif reply:
			raise ValueError("Cannot reply to a string message!")
		if m:=search(r"https?://.+/(\d+)_.+\.png",message):
			id = m.group(1)
	else:
		for attachment in message.attachments:
			# example file name: 1011016_hbWCv9R5.png
			if m := search(r"^(\d+)_.+\.png$", attachment.filename):
				id = m.group(1)
	if id:
		r = requests.get("https://picrew.me/image_maker/{}".format(id))
		if r.ok:
			mess="here: https://picrew.me/image_maker/{}".format(id)
			delete = always_delete
		else:
			mess ="sadly got a {} :( picrew id: {}".format(r.status_code,id)  # )
			delete = True
	else:
		mess="Unable to get picrew id, sorry :(."  # )
		delete = True
	await channel.send(
			embed=Embed(
				description=mess
			),
			mention_author=False,
			**{
				"delete_after": 5 if delete else None,
				"reference": message if reply else None
			}
		)


@dc.event
async def on_message(message:discord.Message):
	if message.author == dc.user or dc.user is None:
		return
	if "picrew" in message.channel.name.lower() and message.content == "search"\
			and message.reference is not None:
		message = await message.channel.fetch_message(message.reference.message_id)
		if message is None:
			return
		await scan(message, message.channel)
		return

	if dc.user in message.mentions:
		if(
				m := search(
					r"https?://discord.com/channels/(\d+)/(\d+)/(\d+)",
					message.content
				)
			):
			channel = dc.get_channel(int(m.group(2)))
			if channel is not None:
				message2 = await channel.fetch_message(int(m.group(3)))
				if message2 is not None:
					await scan(message2, channel)
			else:
				await message.channel.send(
					"Unable to fetch message!",
					delete_after=5
				)
				# )
			return
		if "invite" in message.content.lower():
			await message.channel.send(
				discord.utils.oauth_url(dc.user.id, discord.Permissions(68608))
			)
			return
		if message.attachments is not None:
			await scan(message, message.channel)


@dc.event
async def on_raw_reaction_add(data:discord.RawReactionActionEvent):
	if data.event_type != "REACTION_ADD":
		return

	channel = dc.get_channel(data.channel_id)
	if channel is None:
		return
	message = await channel.fetch_message(data.message_id)

	if not(isinstance(message,discord.Message)):
		return

	if "picrew" in channel.name.lower()\
			and data.emoji.name == "🔍" and message.attachments is not None:
		user = dc.get_user(data.user_id)
		await scan(
			message, message.channel,
			always_delete=(
				user is not None
				and not(user.permissions_in(message.channel).send_messages)
			),
			reply=True
		)

token = os.getenv("TOKEN")

if token is None:
	try:
		with open('.env', 'r') as fh:
			vars_dict = {
				line.split('=')[0]: line.split('=')[1].strip()
				for line in fh.readlines() if not line.startswith('#')
			}
		if 'TOKEN' in vars_dict:
			token = vars_dict['TOKEN']
		else:
			print("Unable to get token via getenv or from .env file!")
	except FileNotFoundError:
		print("Unable to get token via getenv and no .env file found!")
		exit(1)

dc.run(token)
