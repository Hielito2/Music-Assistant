from datetime import datetime
import time
import os
import requests
from bs4 import BeautifulSoup
import re
from src.console import console as logger
from torf import Torrent as makeTorrent
import httpx
import platform

from src.imageprocessing import ProcessImage


class Torrent:
    def __init__(self, path, config, name, artist, album):
        self.path = path
        self.config = config
        self.name = name
        self.artist = artist
        self.album = album

    async def create(self):
        start_time = time.time()
        torrent = makeTorrent(path=self.path, trackers=self.config.tracker_announce, creation_date=datetime.now(), private=True, source=self.config.source, created_by='Music assistant', comment="Created with Music Assistant")
        torrent.generate(interval=5)
        torrent.write(f'{os.getcwd()}/tmp/{self.name}/{self.name}.torrent', overwrite=True)
        torrent.verify_filesize(self.path)
        finish_time = time.time()
        logger.print(f"torrent created in {finish_time - start_time:.4f} seconds")

    async def upload_torrent(self):
        torrent_bin = open(f'{os.getcwd()}/tmp/{self.name}/{self.name}.torrent', 'rb')
        desc = open(f"{os.getcwd()}/tmp/{self.name}/DESCRIPTION.txt", 'r', encoding='utf-8').read()
        files = {"torrent": torrent_bin}
        data = {
            "name": self.name,
            "description": desc,
            'category_id': self.config.category_id,
            'type_id': self.config.type_id,
            'personal_release': True,
            'internal': 0,
            'featured': 0,
            'free': 0,
            'doubleup': 0,
            'sticky':   0,
            'anonymous': True,
            'tmdb':     0,
            'imdb':     0,
            'tvdb':     0,
            'mal':      0,
            'igdb':     0,
            'sd':       0,
            'stream': 0,
        }
        params = {
            "api_token": self.config.api_token
        }
        headers = {
            'User-Agent': f'Music Assistant/2.2 ({platform.system()} {platform.release()})'
        }
        patched = await self.patch_torrent('torrent_id', desc)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.config.upload_api, files=files, data=data, headers=headers, params=params)
            if response.status_code == 200:
                time.sleep(1)
                res_json = response.json()
                match = re.search(r"/download/([^.]*)",res_json['data'])
                if match:
                    torrent_id = match.group(1)
                else:
                    logger.print(f"[red] Not match in upload_torrent")
                    return
                torrent_bin.close()
                logger.print(f"[yellow] Torrent URL: {res_json['data']}")
                logger.print(f"[yellow] Created torrent with ID: {torrent_id}")
                patched = await self.patch_torrent(torrent_id, desc)
                if not patched:
                    logger.print("Unable to patch torrent, check the site.")
                else:
                    logger.print("Torrent published and automatically patched.")
            else:
                logger.print("Torrent Not Uploaded.")



    async def patch_torrent(self, torrent_id, desc):
        _hasimage = await ProcessImage(self.path, name=self.name, artist=self.artist, album=self.album).img_path()
        if not _hasimage:
            logger.print(f'[bold orange] Make sure theres a Cover.jpg|Cover.png|Cover.jpeg on the directory')
            return False
        else:
            _csrf_token = await self.parse_csrf_token(torrent_id)
            files = {
                'torrent-cover': ('cover.png', open(f'{os.getcwd()}/tmp/{self.name}/cover.png', 'rb'), 'image/png]'),
            }
            headers = {
                'User-Agent': f'Music Assistant/2.2 ({platform.system()} {platform.release()})'
            }
            cookies = {
                "laravel_cookie_consent": "1",
                "XSRF-TOKEN": self.config.XSRF_TOKEN,
                "laravel_session": self.config.session_token,
            }
            data = {
                "_token": _csrf_token,
                "_method": "PATCH",
                "name": str(self.name),
                "category_id": str(self.config.category_id),
                "type_id": str(self.config.type_id),
                "tmdb_movie_id": "0",
                "tmdb_tv_id": "0",
                "imdb": "0",
                "tvdb": "0",
                "mal": "0",
                "igdb": "0",
                "anon": "0",
                "internal": "0",
                "description": desc,
                "personal_release": "0",
            }
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(f'{self.config.torrents_url}/{torrent_id}', files=files, data=data, headers=headers, cookies=cookies)
                    print(response)
                    if response.status_code == 413:
                        # fallback to deezer api
                        # logger.print(f" Artists : {self.artist.lower()}, Album {self.album.lower()}")
                        logger.print("Cover image size is too large. Cover not uploaded")
                return True
            except BaseException as e:
                logger.print(f"[bold red] Critical Error {e} [/bold red]")
                return None

    async def parse_csrf_token(self, torrent_id):
        cookies = {
            "laravel_cookie_consent": "1",
            "XSRF-TOKEN": self.config.XSRF_TOKEN,
            "laravel_session": self.config.session_token,
        }
        try:
            response = requests.get(f'{self.config.torrents_url}/{torrent_id}', cookies=cookies)
            parsed = BeautifulSoup(response.text, 'html.parser')
            token = parsed.find("meta", attrs={"name": "csrf-token"})['content']
            return token
        except BaseException as e:
            logger.print(f'[bold red]Something went wrong {e}[/bold red]')
            return None
