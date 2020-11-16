from pathlib import Path

def get_title(p: Path):
    return p.stem

def get_album_name(p: Path):
    return p.parent.name

def get_artist_name(p: Path):
    return p.parent.parent.name
