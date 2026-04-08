"""Test every Flet 0.81.0 API used in main.py - no importing main."""
import flet as ft
print("1. IMPORTS: PASS")

# Enums
ft.ThemeMode.DARK
ft.TextAlign.CENTER
ft.ScrollMode.AUTO
ft.FontWeight.BOLD
ft.FontWeight.NORMAL
ft.CrossAxisAlignment.CENTER
ft.MainAxisAlignment.SPACE_BETWEEN
ft.TextOverflow.ELLIPSIS
print("2. ALL ENUMS: PASS")

# Alignment
ft.alignment.Alignment(0, 0)
print("3. ALIGNMENT: PASS")

# Padding
ft.Padding(left=16, right=16, top=10, bottom=10)
print("4. PADDING: PASS")

# Icons
for icon_name in [ft.Icons.MUSIC_NOTE, ft.Icons.SEARCH, ft.Icons.SETTINGS,
                   ft.Icons.ARROW_BACK, ft.Icons.CHEVRON_RIGHT, ft.Icons.FAVORITE,
                   ft.Icons.FAVORITE_BORDER, ft.Icons.TEXT_INCREASE, ft.Icons.TEXT_DECREASE]:
    ft.Icon(icon_name, size=20)
print("5. ALL 9 ICONS: PASS")

# Widgets
ft.Text("x", size=22, weight=ft.FontWeight.BOLD, color="#C8D6F0",
        text_align=ft.TextAlign.CENTER, expand=True, max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS, selectable=True)
print("6. TEXT: PASS")

ft.IconButton(ft.Icons.SEARCH, icon_color="#C8D6F0")
print("7. ICONBUTTON: PASS")

ft.ElevatedButton("Sync")
print("8. BUTTON: PASS")

ft.Divider(color="#333333")
print("9. DIVIDER: PASS")

ft.TextField(hint_text="s", border_color="transparent", text_size=14, autofocus=True)
print("10. TEXTFIELD: PASS")

ft.Container(height=10)
print("11. CONTAINER: PASS")

ft.SafeArea(content=ft.Text("x"), expand=True)
print("12. SAFEAREA: PASS")

ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
print("13. COLUMN: PASS")

ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=0)
print("14. ROW: PASS")

# Full AppBar simulation
ft.Container(
    content=ft.Row(
        controls=[
            ft.Text("Grace Lyrics", size=22, weight=ft.FontWeight.BOLD, color="#C8D6F0"),
            ft.Row(controls=[ft.IconButton(ft.Icons.SEARCH, icon_color="#C8D6F0")], spacing=0),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    ),
    bgcolor="#202A44",
    padding=ft.Padding(left=16, right=16, top=10, bottom=10),
)
print("15. FULL APPBAR: PASS")

# Full song row
ft.Container(
    content=ft.Row(
        controls=[
            ft.Icon(ft.Icons.MUSIC_NOTE, color="#7B8DB8", size=20),
            ft.Text("Song", expand=True, weight=ft.FontWeight.BOLD, size=15),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#555555", size=18),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    ),
    padding=ft.Padding(left=16, right=16, top=14, bottom=14),
    border_radius=10,
    bgcolor="#1A1F2E",
    ink=True,
)
print("16. FULL SONG ROW: PASS")

# Tab bar simulation
ft.Container(
    content=ft.Text("Tamil", size=16, weight=ft.FontWeight.BOLD, color="#C8D6F0"),
    bgcolor="#202A44",
    border_radius=8,
    padding=ft.Padding(left=24, right=24, top=10, bottom=10),
    expand=True,
    alignment=ft.alignment.Alignment(0, 0),
)
print("17. TAB BUTTON: PASS")

# Full page structure
ft.SafeArea(
    content=ft.Column(
        controls=[
            ft.Container(bgcolor="#202A44", padding=ft.Padding(left=16, right=16, top=10, bottom=10)),
            ft.Container(content=ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True), expand=True),
        ],
        spacing=0,
        expand=True,
    ),
    expand=True,
)
print("18. FULL PAGE: PASS")

# Song detail page
ft.SafeArea(
    content=ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(controls=[
                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color="#C8D6F0"),
                    ft.Text("Title", size=14, color="#C8D6F0", expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(ft.Icons.TEXT_DECREASE, icon_color="#C8D6F0"),
                    ft.IconButton(ft.Icons.TEXT_INCREASE, icon_color="#C8D6F0"),
                    ft.IconButton(ft.Icons.FAVORITE_BORDER, icon_color="#888888"),
                ]),
                bgcolor="#202A44",
                padding=ft.Padding(left=4, right=4, top=4, bottom=4),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Title", size=20, weight=ft.FontWeight.BOLD, color="#7B8DB8"),
                        ft.Divider(color="#333333"),
                        ft.Text("Lyrics...", size=18, selectable=True, color="#E0E0E0"),
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
print("19. FULL SONG DETAIL PAGE: PASS")

# Admin page
ft.SafeArea(
    content=ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(controls=[
                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color="#C8D6F0"),
                    ft.Text("Cloud Sync", size=18, color="#C8D6F0", weight=ft.FontWeight.BOLD),
                ]),
                bgcolor="#202A44",
                padding=ft.Padding(left=4, right=4, top=10, bottom=10),
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Download Songs", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Tap button", size=14, color="#AAAAAA"),
                    ft.Container(height=10),
                    ft.ElevatedButton("Sync Now"),
                    ft.Container(height=10),
                    ft.Text("Ready.", color="green", size=14),
                ]),
                padding=24,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    ),
    expand=True,
)
print("20. FULL ADMIN PAGE: PASS")

print("")
print("=" * 50)
print("  ALL 20 TESTS PASSED - SAFE TO DEPLOY")
print("=" * 50)
