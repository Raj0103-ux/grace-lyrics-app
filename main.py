import flet as ft
import json
import urllib.request
import threading
import os
import traceback

# ===================== CONFIG =====================
DB_PATH = "songs.json"
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
                all_songs = [] ; next_token = None
                while True:
                    url = BASE_URL
                    if next_token: url += f"?pageToken={next_token}"
                    with urllib.request.urlopen(url) as r:
                        d = json.load(r)
                        for doc in d.get("documents", []):
                            f = doc.get("fields", {})
                            raw_lyrics = f.get("lyrics", f.get("Lyric", {})).get("stringValue", "")
                            clean_lyrics = raw_lyrics.replace("\\n", "\n").replace("\\r", "\n").replace("\r\n", "\n")
                            all_songs.append({
                                "title": f.get("title", f.get("Title", {})).get("stringValue", "No Title"),
                                "lyrics": clean_lyrics,
                                "language": f.get("language", f.get("Language", {})).get("stringValue", "tamil").lower()
                            })
                        next_token = d.get("nextPageToken")
                        if not next_token: break
                self.songs = all_songs
                with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(all_songs, out)
                callback(len(all_songs))
            except: callback(-1)
        threading.Thread(target=_task).start()

lm = LyricsManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    try:
        page.assets_dir = "assets"
        page.title = "GGGM"
        page.bgcolor = "#F5F5F5"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        st = {"lang": "tamil", "q": "", "font_size": 22}
        page.appbar = ft.AppBar(visible=False)
        
        # PERSISTENT STRUCTURE
        song_list = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
        
        def filter_songs(q=None):
            if q is not None: st["q"] = q
            song_list.controls.clear()
            
            # Smart Search: Check Title OR Lyrics content
            query = st["q"].lower()
            results = [s for s in lm.songs if s["language"] == st["lang"] and (query in s["title"].lower() or query in s["lyrics"].lower())]
            
            for s in results:
                # Option 1: Dual View (Subtitle shows English preview of lyrics)
                preview = s["lyrics"].split("\n")[0][:40] + "..." if len(s["lyrics"]) > 0 else ""
                
                song_list.controls.append(ft.Container(
                    content=ft.ListTile(
                        leading=ft.Image(src="icon.png", width=30, height=30, error_content=ft.Icon(ft.Icons.MUSIC_NOTE)),
                        title=ft.Text(s["title"], weight="bold", color="black"),
                        subtitle=ft.Text(preview, size=12, color="grey"), # Show English preview for Romanized lyrics
                        on_click=lambda e, song=s: show_reader(song)
                    ),
                    bgcolor="white", border_radius=12, margin=ft.margin.symmetric(vertical=4),
                    shadow=ft.BoxShadow(blur_radius=10, color="#10000000")
                ))
            page.update()

        # FIXED HEADER (Never destroyed during search)
        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Image(src="icon.png", width=50, height=50, error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color="white")), 
                        ft.Text("GGGM", color="white", size=24, weight="bold")
                    ]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: show_settings())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.TextField(hint_text="Search title or lyrics...", expand=True, bgcolor="white", border_radius=12, border_color="transparent", prefix_icon=ft.Icons.SEARCH, on_change=lambda e: filter_songs(e.control.value))
            ])
        )
        
        lang_row = ft.Container(padding=15, content=ft.Row([
            ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if st["lang"]=="tamil" else "white", color="#1A237E" if st["lang"]=="tamil" else "grey", on_click=lambda e: change_lang("tamil")), 
            ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if st["lang"]=="telugu" else "white", color="#1A237E" if st["lang"]=="telugu" else "grey", on_click=lambda e: change_lang("telugu"))
        ], spacing=15))

        def change_lang(l):
            st["lang"] = l
            # Instant Visual Feedback
            for btn in lang_row.content.controls:
                btn.bgcolor = "#E8EAF6" if btn.text.lower() == l else "white"
                btn.color = "#1A237E" if btn.text.lower() == l else "grey"
            
            # FORCE REFRESH: Clear the container first to force the phone to re-draw
            song_list.controls.clear()
            page.update() # First update shows it's clearing
            filter_songs() # Second update brings in the new lang

        home_view = ft.Column([header, lang_row, song_list], spacing=0, expand=True)
        body_container = ft.Container(content=home_view, expand=True, bgcolor="#F5F5F5")
        page.add(body_container)

        def show_reader(s):
            page.appbar.title = ft.Text(s["title"], color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home())
            page.appbar.actions = [
                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(-2)),
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(2))
            ]
            page.appbar.visible = True
            v_list = ft.ListView(expand=True, padding=30)
            def refresh_reader():
                v_list.controls.clear()
                for line in s["lyrics"].split("\n"):
                    if line.strip(): v_list.controls.append(ft.Text(line.strip(), size=st["font_size"], color="#2C3E50", weight="500"))
                    else: v_list.controls.append(ft.Container(height=15))
                page.update()
            def zoom(delta):
                st["font_size"] = max(12, min(44, st["font_size"]+delta))
                refresh_reader()
            
            body_container.content = v_list
            body_container.bgcolor = "#FFF9E1"
            refresh_reader()

        def show_settings():
            page.appbar.title = ft.Text("Settings", color="white")
            page.appbar.visible = True ; page.appbar.actions = []
            def sync_act(e):
                e.control.disabled = True ; page.update()
                lm.sync_cloud(lambda cnt: (page.show_snack_bar(ft.SnackBar(ft.Text(f"Success! {cnt} songs synced."))), render_home()))

            body_container.content = ft.Container(padding=30, content=ft.Column([
                ft.Image(src="icon.png", width=120, height=120, error_content=ft.Icon(ft.Icons.MUSIC_NOTE, size=100)),
                ft.Container(height=20),
                ft.Text("Cloud Sync", size=24, weight="bold", color="black"),
                ft.Text(f"Project: {PROJECT_ID}", color="grey"),
                ft.Container(height=20),
                ft.ElevatedButton("SYNC NOW", icon=ft.Icons.SYNC, bgcolor="#1A237E", color="white", on_click=sync_act, height=60),
                ft.Divider(),
                ft.Text("GGGM v5.9.0", color="grey", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            body_container.bgcolor = "#F5F5F5"
            page.update()

        def render_home():
            page.appbar.visible = False
            body_container.content = home_view
            body_container.bgcolor = "#F5F5F5"
            filter_songs()

        # START 
        filter_songs()

    except Exception:
        err_msg = traceback.format_exc()
        page.add(ft.Container(padding=20, bgcolor="red", expand=True, content=ft.Text(f"INTERNAL ERROR:\n{err_msg}", color="white")))

ft.app(target=main)
