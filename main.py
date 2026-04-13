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
        if not src: return "Please download the Bible in Settings."
        try:
            ch = src[b_idx]["chapters"][c_num-1]
            return "\n".join([f"{v['verse']}. {v['text']}" for v in ch["verses"]])
        except: return "Error. Ensure Bible is fully downloaded."

class AppState:
    def __init__(self):
        self.songs = []
        self.load_songs()
    def load_songs(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
        if not self.songs:
            self.songs = [{"id": "s1", "title": "Welcome to Grace", "language": "tamil", "lyrics": "Please sync from Firebase in Settings."}]

be = BibleEngine()
as_obj = AppState()

def main(page: ft.Page):
    # TOTAL VISIBILITY THEME
    page.title = "Grace Hub v2.0"
    page.bgcolor = "#FFFFFF" # PURE WHITE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    st = {"view": "lyrics", "lang": "tamil", "q": ""}

    # SHARED UI (Stability)
    list_view = ft.ListView(expand=True, padding=10)
    search_box = ft.TextField(
        hint_text="Search lyrics...", expand=True, border_radius=12,
        bgcolor="#EEEEEE", border_color="#BDBDBD", color="#000000",
        on_change=lambda e: filter_lyrics(e.control.value)
    )

    def filter_lyrics(q=""):
        st["q"] = q
        list_view.controls.clear()
        results = [s for s in as_obj.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_view.controls.append(ft.Container(
                content=ft.ListTile(title=ft.Text(s["title"], weight="bold", color="#000000"), on_click=lambda e, song=s: show_read(song)),
                bgcolor="#FFFFFF", border_radius=12, border=ft.border.all(1, "#E0E0E0"), margin=ft.margin.symmetric(vertical=5)
            ))
        page.update()

    def show_read(s):
        # NATIVE READING VIEW
        page.controls.clear()
        page.appbar = ft.AppBar(title=ft.Text(s["title"], color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render()))
        page.add(ft.Container(content=ft.Column([ft.Text(s["lyrics"], size=22, color="#000000")], scroll="auto"), expand=True, padding=30))
        page.update()

    def sync_data(target, callback):
        urls = {"lyrics": FIREBASE_URL, "ta": BIBLE_TA_URL, "te": BIBLE_TE_URL}
        paths = {"lyrics": DB_PATH, "ta": BIBLE_TA_PATH, "te": BIBLE_TE_PATH}
        def _task():
            try:
                with urllib.request.urlopen(urls[target]) as resp:
                    data = json.load(resp)
                    if target == "lyrics":
                        as_obj.songs = [{"id": d["name"].split("/")[-1], "title": d["fields"]["title"]["stringValue"], "lyrics": d["fields"]["lyrics"]["stringValue"], "language": d["fields"]["language"]["stringValue"].lower()} for d in data.get("documents", [])]
                        with open(paths[target], "w", encoding="utf-8") as f: json.dump(as_obj.songs, f)
                    else:
                        with open(paths[target], "w", encoding="utf-8") as f: json.dump(data, f)
                    be.load()
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

    def render():
        page.controls.clear()
        # NATIVE HEADER
        page.appbar = ft.AppBar(title=ft.Text("Grace Lyrics Hub" if st["view"]=="lyrics" else "Bible" if st["view"]=="bible" else "Settings", color="white", weight="bold"), bgcolor="#1A237E", elevation=4)
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon="music_video", label="Lyrics"),
                ft.NavigationBarDestination(icon="menu_book", label="Bible"),
                ft.NavigationBarDestination(icon="settings", label="Settings"),
            ],
            selected_index=0 if st["view"]=="lyrics" else 1 if st["view"]=="bible" else 2,
            on_change=lambda e: (st.update({"view": ["lyrics", "bible", "settings"][e.control.selected_index]}), render()),
            bgcolor="#FFFFFF"
        )

        if st["view"] == "lyrics":
            # REBUILT HEADER (Stability)
            header_box = ft.Container(content=ft.Row([ft.Image(src="icon.png", width=50, height=50), search_box]), padding=15)
            tabs = ft.Container(content=ft.Row([
                ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"lang": "tamil"}), filter_lyrics(st["q"]))),
                ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"lang": "telugu"}), filter_lyrics(st["q"]))),
            ]), padding=ft.Padding(15, 0, 15, 0))
            page.add(header_box, tabs, list_view)
            filter_lyrics(st["q"])
        elif st["view"] == "bible":
            grid = ft.GridView(expand=True, runs_count=2, spacing=15, padding=15)
            for i, b in enumerate(be.books):
                grid.controls.append(ft.Container(content=ft.Text(b, weight="bold", color="#000000"), bgcolor="#FFFFFF", border_radius=12, border=ft.border.all(1, "#E0E0E0"), alignment=ft.alignment.center, height=80, on_click=lambda e, idx=i, name=b: show_bible(idx, name)))
            page.add(grid)
        elif st["view"] == "settings":
            def notify(m): page.snack_bar = ft.SnackBar(ft.Text(m, color="white"), bgcolor="#1A237E"); page.snack_bar.open = True; page.update()
            page.add(ft.Container(content=ft.Column([
                ft.Text("Sync Options", size=24, weight="bold", color="#000000"),
                ft.ListTile(title=ft.Text("Sync Lyrics (Cloud)", color="#000000"), on_click=lambda _: sync_data("lyrics", lambda s: notify("Lyrics Ready!" if s else "Sync Failed"))),
                ft.ListTile(title=ft.Text("Download Tamil Bible", color="#000000"), on_click=lambda _: sync_data("ta", lambda s: notify("Tamil Bible Ready!" if s else "Download Failed"))),
                ft.ListTile(title=ft.Text("Download Telugu Bible", color="#000000"), on_click=lambda _: sync_data("te", lambda s: notify("Telugu Bible Ready!" if s else "Download Failed"))),
                ft.Divider(),
                ft.Text("Version 2.0.0 - Visibility First", color="#757575")
            ]), padding=30))
        page.update()

    def show_bible(idx, name):
        page.controls.clear()
        ch_grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for c in range(1, be.counts[idx]+1):
            ch_grid.controls.append(ft.Container(content=ft.Text(str(c), color="#000000", weight="bold"), bgcolor="#EEEEEE", border_radius=8, alignment=ft.alignment.center, on_click=lambda e, ch=c: show_bible_read(idx, name, ch)))
        page.add(ft.AppBar(title=ft.Text(name, color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render())), ch_grid); page.update()

    def show_bible_read(idx, name, ch):
        page.controls.clear()
        txt = be.get_verses(idx, ch, st["lang"])
        page.appbar = ft.AppBar(title=ft.Text(f"{name} {ch}", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: show_bible(idx, name)))
        page.add(ft.Container(content=ft.Column([ft.Text(txt, size=21, color="#000000", line_height=1.5)], scroll="auto"), expand=True, padding=30)); page.update()

    render()

ft.app(target=main)
