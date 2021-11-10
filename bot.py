#import logging
import os
import signal
import ffmpeg  
from pyrogram import Client, filters
from pytgcalls import GroupCall




API_ID = int(os.environ.get("API_ID",7395896))
API_HASH = os.environ.get("API_HASH","cd3998ddf318dad74d7c506731bc0abc")
SESSION_NAME = os.environ.get("SESSION_NAME","BQCzsuXwrGOtlF7CcoNO-WZTp1FVuIi_W7-2ZCShKj0nz7fFfXJMPDgnchpmqSMsNiJJoDsNLqRbGenptmdY52L72WCQLqNBnku8Wf-24X9hGfNy3Sbm3gneTyZ24svIX9lt8CYdBgQGMAkwZVSDAEEz7q8nRyd6NAC7Z2azw3ffDmVhqQmCw8NakaD0Zsylrv1WTlqN_uHbPHJdsonwwyEP1EPie-5SFWCBfe_31djSET3x2WjRB0xmefxPGkxCybJLUEUPv9ouP0hytTaBZzVS3Pj_Vog3CuowJW2DTvIphaAZiW0Eykr2wg3ePqHvCgCEwTNdm7wP1rfhpdGrKZvKbN33ZwA")


app = Client(SESSION_NAME, API_ID, API_HASH)
#logging.basicConfig(level=logging.INFO)



HELP =""" Radio stations:

1. https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8

2. https://filmymirchihdliv-lh.akamaihd.net/i/FilmyMirchiHDLive_1_1@336266/master.m3u8


To start replay to this message with command !start <ID>
To stop use !stop command"""


GROUP_CALLS = {}
FFMPEG_PROCESSES = {}

@app.on_message(filters.command('help',prefixes='!'))
async def help(client,message):
	get =await client.get_chat_member(message.chat.id,message.from_user.id)
	status = get. status
	cmd_user = ["administrator","creator"]
	if status in cmd_user:
		await message.reply_text(HELP)


@app.on_message(filters.command('start', prefixes='!'))
async def start(client,message):
	get =await client.get_chat_member(message.chat.id,message.from_user.id)
	status = get. status
	cmd_user = ["administrator","creator"]
	if status in cmd_user:
		input_filename = f'radio-{message.chat.id}.raw'
		group_call = GROUP_CALLS.get(message.chat.id)
		if group_call is None:
		      group_call = GroupCall(client, input_filename, path_to_log_file='')
		      GROUP_CALLS[message.chat.id] = group_call
		if not message.reply_to_message or len(message.command) < 2:
		      await message.reply_text('You forgot to replay list of stations or pass a station ID')
		      return
	process = FFMPEG_PROCESSES.get(message.chat.id)
	if process:
		process.send_signal(signal.SIGTERM)
	station_stream_url = None
	station_id = message.command[1]
	msg_lines = message.reply_to_message.text.split('\n')
	for line in msg_lines:
	       line_prefix = f'{station_id}. '
	       if line.startswith(line_prefix):
	           station_stream_url = line.replace(line_prefix, '').replace('\n', '')
	           break
	if not station_stream_url:
	       await message.reply_text(f'Can\'t find a station with id {station_id}')
	       return
	await group_call.start(message.chat.id)
	process = ffmpeg.input(station_stream_url).output(        input_filename, format='s16le',       acodec='pcm_s16le', ac=2, ar='48k'  ).overwrite_output().run_async()
	FFMPEG_PROCESSES[message.chat.id] = process
	await message.reply_text(f'Radio #{station_id} is playing...')


@app.on_message( filters.command('stop', prefixes='!'))
async def stop(client,message):
	get =await client.get_chat_member(message.chat.id,message.from_user.id)
	status = get. status
	cmd_user = ["administrator","creator"]
	if status in cmd_user:
	   group_call = GROUP_CALLS.get(message.chat.id)
	   if group_call:
	   	await group_call.stop()
	   process = FFMPEG_PROCESSES.get(message.chat.id)
	   if process:
	   	process.send_signal(signal.SIGTERM)
	   





app.run()

