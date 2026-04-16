import flet as ft
import json
import urllib.request
import threading
import os
import traceback
import re
import sys
import time

# ===================== CONFIG =====================
PROJECT_ID = "grace-lyrics-admin"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"

# ===================== LOGGING & GLOBALS =====================
_search_timer = None

def log(msg):
    """Print debug messages to stderr so they show in console."""
    print(f"[GGGM] {msg}", file=sys.stderr, flush=True)

# ===================== DATA MANAGER =====================
class LyricsManager:
    def __init__(self):
        self.songs = []
        self._db_path = None
        self._seed_path = "assets/songs.json"

    def set_db_path(self, path):
        self._db_path = path

    def load(self):
        """
        Load songs with a fallback chain:
        1. Writable database file (synced updates)
        2. Seed file in assets (pre-loaded songs)
        """
        # 1. Try writable database
        if self._db_path and os.path.exists(self._db_path):
            try:
                with open(self._db_path, "r", encoding="utf-8") as f:
                    self.songs = json.load(f)
                log(f"Loaded {len(self.songs)} songs from database")
                return
            except Exception as ex:
                log(f"Load database error: {ex}")

        # 2. Try seed file locations
        # assets/songs.json (local dev) or songs.json (bundled in APK root)
        seed_paths = ["assets/songs.json", "songs.json", "data/songs.json"]
        
        for seed_path in seed_paths:
            if os.path.exists(seed_path):
                try:
                    with open(seed_path, "r", encoding="utf-8") as f:
                        self.songs = json.load(f)
                    log(f"Loaded {len(self.songs)} songs from seed: {seed_path}")
                    # Save it to the writable path immediately so future syncs work
                    if self._db_path:
                        self.save()
                    return
                except Exception as ex:
                    log(f"Load seed error ({seed_path}): {ex}")
        
        log(f"No database or seed found.")

    def save(self):
        try:
            d = os.path.dirname(self._db_path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self.songs, f, ensure_ascii=False)
            log(f"Saved {len(self.songs)} songs to {self._db_path}")
        except Exception as ex:
            log(f"Save error: {ex}")

    def sync_from_cloud(self):
        """
        Synchronously fetch ALL songs from Firebase Firestore.
        Returns (songs_list, error_string_or_None).
        """
        all_songs = []
        next_token = None
        page_num = 0

        while True:
            url = BASE_URL + "?pageSize=300"
            if next_token:
                url += f"&pageToken={next_token}"

            log(f"Fetching page {page_num + 1}...")
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)

            docs = data.get("documents", [])
            log(f"Page {page_num + 1}: got {len(docs)} docs")

            for doc in docs:
                f = doc.get("fields", {})
                raw_lyrics = f.get("lyrics", f.get("Lyric", {})).get("stringValue", "")
                clean_lyrics = raw_lyrics.replace("\\n", "\n").replace("\\r", "\n").replace("\r\n", "\n")
                title = f.get("title", f.get("Title", {})).get("stringValue", "No Title")
                language = f.get("language", f.get("Language", {})).get("stringValue", "tamil").lower().strip()

                all_songs.append({
                    "title": title,
                    "lyrics": clean_lyrics,
                    "language": language,
                })

            next_token = data.get("nextPageToken")
            page_num += 1
            if not next_token:
                break

        return all_songs


lm = LyricsManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    try:
        page.assets_dir = "assets"
        page.title = "GGGM"
        page.bgcolor = "#F5F5F5"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        # Resolve a writable data directory
        data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
        if not data_dir:
            # Fallback for Windows/Android local testing
            data_dir = os.path.join(os.getcwd(), "data")
        
        try:
            os.makedirs(data_dir, exist_ok=True)
            lm.set_db_path(os.path.join(data_dir, "songs.json"))
            lm.load()
        except Exception as e:
            log(f"Storage setup error: {e}")
            lm.load() # try loading without a writable path just in case
        log(f"App started. Songs in memory: {len(lm.songs)}")

        st = {"lang": "tamil", "q": "", "font_size": 22, "letter": None, "script": "native"}
        page.appbar = ft.AppBar(visible=False)

        # ---- ALPHABET DATA ----
        TAMIL_ALPHA = ["அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "க", "ச", "ஞ", "த", "ந", "ப", "ம", "ய", "வ"]
        TELUGU_ALPHA = ["అ", "ఆ", "ఇ", "ఈ", "ఉ", "ఊ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ", "క", "గ", "చ", "జ", "ట", "డ", "త", "ద", "న", "ప", "బ", "మ", "య", "ర", "ల", "వ", "స", "హ"]
        ENGLISH_ALPHA = [chr(i) for i in range(65, 91)] # A-Z

        # PERSISTENT STRUCTURE
        list_container = ft.Container(expand=True)
        alpha_container = ft.Container(padding=ft.padding.only(left=15, right=15, bottom=10))
        script_row_container = ft.Container(padding=ft.padding.only(left=15, right=15, bottom=5))

        def get_smart_preview(lyrics):
            for line in lyrics.split("\n"):
                line = line.strip()
                if re.search(r'[a-zA-Z]', line):
                    return line[:40] + ("..." if len(line) > 40 else "")
            lines = [l for l in lyrics.split("\n") if l.strip()]
            return (lines[0][:40] + "...") if lines else ""

        def build_script_row():
            """Toggle between English and Native Alphabets."""
            native_label = "TAMIL" if st["lang"] == "tamil" else "TELUGU"
            return ft.Row([
                ft.TextButton(
                    "English Letters", 
                    style=ft.ButtonStyle(color="#1A237E" if st["script"] == "english" else "grey"),
                    on_click=lambda _: change_script("english")
                ),
                ft.Text(" • ", color="grey"),
                ft.TextButton(
                    f"{native_label} Letters", 
                    style=ft.ButtonStyle(color="#1A237E" if st["script"] == "native" else "grey"),
                    on_click=lambda _: change_script("native")
                ),
            ], alignment=ft.MainAxisAlignment.CENTER)

        def change_script(s):
            st["script"] = s
            st["letter"] = None
            filter_songs()

        def build_alpha_row():
            """Build the horizontal alphabet selector."""
            current_alphas = []
            if st["script"] == "native":
                current_alphas = TAMIL_ALPHA if st["lang"] == "tamil" else TELUGU_ALPHA
            else:
                current_alphas = ENGLISH_ALPHA
            
            row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=10)
            
            # "ALL" button
            row.controls.append(ft.Container(
                content=ft.Text("ALL", color="white" if st["letter"] == None else "#1A237E", weight="bold"),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor="#1A237E" if st["letter"] == None else "#E8EAF6",
                border_radius=20,
                on_click=lambda _: select_letter(None)
            ))

            for char in current_alphas:
                is_sel = st["letter"] == char
                row.controls.append(ft.Container(
                    content=ft.Text(char, color="white" if is_sel else "#1A237E", weight="bold"),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor="#1A237E" if is_sel else "#E8EAF6",
                    border_radius=20,
                    on_click=lambda _, c=char: select_letter(c)
                ))
            return row

        def select_letter(char):
            st["letter"] = char
            # Refresh UI
            filter_songs()

        def build_song_list():
            new_list = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
            query = st["q"].lower()
            
            # Optimization: Filter the list twice. First by language.
            results = [s for s in lm.songs if s.get("language", "") == st["lang"]]
            
            # If query exists, search everywhere (ignores letter index)
            if query:
                results = [s for s in results if (query in s.get("title", "").lower() or query in s.get("lyrics", "").lower())]
            # Otherwise, use alphabet filter if selected
            elif st["letter"]:
                l = st["letter"].lower()
                # SMART FILTER: Check both chunks of a title (e.g. "Native - English")
                def check_match(song):
                    title = song.get("title", "").lower()
                    parts = [p.strip() for p in title.split("-")]
                    for p in parts:
                        if p.startswith(l): return True
                    # Fallback: check first character of lyrics
                    lyrics_start = song.get("lyrics", "").strip()[:5].lower()
                    if lyrics_start.startswith(l): return True
                    return False
                    
                results = [s for s in results if check_match(s)]
            # If nothing selected, show only first 50 songs to prevent initial lag
            elif not query and not st["letter"] and len(results) > 50:
                results = results[:50]

            if not results and (st["q"] or st["letter"]):
                new_list.controls.append(ft.Container(
                    content=ft.Text(f"No songs found matching your filter.", color="grey"),
                    padding=40, alignment=ft.Alignment(0, 0)
                ))
            elif not results:
                new_list.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CLOUD_DOWNLOAD, size=60, color="#9E9E9E"),
                        ft.Text("No songs yet!", size=20, weight="bold", color="#616161"),
                        ft.Text("Tap Settings ⚙ → SYNC NOW\nto download songs from cloud.",
                                size=14, color="#9E9E9E", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=60, alignment=ft.Alignment(0, 0)
                ))

            for s in results:
                # Optimized Item: Simple, no shadows, fast rendering
                new_list.controls.append(ft.ListTile(
                    leading=ft.Image(src="icon.png", width=30, height=30, 
                                     error_content=ft.Icon(ft.Icons.MUSIC_NOTE)),
                    title=ft.Text(s.get("title", "Untitled"), weight="bold", color="black", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    subtitle=ft.Text(get_smart_preview(s.get("lyrics", "")), size=12, color="grey", max_lines=1),
                    on_click=lambda e, song=s: show_reader(song),
                    content_padding=ft.padding.symmetric(horizontal=10, vertical=5)
                ))
                new_list.controls.append(ft.Divider(height=1, color="#EEEEEE"))
            return new_list

        def filter_songs(q=None):
            global _search_timer
            if q is not None: 
                st["q"] = q
                if q: st["letter"] = None # Disable letter filter while searching
            
            if _search_timer:
                _search_timer.cancel()
            
            def _apply():
                list_container.content = build_song_list()
                alpha_container.content = build_alpha_row()
                script_row_container.content = build_script_row()
                page.update()
            
            _search_timer = threading.Timer(0.2, _apply)
            _search_timer.start()

        # HEADER
        header = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Image(src="icon.png", width=50, height=50,
                                 error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color="white")),
                        ft.Text("GGGM", color="white", size=24, weight="bold")
                    ]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white",
                                  on_click=lambda _: show_settings())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.TextField(
                    hint_text="Search title or lyrics...", expand=True,
                    bgcolor="white", border_radius=12, border_color="transparent",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=lambda e: filter_songs(e.control.value))
            ])
        )

        lang_row = ft.Container(padding=15, content=ft.Row([
            ft.ElevatedButton(
                "TAMIL", expand=1,
                bgcolor="#E8EAF6" if st["lang"] == "tamil" else "white",
                color="#1A237E" if st["lang"] == "tamil" else "grey",
                on_click=lambda e: change_lang("tamil")),
            ft.ElevatedButton(
                "TELUGU", expand=1,
                bgcolor="#E8EAF6" if st["lang"] == "telugu" else "white",
                color="#1A237E" if st["lang"] == "telugu" else "grey",
                on_click=lambda e: change_lang("telugu"))
        ], spacing=15))

        def change_lang(l):
            st["lang"] = l
            st["letter"] = None
            for btn in lang_row.content.controls:
                label = str(btn.content).lower() if btn.content else ""
                btn.bgcolor = "#E8EAF6" if label == l else "white"
                btn.color = "#1A237E" if label == l else "grey"
            filter_songs()

        home_view = ft.Column([header, lang_row, script_row_container, alpha_container, list_container], spacing=0, expand=True)
        body_container = ft.Container(content=home_view, expand=True, bgcolor="#F5F5F5")
        page.add(body_container)

        # ---- READER ----
        def show_reader(s):
            page.appbar.title = ft.Text(s["title"], color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(
                ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda _: render_home())
            page.appbar.actions = [
                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white",
                              on_click=lambda _: zoom(-2)),
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white",
                              on_click=lambda _: zoom(2))
            ]
            page.appbar.visible = True
            v_list = ft.ListView(expand=True, padding=30)
            lyrics_text = ft.Text(s["lyrics"], size=st["font_size"], color="#2C3E50", weight="500")
            v_list.controls.append(lyrics_text)

            def refresh_reader():
                lyrics_text.size = st["font_size"]
                page.update()

            def zoom(delta):
                st["font_size"] = max(12, min(44, st["font_size"] + delta))
                refresh_reader()

            body_container.content = v_list
            body_container.bgcolor = "#FFF9E1"
            refresh_reader()

        # ---- SETTINGS / SYNC ----
        def show_settings():
            page.appbar.title = ft.Text("Settings", color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(
                ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda _: render_home())
            page.appbar.visible = True
            page.appbar.actions = []

            sync_btn = ft.ElevatedButton(
                "SYNC NOW", icon=ft.Icons.SYNC,
                bgcolor="#1A237E", color="white", height=60)
            status_text = ft.Text("", size=14, text_align=ft.TextAlign.CENTER,
                                  color="#1A237E")
            progress_ring = ft.ProgressRing(
                visible=False, width=30, height=30, color="#1A237E")
            song_count_text = ft.Text(
                f"Local songs: {len(lm.songs)}", color="grey", size=14)

            def sync_act(e):
                sync_btn.disabled = True
                progress_ring.visible = True
                status_text.value = "Connecting to Firebase..."
                status_text.color = "#1A237E"
                page.update()

                def _bg_sync():
                    try:
                        log("Starting cloud sync...")
                        songs = lm.sync_from_cloud()
                        log(f"Sync complete: {len(songs)} songs fetched")

                        # Update data
                        lm.songs = songs
                        lm.save()

                        # Clear current filter to show fresh results
                        st["letter"] = None
                        st["q"] = ""

                        # Update UI
                        progress_ring.visible = False
                        sync_btn.disabled = False
                        status_text.value = f"Success! {len(songs)} songs live."
                        status_text.color = "#2E7D32"
                        song_count_text.value = f"Local songs: {len(songs)}"
                        page.update()
                        
                        # Show snackbar (Flet 0.81 compat)
                        sb = ft.SnackBar(content=ft.Text(f"✅ Synced {len(songs)} songs live!"))
                        sb.open = True
                        page.snack_bar = sb
                        page.update()

                    except Exception as ex:
                        log(f"Sync error: {traceback.format_exc()}")
                        progress_ring.visible = False
                        sync_btn.disabled = False
                        status_text.value = f"Sync Error. Please retry."
                        status_text.color = "#C62828"
                        page.update()
                        
                        sb = ft.SnackBar(content=ft.Text(f"❌ Sync failed. Try again."))
                        sb.open = True
                        page.snack_bar = sb
                        page.update()

                threading.Thread(target=_bg_sync, daemon=True).start()

            sync_btn.on_click = sync_act

            body_container.content = ft.Container(
                padding=30,
                content=ft.Column([
                    ft.Image(src="icon.png", width=120, height=120,
                             error_content=ft.Icon(ft.Icons.MUSIC_NOTE, size=100)),
                    ft.Container(height=20),
                    ft.Text("Cloud Sync", size=24, weight="bold", color="black"),
                    ft.Text(f"Project: {PROJECT_ID}", color="grey"),
                    song_count_text,
                    ft.Container(height=20),
                    sync_btn,
                    ft.Container(height=10),
                    ft.Row([progress_ring, status_text],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Divider(),
                    ft.Text("GGGM v7.0.0", color="grey", size=12)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            body_container.bgcolor = "#F5F5F5"
            page.update()

        def render_home():
            page.appbar.visible = False
            body_container.content = home_view
            body_container.bgcolor = "#F5F5F5"
            filter_songs()

        # INITIAL DRAW
        filter_songs()

    except Exception:
        err_msg = traceback.format_exc()
        log(f"FATAL ERROR: {err_msg}")
        page.add(ft.Container(
            padding=20, bgcolor="red", expand=True,
            content=ft.Text(f"INTERNAL ERROR:\n{err_msg}", color="white")))

ft.app(target=main)
