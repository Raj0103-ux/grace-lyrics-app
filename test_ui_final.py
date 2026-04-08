"""Final validation of all UI widgets and alignment used in the NEW bright UI."""
import flet as ft
print("1. Imports OK")

# Custom Alignment objects
ft.alignment.Alignment(-1, -1) # top_left replacement
ft.alignment.Alignment(1, 1)   # bottom_right replacement
ft.alignment.Alignment(0, 0)   # center replacement
print("2. Alignment Objects OK")

# LinearGradient
ft.LinearGradient(
    begin=ft.alignment.Alignment(-1, -1),
    end=ft.alignment.Alignment(1, 1),
    colors=["#3F51B5", "#7986CB"]
)
print("3. LinearGradient OK")

# Colors with opacity
ft.Colors.with_opacity(0.05, "black")
print("4. Color Opacity OK")

# Offset
ft.Offset(0, 4)
print("5. Offset OK")

# BoxShadow
ft.BoxShadow(
    blur_radius=10,
    color=ft.Colors.with_opacity(0.05, "black"),
    offset=ft.Offset(0, 4)
)
print("6. BoxShadow OK")

# RoundedRectangleBorder (used in sync button)
ft.RoundedRectangleBorder(radius=15)
print("7. RoundedRectangleBorder OK")

# ButtonStyle
ft.ButtonStyle(
    color="white",
    bgcolor="#3F51B5",
    shape=ft.RoundedRectangleBorder(radius=15),
)
print("8. ButtonStyle OK")

# New Icons added
for ico in [ft.Icons.CLOUD_OFF, ft.Icons.SYNC, ft.Icons.REMOVE_CIRCLE_OUTLINE, ft.Icons.ADD_CIRCLE_OUTLINE]:
    ft.Icon(ico)
print("9. New Icons OK")

print("\n" + "="*30)
print(" ALL DESKTOP TESTS PASSED ")
print("="*30)
