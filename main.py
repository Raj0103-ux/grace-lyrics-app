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

# Reliable Bible Data Sources
BIBLE_TA_URL = "https://raw.githubusercontent.com/joseph-p-anderson/tamil-bible-json/master/tamil-bible.json"
BIBLE_TE_URL = "https://raw.githubusercontent.com/joseph-p-anderson/telugu-bible-json/master/telugu-bible.json"

class BibleManager:
    def __init__(self):
        self.books_ta = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
        self.data_ta = None
        self.data_te = None
        self._load_local()

    def _load_local(self):
        if os.path.exists(BIBLE_TA_PATH):
            try:
                with open(BIBLE_TA_PATH, "r", encoding="utf-8") as f: self.data_ta = json.load(f)
            except: pass
        if os.path.exists(BIBLE_TE_PATH):
            try:
                with open(BIBLE_TE_PATH, "r", encoding="utf-8") as f: self.data_te = json.load(f)
            except: pass

    def get_verses(self, book_idx, ch_num, lang="tamil"):
        data = self.data_ta if lang == "tamil" else self.data_te
        if not data: return "Please download the Bible in Settings to view verses offline."
        try:
            # Standard JSON Bible format parsing
            book_data = data[book_idx]
            chapter_data = book_data["chapters"][ch_num-1]
            return "\n".join([f"{v['verse']}. {v['text']}" for v in chapter_data["verses"]])
        except: return "Error loading verses. Ensure Bible is fully downloaded."

    def download_bible(self, lang, callback):
        url = BIBLE_TA_URL if lang == "tamil" else BIBLE_TE_URL
        path = BIBLE_TA_PATH if lang == "tamil" else BIBLE_TE_PATH
        def _task():
            try:
                with urllib.request.urlopen(url) as res:
                    data = json.load(res)
                    with open(path, "w", encoding="utf-8") as f: json.dump(data, f)
                    self._load_local()
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

class SongManager:
    def __init__(self):
        self.songs = []
        self.load()
    def load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
    def sync_firebase(self, callback):
        def _task():
            try:
                with urllib.request.urlopen(FIREBASE_URL) as res:
                    data = json.load(res)
                    docs = data.get("documents", [])
                    new_list = []
                    for d in docs:
                        f = d.get("fields", {})
                        new_list.append({
                            "id": d["name"].split("/")[-1],
                            "title": f.get("title", {}).get("stringValue", "Untitled"),
                            "lyrics": f.get("lyrics", {}).get("stringValue", ""),
                            "language": f.get("language", {}).get("stringValue", "tamil").lower()
                        })
                    self.songs = new_list
                    with open(DB_PATH, "w", encoding="utf-8") as f: json.dump(new_list, f)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

sm = SongManager()
bm = BibleManager()

def main(page: ft.Page):
    page.title = "Grace Hub Pro"
    page.bgcolor = "#F5F5F5"
    page.padding = 0
    state = {"v": "lyrics", "lang": "tamil", "q": ""}

    # Global Controls for persistence
    list_view = ft.ListView(expand=True, padding=10)
    search_field = ft.TextField(hint_text="Search lyrics...", expand=True, border_radius=10, bgcolor="white",
                                on_change=lambda e: filter_results(e.control.value))

    def filter_results(q=""):
        state["q"] = q
        list_view.controls.clear()
        results = [s for s in sm.songs if s["language"] == state["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_view.controls.append(ft.Container(
                content=ft.ListTile(title=ft.Text(s["title"], weight="bold"), on_click=lambda e, s=s: show_details(s)),
                bgcolor="white", border_radius=12, margin=ft.margin.symmetric(vertical=4), shadow=ft.BoxShadow(blur_radius=5, color="#00000008")
            ))
        page.update()

    def show_details(s):
        page.clean()
        page.add(
            ft.AppBar(title=ft.Text(s["title"]), bgcolor="#1A237E", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: render())),
            ft.Container(content=ft.Column([ft.Text(s["lyrics"], size=22, line_height=1.5)], scroll="auto"), expand=True, padding=30, bgcolor="#FFF9E1")
        )

    def show_v_bible(book_idx, book_name, ch_num):
        page.clean()
        verses = bm.get_verses(book_idx, ch_num, state["lang"])
        page.add(
            ft.AppBar(title=ft.Text(f"{book_name} {ch_num}"), bgcolor="#1A237E", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_chapters(book_idx, book_name))),
            ft.Container(content=ft.Column([ft.Text(verses, size=21, line_height=1.6)], scroll="auto"), expand=True, padding=30, bgcolor="#FFF9E1")
        )

    def show_chapters(idx, name):
        page.clean()
        grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for i in range(1, bm.counts[idx]+1):
            grid.controls.append(ft.Container(content=ft.Text(str(i), weight="bold"), bgcolor="white", border_radius=8, alignment=ft.alignment.center, on_click=lambda e, c=i: show_v_bible(idx, name, c)))
        page.add(ft.AppBar(title=ft.Text(name), bgcolor="#1A237E", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: render())), grid)

    def render():
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("Grace Lyrics Hub"), bgcolor="#1A237E", color="white")
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            selected_index=0 if state["v"]=="lyrics" else 1 if state["v"]=="bible" else 2,
            on_change=lambda e: (state.update({"v": ["lyrics", "bible", "settings"][e.control.selected_index]}), render())
        )

        if state["v"] == "lyrics":
            header = ft.Row([ft.Image(src="icon.png", width=50, height=50, border_radius=10), search_field], padding=15)
            tabs = ft.Row([
                ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (state.update({"lang": "tamil"}), filter_results(state["q"]))),
                ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (state.update({"lang": "telugu"}), filter_results(state["q"]))),
            ], padding=ft.Padding(15, 0, 15, 0))
            page.add(header, tabs, list_view)
            filter_results(state["q"])
        elif state["v"] == "bible":
            grid = ft.GridView(expand=True, runs_count=2, spacing=12, padding=15)
            books = bm.books_ta # Default to Ta, handle Te later
            for i, b in enumerate(books):
                grid.controls.append(ft.Container(content=ft.Text(b, weight="bold"), bgcolor="white", border_radius=12, alignment=ft.alignment.center, height=80, on_click=lambda e, idx=i, name=b: show_chapters(idx, name)))
            page.add(ft.Container(content=ft.Text("Books", size=22, weight="bold"), padding=15), grid)
        elif state["v"] == "settings":
            def notify(msg):
                page.snack_bar = ft.SnackBar(ft.Text(msg)); page.snack_bar.open = True; page.update()
            page.add(ft.Container(content=ft.Column([
                ft.Text("Sync Options", size=24, weight="bold"),
                ft.ListTile(title=ft.Text("Sync Lyrics (Firebase)"), leading=ft.Icon(ft.Icons.SYNC), on_click=lambda _: sm.sync_firebase(lambda s: notify("Lyrics Synced!" if s else "Sync Failed"))),
                ft.ListTile(title=ft.Text("Download Tamil Bible (10MB)"), leading=ft.Icon(ft.Icons.DOWNLOAD), on_click=lambda _: bm.download_bible("tamil", lambda s: notify("Tamil Bible Ready!" if s else "Download Failed"))),
                ft.ListTile(title=ft.Text("Download Telugu Bible (10MB)"), leading=ft.Icon(ft.Icons.DOWNLOAD), on_click=lambda _: bm.download_bible("telugu", lambda s: notify("Telugu Bible Ready!" if s else "Download Failed"))),
            ]), padding=30))
        page.update()

    render()

ft.app(target=main)
