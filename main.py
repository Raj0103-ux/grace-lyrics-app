import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"

class LyricsState:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
    def sync(self, callback):
        def _task():
            try:
                with urllib.request.urlopen(FIREBASE_URL) as r:
                    d = json.load(r)
                    new_list = []
                    for doc in d.get("documents", []):
                        f = doc.get("fields", {})
                        new_list.append({
                            "title": f.get("title", {}).get("stringValue", "No Title"),
                            "lyrics": f.get("lyrics", {}).get("stringValue", ""),
                            "language": f.get("language", {}).get("stringValue", "tamil").lower()
                        })
                    self.songs = new_list
                    with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(new_list, out)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

ls = LyricsState()

def main(page: ft.Page):
    # PURE LYRICS HUB - MINIMALIST & STABLE
    page.title = "Grace Lyrics Hub"
    page.bgcolor = "#FFFFFF"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    st = {"view": "lyrics", "lang": "tamil", "q": ""}
    
    # Persistent UI elements
    list_body = ft.ListView(expand=True, padding=10)
    search_bar = ft.TextField(
        hint_text="Search songs...", expand=True, bgcolor="#F5F7FA", border_radius=12,
        color="black", on_change=lambda e: filter_view(e.control.value)
    )

    def filter_view(q=""):
        st["q"] = q
        list_body.controls.clear()
        results = [s for s in ls.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_body.controls.append(ft.Container(
                content=ft.ListTile(title=ft.Text(s["title"], weight="bold", color="black"), on_click=lambda e, song=s: show_reading_view(song)),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#ECEFF1"), margin=ft.margin.symmetric(vertical=4)
            ))
        page.update()

    def show_reading_view(s):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text(s["title"], color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render()))
        verses = s["lyrics"].split("\n")
        v_list = ft.ListView(expand=True, padding=30)
        for line in verses:
            if line.strip(): v_list.controls.append(ft.Text(line, size=21, color="black", line_height=1.4))
            else: v_list.controls.append(ft.Container(height=15))
        page.add(v_list)
        page.update()

    def render():
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("Grace Lyrics", color="white", weight="bold"), bgcolor="#1A237E", elevation=2)
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon="music_note", label="Songs"),
                ft.NavigationBarDestination(icon="settings", label="Settings"),
            ],
            selected_index=0 if st["view"]=="lyrics" else 1,
            on_change=lambda e: (st.update({"view": "lyrics" if e.control.selected_index==0 else "settings"}), render()),
            bgcolor="white", height=70
        )

        if st["view"] == "lyrics":
            # HEADER ROW (LOGO + SEARCH)
            logo = ft.Container()
            try: logo = ft.Image(src="icon.png", width=45, height=45, border_radius=8)
            except: pass
            
            page.add(
                ft.Container(content=ft.Row([logo, search_bar]), padding=15),
                ft.Container(content=ft.Row([
                    ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"lang": "tamil"}), filter_view())),
                    ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"lang": "telugu"}), filter_view())),
                ]), padding=ft.Padding(15, 0, 15, 10)),
                list_body
            )
            filter_view(st["q"])
        else:
            def notify(m): page.snack_bar = ft.SnackBar(ft.Text(m)); page.snack_bar.open = True; page.update()
            page.add(ft.Container(content=ft.Column([
                ft.Text("App Settings", size=24, weight="bold", color="black"),
                ft.ListTile(title=ft.Text("Sync Lyrics with Firebase", color="black"), leading=ft.Icon(ft.Icons.CLOUD_SYNC, color="#1A237E"), on_click=lambda _: ls.sync(lambda s: notify("Synced Successfully!" if s else "Sync Failed"))),
                ft.Divider(),
                ft.Text("Grace Lyrics Hub v3.0 (Lite)", color="grey")
            ]), padding=30))
        page.update()

    render()

ft.app(target=main)
