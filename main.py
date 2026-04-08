import flet as ft
import json
import urllib.request
import threading
import time

# ===================== IN-MEMORY DATA STORE =====================
SONGS = []

FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-admin/databases/(default)/documents/songs"

def seed_default_songs():
    global SONGS
    if len(SONGS) > 0:
        return
    SONGS = [
        {
            "id": "ta_172",
            "title": "172. கர்த்தாவே தேவர்களில்",
            "language": "tamil",
            "is_favorite": False,
            "lyrics": (
                "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்?\n"
                "வானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\n"
                "உமக்கொப்பனவர் யார்? உமக்கொப்பனவர் யார்?\n"
                "வானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\n"
                "1. செங்கடலை நீர் பிளந்து\n"
                "உந்தன் ஜனங்களை நடத்திச் சென்றீர்\n"
                "நீர் நல்லவர் சர்வ வல்லவர்\n"
                "என்றும் வாக்கு மாறாதவர் (2)\n\n"
                "2. தூதர்கள் உண்ணும் உணவால்\n"
                "உந்தன் ஜனங்களை போஷித்தீரே\n"
                "உம்மைப்போல யாருண்டு\n"
                "இந்த ஜனங்களை நேசித்திட (2)"
            ),
        },
        {
            "id": "te_1",
            "title": "అగ్ని మండించు - Agni Mandinchu",
            "language": "telugu",
            "is_favorite": False,
            "lyrics": (
                "అగ్ని మండించు – నాలో అగ్ని మండించు (2)\n"
                "పరిశుద్ధాత్ముడా – నాలో అగ్ని మండించు (2)\n\n"
                "Agni Mandinchu – Naalo Agni Mandinchu (2)\n"
                "Parishuddhaathmudaa – Naalo Agni Mandinchu (2)"
            ),
        },
    ]

def get_filtered(lang, query=""):
    result = []
    for s in SONGS:
        if s["language"] != lang:
            continue
        if query and query.lower() not in s["title"].lower():
            continue
        result.append(s)
    return sorted(result, key=lambda x: x["title"])

def cloud_sync():
    global SONGS
    count = 0
    try:
        req = urllib.request.Request(FIRESTORE_URL)
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            docs = data.get("documents", [])
            
            # Using a temp set to track favorites across sync
            fav_ids = {s["id"] for s in SONGS if s.get("is_favorite", False)}
            
            new_songs = []
            for doc in docs:
                sid = doc.get("name", "").split("/")[-1]
                fields = doc.get("fields", {})
                
                song = {
                    "id": sid,
                    "title": fields.get("title", {}).get("stringValue", "Untitled"),
                    "language": fields.get("language", {}).get("stringValue", "tamil").lower(),
                    "lyrics": fields.get("lyrics", {}).get("stringValue", "").replace("\\n", "\n"),
                    "is_favorite": sid in fav_ids,
                }
                new_songs.append(song)
                count += 1
            
            if new_songs:
                SONGS = new_songs
    except Exception as e:
        print(f"Sync error: {e}")
    return count

# ===================== MAIN APP =====================
def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F7FA" # Light silver/gray background
    page.padding = 0

    try:
        seed_default_songs()
    except Exception as e:
        page.add(ft.SafeArea(ft.Text(f"Initialization Error: {e}", color="red")))
        return

    # ---- State ----
    current_tab = [0]  # 0=Tamil, 1=Telugu
    search_query = [""]
    search_open = [False]
    is_syncing = [False]

    def refresh_ui():
        try:
            show_home()
        except:
            pass

    def start_auto_sync():
        if is_syncing[0]:
            return
        is_syncing[0] = True
        try:
            c = cloud_sync()
            if c > 0:
                page.run_task(refresh_ui)
        finally:
            is_syncing[0] = False

    # ---- Build song list ----
    def make_song_list(lang, query=""):
        songs = get_filtered(lang, query)
        if not songs:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CLOUD_OFF, size=50, color="#B0BEC5"),
                        ft.Text(
                            "No songs found.\nChecking for updates...",
                            text_align=ft.TextAlign.CENTER,
                            color="#78909C",
                            size=16,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                padding=40,
            )
        
        col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        for s in songs:
            fav = s.get("is_favorite", False)
            col.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.MUSIC_NOTE, color="#3F51B5", size=22),
                                padding=10,
                                bgcolor="#E8EAF6",
                                border_radius=10,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(s["title"], weight=ft.FontWeight.BOLD, size=16, color="#263238"),
                                    ft.Text(s["language"].capitalize(), size=12, color="#90A4AE"),
                                ],
                                expand=True,
                                spacing=0,
                            ),
                            ft.Icon(ft.Icons.FAVORITE, color="#FF5252", size=22) if fav else ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#CFD8DC", size=24),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    border_radius=15,
                    bgcolor="white",
                    on_click=lambda e, sid=s["id"]: show_song(sid),
                    shadow=ft.BoxShadow(
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.05, "black"),
                        offset=ft.Offset(0, 4)
                    ),
                    ink=True,
                )
            )
        return col

    # ---- Tab Bar ----
    def make_tab_bar():
        def select_tab(idx):
            current_tab[0] = idx
            show_home()

        tamil_active = current_tab[0] == 0
        telugu_active = current_tab[0] == 1

        return ft.Container(
             padding=ft.Padding(left=10, right=10, top=5, bottom=5),
             bgcolor="#E1E5F2",
             border_radius=25,
             content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text("Tamil", size=14, weight=ft.FontWeight.BOLD if tamil_active else ft.FontWeight.NORMAL, color="white" if tamil_active else "#5C6BC0"),
                        bgcolor="#3F51B5" if tamil_active else "transparent",
                        border_radius=20,
                        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
                        on_click=lambda e: select_tab(0),
                        expand=True,
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Text("Telugu", size=14, weight=ft.FontWeight.BOLD if telugu_active else ft.FontWeight.NORMAL, color="white" if telugu_active else "#5C6BC0"),
                        bgcolor="#3F51B5" if telugu_active else "transparent",
                        border_radius=20,
                        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
                        on_click=lambda e: select_tab(1),
                        expand=True,
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                ],
                spacing=5,
            )
        )

    # ---- HOME SCREEN ----
    def show_home():
        try:
            lang = "tamil" if current_tab[0] == 0 else "telugu"
            song_list = make_song_list(lang, search_query[0])

            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("Grace Lyrics", size=24, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text("Songs of Worship", size=12, color="#C5CAE9"),
                        ], spacing=2),
                        ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.SEARCH, icon_color="white", on_click=lambda e: toggle_search(e)),
                                ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda e: show_admin()),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#3F51B5", "#7986CB"]
                ),
                padding=ft.Padding(left=20, right=10, top=20, bottom=20),
            )

            controls = [header]

            if search_open[0]:
                controls.append(
                    ft.Container(
                        content=ft.TextField(
                            hint_text="Search song title...",
                            on_change=on_search_change,
                            value=search_query[0],
                            autofocus=True,
                            border_color="#C5CAE9",
                            border_radius=15,
                            prefix_icon=ft.Icons.SEARCH,
                            text_size=14,
                            bgcolor="white",
                        ),
                        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                    )
                )

            controls.append(
                ft.Container(
                    content=make_tab_bar(),
                    padding=ft.Padding(left=20, right=20, top=15, bottom=10),
                )
            )

            controls.append(
                ft.Container(content=song_list, padding=15, expand=True)
            )

            page.controls.clear()
            page.add(ft.SafeArea(content=ft.Column(controls=controls, spacing=0, expand=True), expand=True))
            page.update()
        except Exception as e:
            page.controls.clear()
            page.add(ft.SafeArea(ft.Text(f"Home error: {e}", color="red")))
            page.update()

    def on_search_change(e):
        search_query[0] = e.control.value
        show_home()

    def toggle_search(e):
        search_open[0] = not search_open[0]
        if not search_open[0]:
            search_query[0] = ""
        show_home()

    # ---- SONG DETAIL SCREEN ----
    def show_song(song_id):
        try:
            song = next((s for s in SONGS if s["id"] == song_id), None)
            if not song: return

            font_size = [18]
            lyrics_widget = ft.Text(song["lyrics"], size=font_size[0], selectable=True, color="#37474F", line_height=1.5)

            def update_font(delta):
                font_size[0] = max(10, min(40, font_size[0] + delta))
                lyrics_widget.size = font_size[0]
                page.update()

            def toggle_fav(e):
                song["is_favorite"] = not song.get("is_favorite", False)
                show_song(song_id)

            is_fav = song.get("is_favorite", False)

            page.controls.clear()
            page.add(
                ft.SafeArea(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: show_home()),
                                        ft.Text(song["title"], size=16, color="white", weight=ft.FontWeight.BOLD, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Row([
                                            ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda e: update_font(-2)),
                                            ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda e: update_font(2)),
                                            ft.IconButton(ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER, icon_color="#FFCDD2" if is_fav else "white", on_click=toggle_fav),
                                        ], spacing=0)
                                    ],
                                ),
                                bgcolor="#3F51B5",
                                padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(song["title"], size=22, weight=ft.FontWeight.BOLD, color="#1A237E"),
                                        ft.Divider(color="#E8EAF6", height=30),
                                        lyrics_widget,
                                        ft.Container(height=50),
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                padding=25,
                                bgcolor="white",
                                expand=True,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                )
            )
            page.update()
        except Exception as e:
            page.controls.clear()
            page.add(ft.SafeArea(ft.Text(f"Song detail error: {e}", color="red")))
            page.update()

    # ---- ADMIN / SYNC SCREEN ----
    def show_admin():
        try:
            status = ft.Text("Ready to sync.", color="#43A047", size=14)

            def do_sync(e):
                status.value = "Syncing from cloud..."
                status.color = "#3F51B5"
                page.update()
                try:
                    c = cloud_sync()
                    status.value = f"Success! {c} songs updated."
                    status.color = "#43A047"
                except Exception as ex:
                    status.value = f"Sync failed: {ex}"
                    status.color = "#E53935"
                page.update()

            page.controls.clear()
            page.add(
                ft.SafeArea(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: show_home()),
                                    ft.Text("Settings", size=20, color="white", weight=ft.FontWeight.BOLD),
                                ]),
                                bgcolor="#3F51B5",
                                padding=ft.Padding(left=5, right=5, top=10, bottom=10),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Cloud Sync", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
                                        ft.Text("Update your song library with the latest lyrics from the server.", size=14, color="#546E7A"),
                                        ft.Container(height=20),
                                        ft.ElevatedButton(
                                            content=ft.Row([ft.Icon(ft.Icons.SYNC), ft.Text("SYNC NOW")], alignment=ft.MainAxisAlignment.CENTER),
                                            on_click=do_sync,
                                            height=50,
                                            style=ft.ButtonStyle(
                                                color="white",
                                                bgcolor="#3F51B5",
                                                shape=ft.RoundedRectangleBorder(radius=15),
                                            )
                                        ),
                                        ft.Container(height=15),
                                        status,
                                    ],
                                ),
                                padding=30,
                                expand=True,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                )
            )
            page.update()
        except Exception as e:
            page.controls.clear()
            page.add(ft.SafeArea(ft.Text(f"Settings error: {e}", color="red")))
            page.update()

    # ---- START ----
    show_home()
    # Trigger auto-sync in background
    threading.Thread(target=start_auto_sync, daemon=True).start()

ft.app(main)
