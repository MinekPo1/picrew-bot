import os
from re import search
import discord

dc = discord.Client()


@dc.event
async def on_ready():
	channel = dc.get_channel("805214055643349003")
	if channel is not None:
		channel.send("Bot is online!")
	else:
		print("Unable to access channel!")
	print("logged in as {}".format(dc.user))


@dc.event
async def on_message(message:discord.Message):
	if message.author == dc.user:
		return
	if "picrew" in message.channel.name and message.content == "search"\
			and message.reference is not None:
		message = await message.channel.fetch_message(message.reference.message_id)
		if message is None:
			return
		if message.attachments is not None:
			for attachment in message.attachments:
				# example file name: 1011016_hbWCv9R5.png
				if m := search(r"^\d{7}_.{8}\.png$", attachment.filename):
					await message.channel.send(
						"https://picrew.me/image_maker/{}".format(m.group(0))
					)
					return
				else:
					await message.channel.send("Unable to get picrew id, sorry :(.")


dc.run(os.getenv("TOKEN"))
