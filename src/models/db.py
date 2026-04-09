import time
import os
import json
import urllib.request
from typing import List, Optional
from src.models.song import Song

# Cloudflare Sync Config
FIRESTORE_URL = "https://gggm-admin.rajhanoch24.workers.dev"
SYNC_URL = f"{FIRESTORE_URL}/songs"

# Find a writable directory - try multiple fallbacks
def _get_data_file():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs.json"),
        os.path.join(os.getcwd(), "songs.json"),
        os.path.join(os.path.expanduser("~"), "songs.json"),
    ]
    for path in candidates:
        try:
            d = os.path.dirname(path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            # Quick write test
            with open(path, "a", encoding="utf-8") as f:
                pass
            return path
        except:
            continue
    return candidates[0]

DATA_FILE = _get_data_file()

def _load_all() -> List[dict]:
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def _save_all(data: List[dict]):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass

def init_db():
    data = _load_all()
    if len(data) == 0:
        seed = [
            {"id": "ta_172", "title": "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்?", "language": "tamil", "number": "172", "category": "", "composer": "", "is_favorite": False,
             "lyrics": "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்?\nவானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\nஉமக்கொப்பனவர் யார்? உமக்கொப்பனவர் யார்?\nவானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\n1. செங்கடலை நீர் பிளந்து\nஉந்தன் ஜனங்களை நடத்திச் சென்றீர்\nநீர் நல்லவர் சர்வ வல்லவர்\nஎன்றும் வாக்கு மாறாதவர் (2)\n\n2. தூதர்கள் உண்ணும் உணவால்\nஉந்தன் ஜனங்களை போஷித்தீரே\nஉம்மைப்போல யாருண்டு\nஇந்த ஜனங்களை நேசித்திட (2)\n\n3. கன்மலையை நீர் பிளந்து\nஉந்தன் ஜனங்களின் தாகம் தீர்த்தீர்\nஉந்தன் நாமம் அதிசயம்\nஇன்றும் அற்புதம் செய்திடுவீர் (2)"},
            {"id": "te_1", "title": "అగ్ని మండించు - Agni Mandinchu", "language": "telugu", "number": "", "category": "", "composer": "Freddy Paul", "is_favorite": False,
             "lyrics": "అగ్ని మండించు – నాలో అగ్ని మండించు (2)\nపరిశుద్ధాత్ముడా – నాలో అగ్ని మండించు (2)\n\nAgni Mandinchu – Naalo Agni Mandinchu (2)\nParishuddhaathmudaa – Naalo Agni Mandinchu (2)"}
        ]
        _save_all(seed)

def save_to_local_cache(song: Song):
    data = _load_all()
    d = {"id": song.id, "title": song.title, "language": song.language, "lyrics": song.lyrics, "number": song.number or "", "category": song.category or "", "composer": song.composer or "", "is_favorite": song.is_favorite}
    for i, s in enumerate(data):
        if s["id"] == song.id:
            d["is_favorite"] = s.get("is_favorite", False)
            data[i] = d
            _save_all(data)
            return
    data.append(d)
    _save_all(data)

def toggle_favorite(song_id: str) -> bool:
    data = _load_all()
    for s in data:
        if s["id"] == song_id:
            s["is_favorite"] = not s.get("is_favorite", False)
            _save_all(data)
            return s["is_favorite"]
    return False

def get_songs_by_language(language: str, search_query: str = "") -> List[Song]:
    data = _load_all()
    songs = []
    sq = search_query.lower()
    for s in data:
        if s.get("language") == language:
            if sq and sq not in s.get("title", "").lower():
                continue
            songs.append(Song(id=s["id"], title=s["title"], language=s["language"], lyrics=s["lyrics"], number=s.get("number"), category=s.get("category"), composer=s.get("composer"), is_favorite=s.get("is_favorite", False)))
    return sorted(songs, key=lambda x: x.title)

def get_song_by_id(song_id: str) -> Optional[Song]:
    data = _load_all()
    for s in data:
        if s["id"] == song_id:
            return Song(id=s["id"], title=s["title"], language=s["language"], lyrics=s["lyrics"], number=s.get("number"), category=s.get("category"), composer=s.get("composer"), is_favorite=s.get("is_favorite", False))
    cloud = fetch_from_cloud_api(song_id)
    if cloud:
        save_to_local_cache(cloud)
        return cloud
    return None

def fetch_all_from_cloud() -> int:
    """Fetches all songs from Cloudflare Remote API and saves them locally."""
    try:
        # We use a clean urllib request to hit the Cloudflare Worker
        with urllib.request.urlopen(SYNC_URL, timeout=10) as response:
            if response.status == 200:
                cloud_data = json.loads(response.read().decode("utf-8"))
                if isinstance(cloud_data, list):
                    # We preserve favorites when syncing
                    current_data = _load_all()
                    favorites = {s["id"] for s in current_data if s.get("is_favorite")}
                    
                    final_songs = []
                    for s in cloud_data:
                        # Extract data from the Cloudflare schema
                        song_dict = {
                            "id": str(s.get("id")),
                            "title": s.get("title", ""),
                            "language": s.get("language", "tamil"),
                            "lyrics": s.get("lyrics", ""),
                            "number": s.get("number", ""),
                            "category": s.get("category", ""),
                            "composer": s.get("composer", ""),
                            "is_favorite": str(s.get("id")) in favorites
                        }
                        final_songs.append(song_dict)
                    
                    _save_all(final_songs)
                    return len(final_songs)
    except Exception as e:
        print(f"Sync error: {e}")
        raise e
    return 0

def fetch_from_cloud_api(song_id: str) -> Optional[Song]:
    # Individual lookup is handled by global sync in this version
    return None
