import time
import urllib.request
import json
from typing import List, Optional
from src.models.song import Song

PROJECT_ID = "grace-lyrics-admin"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"

# --- LOCAL STORAGE HELPER NATIVE TO FLET ANDROID ---
def _get_local_songs(page) -> List[dict]:
    val = page.client_storage.get("grace_songs")
    if val:
        try:
            return json.loads(val)
        except:
            pass
    return []

def _save_local_songs(page, songs_list: List[dict]):
    page.client_storage.set("grace_songs", json.dumps(songs_list))

def init_db(page):
    val = page.client_storage.get("grace_songs")
    if not val or val == "[]":
        tamil_lyrics = "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்? வானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\nஉமக்கொப்பனவர் யார்? உமக்கொப்பனவர் யார்? வானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\n1. செங்கடலை நீர் பிளந்து உந்தன் ஜனங்களை நடத்திச் சென்றீர்  நீர் நல்லவர் சர்வ வல்லவர் என்றும் வாக்கு மாறாதவர் (2)\n\nஉமக்கொப்பனவர் யார்? உமக்கொப்பனவர் யார்? வானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?"
        telugu_lyrics = "అగ్ని మండించు – నాలో అగ్ని మండించు (2)\nపరిశుద్ధాత్ముడా – నాలో అగ్ని మండించు (2)\n\nAgni Mandinchu – Naalo Agni Mandinchu (2)\nParishuddhaathmudaa – Naalo Agni Mandinchu (2)"
        
        seed = [
            {"id": "ta_172", "title": "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்?", "language": "tamil", "lyrics": tamil_lyrics, "number": "172", "category": "", "composer": "", "is_favorite": False, "last_cached_at": int(time.time())},
            {"id": "te_1", "title": "అగ్ని మండించు - Agni Mandinchu", "language": "telugu", "lyrics": telugu_lyrics, "number": "", "category": "", "composer": "Freddy Paul", "is_favorite": False, "last_cached_at": int(time.time())}
        ]
        _save_local_songs(page, seed)

def save_to_local_cache(page, song: Song):
    all_dicts = _get_local_songs(page)
    new_dict = {"id": song.id, "title": song.title, "language": song.language, "lyrics": song.lyrics, "number": song.number, "category": song.category, "composer": song.composer, "is_favorite": song.is_favorite, "last_cached_at": int(time.time())}
    for i, s in enumerate(all_dicts):
        if s["id"] == song.id:
            new_dict["is_favorite"] = s.get("is_favorite", False) # Preserve
            all_dicts[i] = new_dict
            _save_local_songs(page, all_dicts)
            return
    all_dicts.append(new_dict)
    _save_local_songs(page, all_dicts)

def toggle_favorite(page, song_id: str) -> bool:
    all_dicts = _get_local_songs(page)
    for s in all_dicts:
        if s["id"] == song_id:
            s["is_favorite"] = not s.get("is_favorite", False)
            _save_local_songs(page, all_dicts)
            return s["is_favorite"]
    return False

def get_songs_by_language(page, language: str, search_query: str = "") -> List[Song]:
    all_dicts = _get_local_songs(page)
    songs = []
    search_lower = search_query.lower()
    for s in all_dicts:
        if s.get("language") == language:
            if search_lower and search_lower not in s.get("title", "").lower():
                continue
            songs.append(Song(
                id=s["id"], title=s["title"], language=s["language"], 
                lyrics=s["lyrics"], number=s.get("number"), 
                category=s.get("category"), composer=s.get("composer"), 
                is_favorite=s.get("is_favorite", False)
            ))
    return sorted(songs, key=lambda x: x.title)

def get_song_by_id(page, song_id: str) -> Optional[Song]:
    all_dicts = _get_local_songs(page)
    for s in all_dicts:
        if s["id"] == song_id:
            return Song(
                id=s["id"], title=s["title"], language=s["language"], 
                lyrics=s["lyrics"], number=s.get("number"), 
                category=s.get("category"), composer=s.get("composer"), 
                is_favorite=s.get("is_favorite", False)
            )
            
    # Not found locally, fetch
    cloud_song = fetch_from_cloud_api(song_id)
    if cloud_song:
        save_to_local_cache(page, cloud_song)
        return cloud_song
    return None

def fetch_from_cloud_api(song_id: str) -> Optional[Song]:
    try:
        req = urllib.request.Request(f"{FIRESTORE_URL}/{song_id}")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                doc = json.loads(data)
                fields = doc.get('fields', {})
                return Song(
                    id=song_id,
                    title=fields.get('title', {}).get('stringValue', ''),
                    language=fields.get('language', {}).get('stringValue', ''),
                    lyrics=fields.get('lyrics', {}).get('stringValue', '').replace('\\n', '\n'),
                    number=fields.get('number', {}).get('stringValue', None),
                    category=fields.get('category', {}).get('stringValue', None),
                    composer=fields.get('composer', {}).get('stringValue', None),
                    is_favorite=False
                )
    except Exception as e:
        print(f"Network error: {e}")
    return None 

def fetch_all_from_cloud(page) -> int:
    synced_count = 0
    try:
        req = urllib.request.Request(FIRESTORE_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                parsed_data = json.loads(data)
                documents = parsed_data.get('documents', [])
                
                for doc in documents:
                    name_path = doc.get('name', '')
                    song_id = name_path.split('/')[-1]
                    fields = doc.get('fields', {})
                    song = Song(
                        id=song_id,
                        title=fields.get('title', {}).get('stringValue', ''),
                        language=fields.get('language', {}).get('stringValue', ''),
                        lyrics=fields.get('lyrics', {}).get('stringValue', '').replace('\\n', '\n'),
                        number=fields.get('number', {}).get('stringValue', None),
                        category=fields.get('category', {}).get('stringValue', None),
                        composer=fields.get('composer', {}).get('stringValue', None),
                        is_favorite=False
                    )
                    save_to_local_cache(page, song)
                    synced_count += 1
    except Exception as e:
        print(f"Sync error: {e}")
    return synced_count
