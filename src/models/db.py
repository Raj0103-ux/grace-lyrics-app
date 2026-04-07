import sqlite3
import os
import time
import urllib.request
import json
from typing import List, Optional
from src.models.song import Song

DB_PATH = os.path.join(os.path.dirname(__file__), 'grace_lyrics.db')

# Firebase Firestore Configuration
PROJECT_ID = "grace-lyrics-admin"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            language TEXT NOT NULL,
            lyrics TEXT NOT NULL,
            number TEXT,
            category TEXT,
            composer TEXT,
            is_favorite BOOLEAN DEFAULT 0,
            last_cached_at INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_to_local_cache(song: Song):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO songs 
        (id, title, language, lyrics, number, category, composer, is_favorite, last_cached_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (song.id, song.title, song.language, song.lyrics, song.number, 
          song.category, song.composer, song.is_favorite, int(time.time())))
    conn.commit()
    conn.close()

def toggle_favorite(song_id: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT is_favorite FROM songs WHERE id = ?', (song_id,))
    row = c.fetchone()
    if row:
        new_status = not bool(row[0])
        c.execute('UPDATE songs SET is_favorite = ? WHERE id = ?', (new_status, song_id))
        conn.commit()
        conn.close()
        return new_status
    conn.close()
    return False

def get_songs_by_language(language: str, search_query: str = "") -> List[Song]:
    conn = get_connection()
    c = conn.cursor()
    
    if search_query:
        c.execute('SELECT * FROM songs WHERE language = ? AND title LIKE ? ORDER BY title', (language, f'%{search_query}%'))
    else:
        c.execute('SELECT * FROM songs WHERE language = ? ORDER BY title', (language,))
        
    rows = c.fetchall()
    conn.close()
    
    songs = []
    for r in rows:
        songs.append(Song(
            id=r[0], title=r[1], language=r[2], lyrics=r[3], 
            number=r[4], category=r[5], composer=r[6], is_favorite=bool(r[7])
        ))
    return songs

# --- LIVE FIREBASE INTEGRATION USING STANDARD LIBRARY (urllib) ---
def fetch_from_cloud_api(song_id: str) -> Optional[Song]:
    print(f"--> [NETWORK] Fetching {song_id} from Firebase...")
    try:
        req = urllib.request.Request(f"{FIRESTORE_URL}/{song_id}")
        with urllib.request.urlopen(req) as response:
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
        print(f"--> [NETWORK EXCEPTION] {e}")
        
    return None 

def fetch_all_from_cloud() -> int:
    print("--> [NETWORK] Syncing all master data from Firebase...")
    synced_count = 0
    try:
        req = urllib.request.Request(FIRESTORE_URL)
        with urllib.request.urlopen(req) as response:
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
                    
                    save_to_local_cache(song)
                    synced_count += 1
                    
                print(f"--> [SYNC COMPLETE] Downloaded {synced_count} songs locally.")
    except Exception as e:
        print(f"--> [SYNC EXCEPTION] {e}")
        
    return synced_count

def get_song_by_id(song_id: str) -> Optional[Song]:
    # 1. Local Cache Check
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
    r = c.fetchone()
    conn.close()
    
    if r:
        print(f"--> [LOCAL] Cache hit for {song_id}")
        return Song(
            id=r[0], title=r[1], language=r[2], lyrics=r[3], 
            number=r[4], category=r[5], composer=r[6], is_favorite=bool(r[7])
        )
        
    # 2. Network Fetch 
    print(f"--> [CACHE MISS] Song {song_id} not locally found.")
    cloud_song = fetch_from_cloud_api(song_id)
    
    if cloud_song:
        save_to_local_cache(cloud_song)
        return cloud_song
        
    return None

init_db()
