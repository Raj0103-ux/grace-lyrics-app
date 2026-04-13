import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
BIBLE_TA_PATH = "bible_ta.json"
BIBLE_TE_PATH = "bible_te.json"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"
BIBLE_TA_URL = "https://raw.githubusercontent.com/joseph-p-anderson/tamil-bible-json/master/tamil-bible.json"
BIBLE_TE_URL = "https://raw.githubusercontent.com/joseph-p-anderson/telugu-bible-json/master/telugu-bible.json"

class BibleEngine:
    def __init__(self):
        self.books = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
        self.data_ta = None
        self.data_te = None
        self.load()
    def load(self):
        if os.path.exists(BIBLE_TA_PATH):
            try:
                with open(BIBLE_TA_PATH, "r", encoding="utf-8") as f: self.data_ta = json.load(f)
            except: pass
        if os.path.exists(BIBLE_TE_PATH):
            try:
                with open(BIBLE_TE_PATH, "r", encoding="utf-8") as f: self.data_te = json.load(f)
            except: pass
    def get_verses(self, b_idx, c_num, lang="tamil"):
        src = self.data_ta if lang == "tamil" else self.data_te
        if not src: return "Please download Bible in Settings."
        try:
            return "\n".join([f"{v['verse']}. {v['text']}" for v in src[b_idx]["chapters"][c_num-1]["verses"]])
        except: return "No data. Re-download Bible."

class GlobalState:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
    def sync(self, callback):
        def _t():
            try:
                with urllib.request.urlopen(FIREBASE_URL) as r:
                    d = json.load(r)
                    self.songs = [{"title": doc["fields"]["title"]["stringValue"], "lyrics": doc["fields"]["lyrics"]["stringValue"], "language": doc["fields"]["language"]["stringValue"].lower()} for doc in d.get("documents", [])]
                    with open(DB_PATH, "w", encoding="utf-8") as f: json.dump(self.songs, f)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_t).start()

be = BibleEngine()
gs = GlobalState()

def main(page: ft.Page):
    page.title = "Grace Infinity v2.1"
    page.bgcolor = "#FFFFFF"
    page.padding = 0
    st = {"v": "lyrics", "l": "tamil", "q": ""}

    def route_change(e):
        page.views.clear()
        
        # Navigation bar (Always Locked to the actual Android Nav Bar frame)
        navbar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon="music_video", label="Lyrics"),
                ft.NavigationBarDestination(icon="menu_book", label="Bible"),
                ft.NavigationBarDestination(icon="settings", label="Settings"),
            ],
            selected_index=0 if st["v"]=="lyrics" else 1 if st["v"]=="bible" else 2,
            on_change=lambda e: (st.update({"v": ["lyrics", "bible", "settings"][e.control.selected_index]}), page.go("/" + st["v"]))
        )

        view = ft.View(
            "/" + st["v"],
            bgcolor="#FFFFFF",
            navigation_bar=navbar,
            appbar=ft.AppBar(title=ft.Text("Grace Lyrics Hub" if st["v"]=="lyrics" else "Sacred Bible" if st["v"]=="bible" else "Settings", color="white"), bgcolor="#1A237E")
        )

        if st["v"] == "lyrics":
            songs = [s for s in gs.songs if s["language"] == st["l"] and st["q"].lower() in s["title"].lower()]
            view.controls = [
                ft.Container(content=ft.Row([ft.Image(src="icon.png", width=50, height=50), ft.TextField(hint_text="Search lyrics...", expand=1, on_change=lambda e: (st.update({"q": e.control.value}), route_change(None)))], padding=15)),
                ft.Container(content=ft.Row([ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"l": "tamil"}), route_change(None))), ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"l": "telugu"}), route_change(None)))]), padding=ft.Padding(15, 0, 15, 10)),
                ft.ListView([ft.Container(content=ft.ListTile(title=ft.Text(s["title"], weight="bold", color="#000000"), on_click=lambda e, song=s: show_song(song)), bgcolor="white", border_radius=12, border=ft.border.all(1, "#E0E0E0"), margin=ft.margin.symmetric(horizontal=15, vertical=5)) for s in songs], expand=1)
            ]
        elif st["v"] == "bible":
            grid = ft.GridView(expand=1, runs_count=2, spacing=15, padding=15)
            for i, b in enumerate(be.books):
                grid.controls.append(ft.Container(content=ft.Text(b, weight="bold", color="black"), bgcolor="white", border_radius=12, border=ft.border.all(1, "#E0E0E0"), alignment=ft.alignment.center, height=80, on_click=lambda e, idx=i, name=b: show_chapters(idx, name)))
            view.controls = [grid]
        elif st["v"] == "settings":
            def notify(msg): page.snack_bar = ft.SnackBar(ft.Text(msg)); page.snack_bar.open = True; page.update()
            view.controls = [ft.Container(content=ft.Column([
                ft.Text("Storage Control", size=24, weight="bold", color="black"),
                ft.ListTile(title=ft.Text("Sync Lyrics (Cloud)", color="black"), on_click=lambda _: gs.sync(lambda s: notify("Lyrics Synced!" if s else "Sync Fail"))),
                ft.ListTile(title=ft.Text("Download Tamil Bible", color="black"), on_click=lambda _: be.download_bible("tamil", lambda s: notify("Tamil Download Ready!" if s else "Fail"))),
                ft.ListTile(title=ft.Text("Download Telugu Bible", color="black"), on_click=lambda _: be.download_bible("telugu", lambda s: notify("Telugu Download Ready!" if s else "Fail")))
            ]), padding=30)]
        
        page.views.append(view)
        page.update()

    def show_song(s):
        # INFINITE LIST VIEW FOR LONG LYRICS
        page.views.append(ft.View("/song", [
            ft.AppBar(title=ft.Text(s["title"], color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.views.pop() or page.update())),
            ft.ListView([ft.Text(s["lyrics"], size=22, color="black")], expand=1, padding=30)
        ], bgcolor="#FFF9E1"))
        page.update()

    def show_chapters(idx, name):
        grid = ft.GridView(expand=1, runs_count=5, spacing=10, padding=20)
        for c in range(1, be.counts[idx]+1):
            grid.controls.append(ft.Container(content=ft.Text(str(c), weight="bold", color="black"), bgcolor="#EEEEEE", border_radius=8, alignment=ft.alignment.center, on_click=lambda e, ch=c: show_verses(idx, name, ch)))
        page.views.append(ft.View("/chapters", [ft.AppBar(title=ft.Text(name, color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.views.pop() or page.update())), grid], bgcolor="#FFFFFF"))
        page.update()

    def show_verses(idx, name, ch):
        txt = be.get_verses(idx, ch, st["l"])
        page.views.append(ft.View("/verses", [ft.AppBar(title=ft.Text(f"{name} {ch}", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.views.pop() or page.update())), ft.ListView([ft.Text(txt, size=21, color="black")], expand=1, padding=30)], bgcolor="#FFF9E1"))
        page.update()

    # Bible Download logic must be inside BibleEngine for stability
    def download_bible_task(lang, callback):
        url = BIBLE_TA_URL if lang == "tamil" else BIBLE_TE_URL
        path = BIBLE_TA_PATH if lang == "tamil" else BIBLE_TE_PATH
        def _t():
            try:
                with urllib.request.urlopen(url) as r:
                    data = json.load(r)
                    with open(path, "w", encoding="utf-8") as f: json.dump(data, f)
                    be.load()
                    callback(True)
            except: callback(False)
        threading.Thread(target=_t).start()
    be.download_bible = download_bible_task

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)
