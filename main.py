import flet as ft
import json
import urllib.request

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
                "இந்த ஜனங்களை நேசித்திட (2)\n\n"
                "3. கன்மலையை நீர் பிளந்து\n"
                "உந்தன் ஜனங்களின் தாகம் தீர்த்தீர்\n"
                "உந்தன் நாமம் அதிசயம்\n"
                "இன்றும் அற்புதம் செய்திடுவீர் (2)"
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
    req = urllib.request.Request(FIRESTORE_URL)
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        docs = json.loads(body).get("documents", [])
        existing_ids = {s["id"] for s in SONGS}
        for doc in docs:
            sid = doc.get("name", "").split("/")[-1]
            f = doc.get("fields", {})
            song = {
                "id": sid,
                "title": f.get("title", {}).get("stringValue", ""),
                "language": f.get("language", {}).get("stringValue", ""),
                "lyrics": f.get("lyrics", {}).get("stringValue", "").replace("\\n", "\n"),
                "is_favorite": False,
            }
            if sid in existing_ids:
                for i, existing in enumerate(SONGS):
                    if existing["id"] == sid:
                        song["is_favorite"] = existing.get("is_favorite", False)
                        SONGS[i] = song
                        break
            else:
                SONGS.append(song)
            count += 1
    return count


# ===================== MAIN APP =====================
def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0D1117"
    page.padding = 0

    try:
        seed_default_songs()
    except Exception as e:
        page.add(ft.SafeArea(ft.Text(f"Seed error: {e}", color="red", selectable=True)))
        return

    # ---- State ----
    current_tab = [0]  # 0=Tamil, 1=Telugu
    search_query = [""]
    search_open = [False]

    # ---- Build song list ----
    def make_song_list(lang, query=""):
        songs = get_filtered(lang, query)
        if not songs:
            return ft.Container(
                content=ft.Text(
                    "No songs loaded.\nTap Settings > Sync to download.",
                    text_align=ft.TextAlign.CENTER,
                    color="#888888",
                    size=16,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
        col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
        for s in songs:
            fav = s.get("is_favorite", False)
            col.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MUSIC_NOTE, color="#7B8DB8", size=20),
                            ft.Text(s["title"], expand=True, weight=ft.FontWeight.BOLD, size=15),
                            ft.Icon(ft.Icons.FAVORITE, color="red", size=18) if fav else ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#555555", size=18),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                    border_radius=10,
                    bgcolor="#1A1F2E",
                    on_click=lambda e, sid=s["id"]: show_song(sid),
                    ink=True,
                )
            )
        return col

    # ---- Custom Tab Bar (no ft.Tabs needed) ----
    def make_tab_bar():
        def select_tab(idx):
            current_tab[0] = idx
            show_home()

        tamil_active = current_tab[0] == 0
        telugu_active = current_tab[0] == 1

        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("Tamil", size=16, weight=ft.FontWeight.BOLD if tamil_active else ft.FontWeight.NORMAL, color="#C8D6F0" if tamil_active else "#666666"),
                    bgcolor="#202A44" if tamil_active else "transparent",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=24, vertical=10),
                    on_click=lambda e: select_tab(0),
                    expand=True,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text("Telugu", size=16, weight=ft.FontWeight.BOLD if telugu_active else ft.FontWeight.NORMAL, color="#C8D6F0" if telugu_active else "#666666"),
                    bgcolor="#202A44" if telugu_active else "transparent",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=24, vertical=10),
                    on_click=lambda e: select_tab(1),
                    expand=True,
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=4,
        )

    # ---- Search ----
    def on_search_change(e):
        search_query[0] = e.control.value
        show_home()

    def toggle_search(e):
        search_open[0] = not search_open[0]
        if not search_open[0]:
            search_query[0] = ""
        show_home()

    # ---- HOME SCREEN ----
    def show_home():
        try:
            lang = "tamil" if current_tab[0] == 0 else "telugu"
            song_list = make_song_list(lang, search_query[0])

            controls = [
                # App Bar
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Grace Lyrics", size=22, weight=ft.FontWeight.BOLD, color="#C8D6F0"),
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.Icons.SEARCH, icon_color="#C8D6F0", on_click=toggle_search),
                                    ft.IconButton(ft.Icons.SETTINGS, icon_color="#C8D6F0", on_click=lambda e: show_admin()),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#202A44",
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ),
            ]

            # Search bar
            if search_open[0]:
                controls.append(
                    ft.Container(
                        content=ft.TextField(
                            hint_text="Search song title...",
                            on_change=on_search_change,
                            value=search_query[0],
                            autofocus=True,
                            border_color="transparent",
                            text_size=14,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=4),
                    )
                )

            # Tab bar
            controls.append(
                ft.Container(
                    content=make_tab_bar(),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor="#111520",
                )
            )

            # Song list
            controls.append(
                ft.Container(content=song_list, padding=10, expand=True)
            )

            page.controls.clear()
            page.add(ft.SafeArea(content=ft.Column(controls=controls, spacing=0, expand=True), expand=True))
            page.update()
        except Exception as e:
            page.controls.clear()
            page.add(ft.SafeArea(ft.Text(f"Home error: {e}", color="red", selectable=True)))
            page.update()

    # ---- SONG DETAIL SCREEN ----
    def show_song(song_id):
        try:
            song = None
            for s in SONGS:
                if s["id"] == song_id:
                    song = s
                    break
            if not song:
                return

            font_size = [18]
            lyrics_widget = ft.Text(song["lyrics"], size=font_size[0], selectable=True, color="#E0E0E0")

            def inc_font(e):
                if font_size[0] < 40:
                    font_size[0] += 2
                    lyrics_widget.size = font_size[0]
                    page.update()

            def dec_font(e):
                if font_size[0] > 10:
                    font_size[0] -= 2
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
                            # Top bar
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.IconButton(ft.Icons.ARROW_BACK, icon_color="#C8D6F0", on_click=lambda e: show_home()),
                                        ft.Text(song["title"], size=14, color="#C8D6F0", expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.IconButton(ft.Icons.TEXT_DECREASE, icon_color="#C8D6F0", on_click=dec_font),
                                        ft.IconButton(ft.Icons.TEXT_INCREASE, icon_color="#C8D6F0", on_click=inc_font),
                                        ft.IconButton(
                                            ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
                                            icon_color="red" if is_fav else "#888888",
                                            on_click=toggle_fav,
                                        ),
                                    ],
                                ),
                                bgcolor="#202A44",
                                padding=ft.padding.symmetric(horizontal=4, vertical=4),
                            ),
                            # Lyrics body
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(song["title"], size=20, weight=ft.FontWeight.BOLD, color="#7B8DB8"),
                                        ft.Divider(color="#333333"),
                                        lyrics_widget,
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                padding=20,
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
            page.add(ft.SafeArea(ft.Text(f"Song error: {e}", color="red", selectable=True)))
            page.update()

    # ---- ADMIN / SYNC SCREEN ----
    def show_admin():
        try:
            status = ft.Text("Ready to sync.", color="green", size=14)

            def do_sync(e):
                status.value = "Syncing from cloud..."
                status.color = "#4488FF"
                page.update()
                try:
                    c = cloud_sync()
                    status.value = f"Done! Synced {c} songs from cloud."
                    status.color = "green"
                except Exception as ex:
                    status.value = f"Sync failed: {ex}"
                    status.color = "red"
                page.update()

            page.controls.clear()
            page.add(
                ft.SafeArea(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.IconButton(ft.Icons.ARROW_BACK, icon_color="#C8D6F0", on_click=lambda e: show_home()),
                                        ft.Text("Cloud Sync", size=18, color="#C8D6F0", weight=ft.FontWeight.BOLD),
                                    ],
                                ),
                                bgcolor="#202A44",
                                padding=ft.padding.symmetric(horizontal=4, vertical=10),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Download Songs", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Text("Tap the button below to download the latest songs pushed by the admin.", size=14, color="#AAAAAA"),
                                        ft.Container(height=10),
                                        ft.ElevatedButton("Sync Now", on_click=do_sync),
                                        ft.Container(height=10),
                                        status,
                                    ],
                                ),
                                padding=24,
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
            page.add(ft.SafeArea(ft.Text(f"Admin error: {e}", color="red", selectable=True)))
            page.update()

    # ---- START ----
    show_home()


ft.app(main)
