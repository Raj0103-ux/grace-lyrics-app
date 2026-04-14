import flet as ft
import json
import urllib.request
import threading
import os

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
                            # LYRICS POLISHER: Converst literal \n into real newlines
                            clean_lyrics = raw_lyrics.replace("\\n", "\n").replace("\\r", "\n")
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
    page.title = "Grace Hub Polished"
    page.bgcolor = "#F5F5F5" ; page.padding = 0 ; page.theme_mode = ft.ThemeMode.LIGHT
    st = {"lang": "tamil", "q": "", "font_size": 22}

    list_body = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
    search_bar = ft.TextField(
        hint_text="Search songs...", expand=True, bgcolor="white",
        border_radius=12, border_color="transparent", prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_songs(e.control.value)
    )

    def filter_songs(q=""):
        st["q"] = q ; list_body.controls.clear()
        results = [s for s in lm.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_body.controls.append(ft.Container(
                content=ft.ListTile(leading=ft.Icon(ft.Icons.MUSIC_NOTE, color="#1A237E"), title=ft.Text(s["title"], weight="bold", color="black"), on_click=lambda e, song=s: show_reader(song)),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#E8EAF6"), margin=ft.margin.symmetric(vertical=4), shadow=ft.BoxShadow(blur_radius=10, color="#10000000", offset=ft.Offset(0, 4))
            ))
        page.update()

    def show_reader(s):
        page.clean() ; page.bgcolor = "#FFF9E1"
        v_list = ft.ListView(expand=True, padding=30)
        def refresh():
            v_list.controls.clear()
            for line in s["lyrics"].split("\n"):
                if line.strip(): v_list.controls.append(ft.Text(line.strip(), size=st["font_size"], color="#2C3E50", weight="500"))
                else: v_list.controls.append(ft.Container(height=15))
            page.update()
        page.appbar = ft.AppBar(
            title=ft.Text(s["title"], color="white"), bgcolor="#1A237E",
            leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home()),
            actions=[ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: (st.update({"font_size": max(12, st["font_size"]-2)}), refresh())), ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: (st.update({"font_size": min(40, st["font_size"]+2)}), refresh()))]
        )
        refresh() ; page.add(v_list) ; page.update()

    def show_settings():
        page.clean() ; page.bgcolor = "#F5F5F5"
        page.appbar = ft.AppBar(title=ft.Text("Settings", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home()))
        def sync_act(e):
            e.control.disabled = True ; page.update()
            lm.sync_cloud(lambda cnt: (page.show_snack_bar(ft.SnackBar(ft.Text(f"Sync Complete! {cnt} songs." if cnt>=0 else "Sync Fail."))), render_home()))
        page.add(ft.Container(padding=30, content=ft.Column([ft.Text("Cloud Sync", size=24, weight="bold", color="black"), ft.Text(f"Target: {PROJECT_ID}", color="grey"), ft.Container(height=20), ft.ElevatedButton("SYNC NOW", icon=ft.Icons.SYNC, bgcolor="#1A237E", color="white", on_click=sync_act, height=50), ft.Divider(), ft.Text("v5.2.0 Polished Hub", color="grey", size=11)])))
        page.update()

    def render_home():
        page.clean() ; page.bgcolor = "#F5F5F5"
        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([ft.Row([ft.Row([ft.Image(src="icon.png", width=40, height=40), ft.Text("Grace Lyrics", color="white", size=24, weight="bold")]), ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: show_settings())], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Container(height=10), ft.Row([ft.Container(content=search_bar, expand=True)])])
        )
        lang_row = ft.Container(padding=15, content=ft.Row([ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if st["lang"]=="tamil" else "white", color="#1A237E" if st["lang"]=="tamil" else "grey", on_click=lambda _: (st.update({"lang": "tamil"}), filter_songs())), ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if st["lang"]=="telugu" else "white", color="#1A237E" if st["lang"]=="telugu" else "grey", on_click=lambda _: (st.update({"lang": "telugu"}), filter_songs()))], spacing=15))
        page.add(header, lang_row, list_body) ; filter_songs(st["q"])

    render_home()

ft.app(target=main)
