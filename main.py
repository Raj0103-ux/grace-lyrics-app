import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
# UPDATED: Using the correct project ID provided by user
PROJECT_ID = "grace-lyrics-admin"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"

# ===================== DATA MANAGER =====================
class LyricsManager:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass

    def sync_cloud(self, callback):
        def _task():
            try:
                all_songs = []
                next_token = None
                
                # UNLIMITED SYNC LOOP (Handles more than 20 songs)
                while True:
                    url = BASE_URL
                    if next_token: url += f"?pageToken={next_token}"
                    
                    with urllib.request.urlopen(url) as r:
                        d = json.load(r)
                        for doc in d.get("documents", []):
                            f = doc.get("fields", {})
                            # Support both 'lyrics' and 'Lyric' field names for robustness
                            lyrics_raw = f.get("lyrics", f.get("Lyric", {})).get("stringValue", "")
                            all_songs.append({
                                "title": f.get("title", f.get("Title", {})).get("stringValue", "No Title"),
                                "lyrics": lyrics_raw,
                                "language": f.get("language", f.get("Language", {})).get("stringValue", "tamil").lower()
                            })
                        
                        next_token = d.get("nextPageToken")
                        if not next_token: break # No more pages

                self.songs = all_songs
                with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(all_songs, out)
                callback(len(all_songs))
            except Exception as e:
                print(f"Sync Err: {e}")
                callback(-1)
        threading.Thread(target=_task).start()

lm = LyricsManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    page.title = "Grace Hub Admin-Direct"
    page.bgcolor = "#F5F5F5"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # APP STATE
    state = {"lang": "tamil", "q": "", "font_size": 22}

    # GLOBAL UI REFS
    list_body = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
    search_bar = ft.TextField(
        hint_text="Search songs...", expand=True, bgcolor="white",
        border_radius=12, border_color="transparent", prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_songs(e.control.value)
    )

    def filter_songs(q=""):
        state["q"] = q
        list_body.controls.clear()
        results = [s for s in lm.songs if s["language"] == state["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_body.controls.append(ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MUSIC_NOTE, color="#1A237E"),
                    title=ft.Text(s["title"], weight="bold", color="black"),
                    on_click=lambda e, song=s: show_reader(song)
                ),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#E8EAF6"), margin=ft.margin.symmetric(vertical=4),
                shadow=ft.BoxShadow(blur_radius=10, color="#10000000", offset=ft.Offset(0, 4))
            ))
        page.update()

    def show_reader(s):
        page.clean()
        page.bgcolor = "#FFF9E1" # Parchment Theme
        
        # ZOOMABLE LIST BODY
        v_list = ft.ListView(expand=True, padding=30)
        
        def refresh_zoom():
            v_list.controls.clear()
            for line in s["lyrics"].split("\n"):
                if line.strip(): v_list.controls.append(ft.Text(line, size=state["font_size"], color="#2C3E50", weight="500"))
                else: v_list.controls.append(ft.Container(height=15))
            page.update()

        # ZOOM ACTIONS
        def zoom(delta):
            state["font_size"] = max(14, min(40, state["font_size"] + delta))
            refresh_zoom()

        page.appbar = ft.AppBar(
            title=ft.Text(s["title"], color="white"),
            bgcolor="#1A237E",
            leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home()),
            actions=[
                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(-2)),
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(2)),
            ]
        )
        refresh_zoom()
        page.add(v_list)
        page.update()

    def show_settings():
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("Settings", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home()))
        page.bgcolor = "#F5F5F5"
        
        def sync_action(e):
            e.control.disabled = True; page.update()
            lm.sync_cloud(lambda count: (
                page.show_snack_bar(ft.SnackBar(ft.Text(f"Success! {count} songs synced." if count >= 0 else "Sync Failed! Check connection."))),
                render_home()
            ))

        page.add(ft.Container(padding=30, content=ft.Column([
            ft.Text("Cloud Sync", size=24, weight="bold", color="black"),
            ft.Text("Project: grace-lyrics-admin", size=14, color="grey"),
            ft.Container(height=20),
            ft.ElevatedButton("SYNC NOW", icon=ft.Icons.SYNC, bgcolor="#1A237E", color="white", on_click=sync_action, height=50),
            ft.Divider(height=40),
            ft.Text("v5.1.0 Admin Edition", color="grey", size=11)
        ])))
        page.update()

    def render_home():
        page.clean()
        page.bgcolor = "#F5F5F5"
        
        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Row([ft.Image(src="icon.png", width=40, height=40), ft.Text("Grace Lyrics", color="white", size=24, weight="bold")]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: show_settings())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([ft.Container(content=search_bar, expand=True)])
            ])
        )

        lang_row = ft.Container(padding=15, content=ft.Row([
            ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if state["lang"]=="tamil" else "white", color="#1A237E" if state["lang"]=="tamil" else "grey", on_click=lambda _: (state.update({"lang": "tamil"}), filter_songs())),
            ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if state["lang"]=="telugu" else "white", color="#1A237E" if state["lang"]=="telugu" else "grey", on_click=lambda _: (state.update({"lang": "telugu"}), filter_songs())),
        ], spacing=15))

        page.add(header, lang_row, list_body)
        filter_songs(state["q"])

    render_home()

ft.app(target=main)
