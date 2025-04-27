import os
from pathlib import Path


class Setup:
    def __init__(self, data):
        self.data = data
    async def torrent_name(self):
        sampling = ''
        artist = self.data[0]['Artist']
        album = self.data[0]['Album_Title']
        track_format = self.data[0]['Format']
        bits = self.data[0]['Bits']
        match self.data[0]['Sampling']:
            case '44100':
                sampling = '44.1kHz'
            case '48000':
                sampling = '48kHz'
            case '24000':
                sampling = '24khZ'
            case '96000':
                sampling = '96kHz'
        torrent_name = f'{artist} {album} {track_format} {bits}bits {sampling}'
        search_name = f'{artist} {album}'
        await self.create_tmp_dir(torrent_name)
        await self.descprtion(torrent_name)
        return torrent_name, search_name, artist, album
    
    async def descprtion(self, name):
        track_sampling = ''
        with open(f'{os.getcwd()}/tmp/{name}/DESCRIPTION.txt', 'w') as desc:
            desc.write("[table][tr][th] Artists [/th][th] Song Name [/th][th] Track # [/th][th] Format [/th][th] Duration [/th][th] Sampling [/th][th] Bits [/th][/tr]")
        #print(self.data)
        for track in self.data:
            track_artist = track['Artist']
            track_name = track['Track_Title']
            track_number = track['Track_Number']
            track_format = track['Format']
            track_duration = track['Duration']
            match track['Sampling']:
                case '44100':
                    track_sampling = '44.1kHz'
                case '48000':
                    track_sampling = '48kHz'
                case '24000':
                    track_sampling = '24khZ'
                case '96000':
                    track_sampling = '96kHz'
            track_bits = track['Bits']
            with open(f'{os.getcwd()}/tmp/{name}/DESCRIPTION.txt', 'a') as desc:
                desc.write(f'[tr][td]{track_artist}[/td]  [td]{track_name} [/td] [td]{track_number} [/td] [td]{track_format}[/td] [td] {track_duration} [/td] [td] {track_sampling} [/td] [td] {track_bits} [/td][/tr]')
        with open(f'{os.getcwd()}/tmp/{name}/DESCRIPTION.txt', 'a') as desc:
            desc.write('[/table]')
    @staticmethod
    async def create_tmp_dir(name):
        Path(f'{Path.cwd()}/tmp/{name}').mkdir(parents=True, exist_ok=True)