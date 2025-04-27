from pathlib import Path
from src.console import console as logger


class FilesChecks:
    def __init__(self, name, config):
        self.name = name
        self.config = config

    async def check_tmp_directory(self):
        tmp = Path.cwd() / f'tmp'
        tmp.mkdir(parents=True, exist_ok=True)
        excluded_extensions = {'.jpg', '.jpeg', '.png', '.lrc', '.cue'}
        tmp_dir = Path.cwd() / f"tmp/{self.name}"
        files = [entry.name for entry in tmp_dir.iterdir() if
                 entry.is_file() and not entry.suffix.lower() in excluded_extensions]
        if f'{self.name}.torrent' in files:
            return True
        return False



