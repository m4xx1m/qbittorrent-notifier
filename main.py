import os
import sys
import aiogram
import asyncio
import argparse
import humanize
import xmltodict
import traceback

DEFAULT_TEXT = "[qBittorrent] '{torrent_name}' has finished downloading\n\nTorrent name: {torrent_name}\nTorrent size: {torrent_size}\nSave path:    {content_path}"
parser = argparse.ArgumentParser()

# Script args
parser.add_argument("--config", default="config.xml", help="Path to xml config file")
parser.add_argument("--text", default=DEFAULT_TEXT, help="Text to be sent to chat")
parser.add_argument("--bot_token", default=None, help="Bot token from @botfather")
parser.add_argument("--send_to", default=None, help="Telegram chat ID of the chat to which the text will be sent")
parser.add_argument("--silent", default=False, help="Notofy without sound")
# qBittorrent args
parser.add_argument("-N", default=None, help="Torrent name")
parser.add_argument("-L", default=None, help="Category")
parser.add_argument("-G", default=None, help="Tags (separated by comma)")
parser.add_argument("-F", default=None, help="Content path (same as root path for multifile torrent)")
parser.add_argument("-R", default=None, help="Root path (first torrent subdirectory path)")
parser.add_argument("-D", default=None, help="Save path")
parser.add_argument("-C", default=None, help="Number of files")
parser.add_argument("-Z", default=0, help="Torrent size (bytes)")
parser.add_argument("-T", default=None, help="Current tracker")
parser.add_argument("-I", default=None, help="Info hash")

args = parser.parse_args()
config = None if not os.path.exists(args.config) \
                else dict(xmltodict.parse(open(args.config, "r", encoding="utf=8").read())["data"])

if config:
    # BOT_TOKEN
    if "BOT_TOKEN" not in config:
        if not args.text:
            print('Bot token doesn\'t set')
            exit(-1)
        else:
            BOT_TOKEN = args.bot_token
    else:
        BOT_TOKEN = config["BOT_TOKEN"]

    # TEXT
    if "TEXT" not in config:
        if not args.text:
            print('Text doesn\'t set')
            exit(-1)
        else:
            TEXT = args.text
    else:
        TEXT = config["TEXT"]

    # SEND_TO
    if "SEND_TO" not in config:
        if not args.text:
            print('Sent to chat doesn\'t set')
            exit(-1)
        else:
            SEND_TO = args.send_to
    else:
        SEND_TO = config["SEND_TO"]

    # SILENT_MESSAGE
    try:
        SILENT = True if int(config["SILENT_MESSAGE"]) else False
    except:
        if args.silent is None:
            print(f"Error getting SILENT_MESSAGE param from {args.config}")
            SILENT = False
        else:
            SILENT = bool(args.silent)


elif config is None:
    if not args.bot_token or not args.text or not args.send_to:
        print("Failed to get configuration")
        exit(-1)

    BOT_TOKEN = args.bot_token
    TEXT = args.text
    SEND_TO = args.send_to
    SILENT = args.silent

else:
    print("Failed to get args")
    exit(-1)

bot = aiogram.Bot(token=BOT_TOKEN)
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(
        bot.send_message(
            chat_id=SEND_TO,
            text=TEXT.format(
                torrent_name=args.N,
                category=args.L,
                tags=args.G,
                content_path=args.F,
                root_path=args.R,
                save_path=args.D,
                number_of_files=args.C,
                torrent_size=humanize.naturalsize(args.Z, binary=True),  # from bytes to GB/MB/KB
                current_tracker=args.T,
                info_hash=args.I
            ),
            disable_notification=SILENT
        )
    )

except aiogram.exceptions.ChatNotFound:
    print(f"Chat {SEND_TO} not found")

except aiogram.exceptions.Unauthorized:
    print("Bot unauthorized")

except Exception as err:
    try:
        exc = sys.exc_info()
        exc = "".join(traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next))
    except:
        exc = err
    print(exc)


else:
    print("Notify was sended successfully")

finally:
    loop.run_until_complete(
        bot.session.close()
    )
    exit(0)
