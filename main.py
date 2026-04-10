import flet as ft
import json
import urllib.request
import threading
import time
import os
import uuid
import traceback

# ===================== CONFIGURATION =====================
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"

# ===================== GLOBAL STATE =====================
SONGS = []
history_stack = ["home"]
current_lang_tab = [0] # 0=Tamil, 1=Telugu
search_query = [""]
search_open = [False]

# ===================== DATA SERVICES =====================
def seed_default_songs():
    global SONGS
    SONGS = [
        {"id": "s1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே...\\nஉம்மால் எல்லாம் கூடும்."},
        {"id": "s2", "title": "பெத்தலையில் பிறந்தவரை", "language": "tamil", "lyrics": "பெத்தலையில் பிறந்தவரை...\\nபோற்றி பாடுவோம்."}
    ]

def get_filtered(lang, query=""):
    return [s for s in SONGS if s["language"] == lang and query.lower() in s["title"].lower()]

def cloud_sync():
    global SONGS
    try:
        with urllib.request.urlopen(FIRESTORE_URL) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                new_songs = []
                for doc in data.get("documents", []):
                    fields = doc.get("fields", {})
                    song_id = doc["name"].split("/")[-1]
                    new_songs.append({
                        "id": song_id,
                        "title": fields.get("title", {}).get("stringValue", "Untitled"),
                        "language": fields.get("language", {}).get("stringValue", "tamil").lower(),
                        "lyrics": fields.get("lyrics", {}).get("stringValue", "").replace("\\n", "\n"),
                        "number": fields.get("number", {}).get("stringValue", ""),
                    })
                if new_songs:
                    SONGS = new_songs
                    return len(new_songs)
    except Exception as e:
        print(f"Sync error: {e}")
    return 0

# ===================== BIBLE ENGINE =====================
class BibleManager:
    def __init__(self):
        self.selected_lang = "tamil"
        self.metadata = {"tamil": [{"name": "Adiyagamam", "chapters": 50}], "telugu": [{"name": "Adikandamu", "chapters": 50}]}
        try:
            meta_path = os.path.join(os.getcwd(), "assets", "bible", "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
        except: pass

bible_eng = BibleManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    try:
        page.title = "GGGM - Grace Lyrics"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.bgcolor = "#F5F7FA"

        # --- NAVIGATION HANDLER ---
        def on_nav_change(e):
            idx = e.control.selected_index
            if idx == 0: show_home()
            elif idx == 1: show_bible_library()
            elif idx == 2: show_settings()

        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            on_change=on_nav_change,
            selected_index=0,
            bgcolor="white",
        )

        # --- VIEW: HOME ---
        def show_home():
            nav_bar.selected_index = 0
            lang = "tamil" if current_lang_tab[0] == 0 else "telugu"
            songs = get_filtered(lang, search_query[0])
            
            # Header
            header = ft.Container(
                content=ft.Row([
                    ft.Text("GGGM", size=24, weight="bold", color="white"),
                    ft.Row([
                        ft.IconButton(ft.Icons.SEARCH, icon_color="white", on_click=lambda _: toggle_search()),
                        ft.IconButton(ft.Icons.SYNC, icon_color="white", on_click=lambda _: cloud_sync())
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#3F51B5", padding=20
            )

            # Tab Switcher
            tabs = ft.Container(
                content=ft.Row([
                    ft.ElevatedButton("Tamil", on_click=lambda _: switch_lang(0), bgcolor="#3F51B5" if current_lang_tab[0]==0 else "white", color="white" if current_lang_tab[0]==0 else "black"),
                    ft.ElevatedButton("Telugu", on_click=lambda _: switch_lang(1), bgcolor="#3F51B5" if current_lang_tab[0]==1 else "white", color="white" if current_lang_tab[0]==1 else "black"),
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10
            )

            list_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
            for s in songs:
                list_col.controls.append(
                    ft.ListTile(title=ft.Text(s["title"]), subtitle=ft.Text(s["language"]), on_click=lambda e, sid=s["id"]: show_song(sid))
                )

            page.controls.clear()
            page.navigation_bar = nav_bar
            page.add(ft.SafeArea(content=ft.Column([header, tabs, list_col], expand=True), expand=True))
            page.update()

        def switch_lang(idx):
            current_lang_tab[0] = idx
            show_home()

        def toggle_search():
            search_open[0] = not search_open[0]
            show_home()

        # --- VIEW: SONG ---
        def show_song(sid):
            song = next((s for s in SONGS if s["id"] == sid), None)
            if not song: return
            page.controls.clear()
            page.add(
                ft.SafeArea(
                    content=ft.Column([
                        ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_home()), ft.Text(song["title"], size=20)]), bgcolor="#3F51B5", padding=10),
                        ft.Container(content=ft.Text(song["lyrics"], size=18), padding=20, expand=True)
                    ], expand=True)
                )
            )
            page.update()

        # --- VIEW: BIBLE ---
        def show_bible_library():
            nav_bar.selected_index = 1
            books = bible_eng.metadata.get(bible_eng.selected_lang, [])
            
            grid = ft.GridView(expand=True, runs_count=3, spacing=10, padding=20)
            for b in books:
                grid.controls.append(
                    ft.Container(content=ft.Text(b["name"], weight="bold"), bgcolor="white", padding=20, border_radius=10, on_click=lambda e, bk=b: show_reading_view(bk, 1))
                )

            page.controls.clear()
            page.navigation_bar = nav_bar
            page.add(ft.SafeArea(content=ft.Column([ft.Container(content=ft.Text("Bible", size=24, color="white"), bgcolor="#3F51B5", padding=20), grid], expand=True), expand=True))
            page.update()

        def show_reading_view(book, chapter):
            page.controls.clear()
            # Quick Jump Strip
            jump = ft.Row(scroll=ft.ScrollMode.AUTO, controls=[
                ft.Container(content=ft.Text(str(i)), width=40, height=40, bgcolor="#3F51B5" if i==chapter else "white", on_click=lambda e, ch=i: show_reading_view(book, ch))
                for i in range(1, book.get("chapters", 20)+1)
            ])
            page.add(
                ft.SafeArea(content=ft.Column([
                    ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_bible_library()), ft.Text(f"{book['name']} {chapter}", size=20)]), bgcolor="#3F51B5", padding=10),
                    ft.Container(content=ft.Text(f"Sacred text for {book['name']} chapter {chapter}...", size=18), bgcolor="#FFF9E1", padding=20, expand=True),
                    ft.Container(content=jump, padding=10, bgcolor="white")
                ], expand=True))
            )
            page.update()

        # --- VIEW: SETTINGS ---
        def show_settings():
            nav_bar.selected_index = 2
            page.controls.clear()
            page.navigation_bar = nav_bar
            page.add(ft.SafeArea(content=ft.Column([ft.Container(content=ft.Text("Settings", size=24, color="white"), bgcolor="#3F51B5", padding=20), ft.ElevatedButton("Sync Now", on_click=lambda _: cloud_sync())])))
            page.update()

        # START
        seed_default_songs()
        show_home()
        threading.Thread(target=cloud_sync, daemon=True).start()

    except Exception as e:
        page.add(ft.Text(f"FATAL ERROR: {e}\n{traceback.format_exc()}", color="red"))
        page.update()

ft.app(target=main)
