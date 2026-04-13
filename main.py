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
        self.data_ta = None ; self.data_te = None ; self.load()
    def load(self):
        for p, attr in [(BIBLE_TA_PATH, "data_ta"), (BIBLE_TE_PATH, "data_te")]:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f: setattr(self, attr, json.load(f))
                except: pass
    def get_v(self, b_idx, c_num, lang="tamil"):
        src = self.data_ta if lang == "tamil" else self.data_te
        if not src: return ["Please download Bible in Settings."]
        try:
            return [f"{v['verse']}. {v['text']}" for v in src[b_idx]["chapters"][c_num-1]["verses"]]
        except: return ["Error loading verses."]

class DataStore:
    def __init__(self):
        self.songs = [] ; self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
    def cloud_sync(self, callback):
        def _t():
            try:
                # FULL STREAM SYNC WITH ERROR RECOVERY
                with urllib.request.urlopen(FIREBASE_URL) as r:
                    d = json.load(r)
                    self.songs = []
                    for doc in d.get("documents", []):
                        f = doc.get("fields", {})
                        self.songs.append({
                            "title": f.get("title", {}).get("stringValue", "No Title"),
                            "lyrics": f.get("lyrics", {}).get("stringValue", ""),
                            "language": f.get("language", {}).get("stringValue", "tamil").lower()
                        })
                    with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(self.songs, out)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_t).start()

ds = DataStore() ; be = BibleEngine()

def main(page: ft.Page):
    page.title = "Grace Hub Full-Stream"
    page.bgcolor = "#FFFFFF" ; page.padding = 0 ; page.theme_mode = ft.ThemeMode.LIGHT
    st = {"view": "lyrics", "lang": "tamil", "q": ""}

    def filter_ui(q=""):
        st["q"] = q ; list_body.controls.clear()
        results = [s for s in ds.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_body.controls.append(ft.Container(
                content=ft.ListTile(title=ft.Text(s["title"], weight="bold", color="black"), on_click=lambda e, song=s: show_reading(song)),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#E0E0E0"), margin=ft.margin.symmetric(vertical=5)
            ))
        page.update()

    def show_reading(s):
        # VERSE-BY-VERSE RENDERING (Solves 'Half Lyrics' issue)
        page.clean()
        lines = s["lyrics"].split("\n")
        scroll_list = ft.ListView(expand=True, padding=30)
        for line in lines:
            if line.strip(): scroll_list.controls.append(ft.Text(line, size=21, color="black", line_height=1.4))
            else: scroll_list.controls.append(ft.Container(height=15)) # Small gap between stanzas
        page.appbar = ft.AppBar(title=ft.Text(s["title"], color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render()))
        page.add(scroll_list) ; page.update()

    def sync_proc(target, callback):
        urls = {"ta": BIBLE_TA_URL, "te": BIBLE_TE_URL} ; paths = {"ta": BIBLE_TA_PATH, "te": BIBLE_TE_PATH}
        def _task():
            try:
                with urllib.request.urlopen(urls[target]) as resp:
                    with open(paths[target], "w", encoding="utf-8") as f: json.dump(json.load(resp), f)
                    be.load() ; callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

    list_body = ft.ListView(expand=True, padding=10)
    search_bar = ft.TextField(hint_text="Search lyrics...", expand=True, bgcolor="#F0F2F5", color="black", border_radius=10, on_change=lambda e: filter_ui(e.control.value))

    def render():
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("Grace Hub", color="white", weight="bold"), bgcolor="#1A237E")
        page.navigation_bar = ft.NavigationBar(
            destinations=[ft.NavigationBarDestination(icon="music_note", label="Lyrics"), ft.NavigationBarDestination(icon="book", label="Bible"), ft.NavigationBarDestination(icon="settings", label="Settings")],
            selected_index=0 if st["view"]=="lyrics" else 1 if st["view"]=="bible" else 2,
            on_change=lambda e: (st.update({"view": ["lyrics", "bible", "settings"][e.control.selected_index]}), render()),
            bgcolor="white", height=75
        )

        if st["view"] == "lyrics":
            # SAFE LOGO LOAD
            logo = ft.Container()
            try: logo = ft.Image(src="icon.png", width=50, height=50)
            except: pass
            page.add(
                ft.Container(content=ft.Row([logo, search_bar]), padding=15),
                ft.Container(content=ft.Row([ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"lang": "tamil"}), filter_ui())), ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"lang": "telugu"}), filter_ui()))]), padding=ft.Padding(15, 0, 15, 10)),
                list_body
            )
            filter_ui(st["q"])
        elif st["view"] == "bible":
            grid = ft.GridView(expand=True, runs_count=2, spacing=15, padding=15)
            for i, b in enumerate(be.books):
                grid.controls.append(ft.Container(content=ft.Text(b, weight="bold", color="black"), bgcolor="white", border_radius=12, border=ft.border.all(1, "#E0E0E0"), alignment=ft.alignment.center, height=80, on_click=lambda e, idx=i, name=b: show_bible_ch(idx, name)))
            page.add(grid)
        elif st["view"] == "settings":
            def msg(t): page.snack_bar = ft.SnackBar(ft.Text(t)); page.snack_bar.open = True; page.update()
            page.add(ft.Container(content=ft.Column([
                ft.Text("Super Sync Console", size=24, weight="bold", color="black"),
                ft.ListTile(title=ft.Text("Sync Full Lyrics (Cloud)"), on_click=lambda _: ds.cloud_sync(lambda s: msg("Lyrics Full Synced!" if s else "Sync Fail"))),
                ft.ListTile(title=ft.Text("Download Tamil Bible"), on_click=lambda _: sync_proc("ta", lambda s: msg("Tamil Bible Downloaded!" if s else "Fail"))),
                ft.ListTile(title=ft.Text("Download Telugu Bible"), on_click=lambda _: sync_proc("te", lambda s: msg("Telugu Bible Downloaded!" if s else "Fail"))),
                ft.Divider(), ft.Text("Version 2.3.0 - Full Stream", color="grey")
            ]), padding=30))
        page.update()

    def show_bible_ch(idx, name):
        page.clean()
        ch_grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for c in range(1, be.counts[idx]+1):
            ch_grid.controls.append(ft.Container(content=ft.Text(str(c), weight="bold", color="black"), bgcolor="#F0F2F5", border_radius=8, alignment=ft.alignment.center, on_click=lambda e, ch=c: show_bible_v(idx, name, ch)))
        page.add(ft.AppBar(title=ft.Text(name, color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render())), ch_grid) ; page.update()

    def show_bible_v(idx, name, ch):
        page.clean()
        lines = be.get_v(idx, ch, st["lang"]) ; v_list = ft.ListView(expand=True, padding=30)
        for line in lines: v_list.controls.append(ft.Text(line, size=21, color="black", line_height=1.5))
        page.add(ft.AppBar(title=ft.Text(f"{name} {ch}", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: show_bible_ch(idx, name))), v_list) ; page.update()

    render()

ft.app(target=main)
