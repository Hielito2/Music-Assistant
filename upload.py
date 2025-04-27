import argparse
import asyncio
import os
import sys
import traceback
from src.console import console as logger
from src.filechecks import FilesChecks
from src.mediaparser import MediaParser
from src.torrentcreate import Torrent
from src.torrentname import Setup


try:
    from config import config
except Exception as e:
    if not os.path.exists(f"{os.getcwd()}/config.yml"):
        print(f"Config file not found {e}")
        exit()
    else:
        print(traceback.print_exc())
class Upload:
    def __init__(self, args):
        self.args = args
        pass


    async def do_the_thing(self):
        parser = MediaParser(directory=self.args)
        data = await parser.info_parser()
        name, search_name, artist, album = await Setup(data=data).torrent_name()
        FilesChecks(name, config)
        logger.print("[bold red] Creating Torrent...")
        torrent = Torrent(self.args, config, name, artist, album)
        await torrent.create()
        await torrent.upload_torrent()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Enter directory path")
    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        logger.print(f'[red] Error: Unrecognized arguments: {unknown_args}')
        sys.exit(1)
    logger.print(f'[blue] Argument Received: {args.path}')
    upload = Upload(args=args.path)
    await upload.do_the_thing()


if __name__ == "__main__":
    asyncio.run(main())
