import os
from re import search
import discord
import requests

dc = discord.Client()


@dc.event
async def on_ready():
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


@dc.event
async def on_message(message:discord.Message):
	if message.author == dc.user:
		return
	if "picrew" in message.channel.name.lower() and message.content == "search"\
			and message.reference is not None:
		message = await message.channel.fetch_message(message.reference.message_id)
		if message is None:
			return
		if message.attachments is not None:
			for attachment in message.attachments:
				# example file name: 1011016_hbWCv9R5.png
				if m := search(r"^(\d+)_.+\.png$", attachment.filename):
					r = requests.get("https://picrew.me/image_maker/{}".format(m.group(1)))
					if r.ok:
						await message.channel.send(
							"here: https://picrew.me/image_maker/{}".format(m.group(1))
						)
					else:
						await message.channel.send(
							"sadly got a {} :( picrew id: {}".format(r.status_code,m.group(1)),
							# )
							delete_after=5
						)
				else:
					await message.channel.send(
						"Unable to get picrew id, sorry :(.",
						delete_after=5
					)
					# )
				return
	if dc.user in message.mentions and "invite" in message.content.lower():
		await message.channel.send(
			discord.utils.oauth_url(dc.user.id, discord.Permissions(68608))
		)


@dc.event
async def on_reaction_add(reaction:discord.Reaction, user:discord.User):
	if "picrew" in reaction.message.channel.name.lower()\
			and reaction.emoji == "🔍" and reaction.message.attachments is not None:
		message = reaction.message
		for attachment in message.attachments:
			# example file name: 1011016_hbWCv9R5.png
			if m := search(r"^(\d+)_.+\.png$", attachment.filename):
				r = requests.get("https://picrew.me/image_maker/{}".format(m.group(1)))
				if r.ok:
					if user.permissions_in(message.channel).send_messages:
						await message.channel.send(
							"here: https://picrew.me/image_maker/{}".format(m.group(1)),
							reference=message
						)
					else:
						await message.channel.send(
							"here: https://picrew.me/image_maker/{}".format(m.group(1)),
							reference=message,
							delete_after=5
						)
				else:
					await message.channel.send(
						"sadly got a {} :( picrew id: {}".format(r.status_code,m.group(1)),
						# )
						reference=message,
						delete_after=5
					)
			else:
				await message.channel.send(
					"Unable to get picrew id, sorry :(.",
					delete_after=5
				)
				# )
			return

dc.run(os.getenv("TOKEN"))
