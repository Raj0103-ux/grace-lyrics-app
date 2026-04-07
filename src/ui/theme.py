import flet as ft

primary_color = "#202A44" # Dark Blue
secondary_color = "#C0C0C0" # Silver
surface_color = "#121212" if True else "#FFFFFF"

def get_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=primary_color,
            secondary=secondary_color,
        ),
        use_material3=True,
    )
