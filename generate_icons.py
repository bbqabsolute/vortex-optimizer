"""
Icon generator for VORTEX Gaming Engine
Generates crisp, antialiased 2x icons (96x96 downsampled to 48x48) with alpha transparency.
"""
import os
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")
os.makedirs(ASSETS_DIR, exist_ok=True)

SCALE = 4  # 4x supersampling for ultra-crisp antialiased vector appearance
SIZE = 48 * SCALE

def create_base_canvas():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

def save_icon(img, name):
    target = img.resize((48, 48), Image.Resampling.LANCZOS)
    path = os.path.join(ASSETS_DIR, f"{name}.png")
    target.save(path, "PNG")
    return path

# 1. Dashboard: 4 rounded squares (2x2 grid)
def draw_dashboard():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255) # #94A3B8
    stroke = 14
    r = 24
    
    # Top-left, top-right, bottom-left, bottom-right
    d.rounded_rectangle([28, 28, 86, 86], radius=r, outline=color, width=stroke)
    d.rounded_rectangle([106, 28, 164, 86], radius=r, outline=color, width=stroke)
    d.rounded_rectangle([28, 106, 86, 164], radius=r, outline=color, width=stroke)
    d.rounded_rectangle([106, 106, 164, 164], radius=r, outline=color, width=stroke)
    save_icon(img, "nav_dashboard")

# 2. Resolution: Monitor screen with base
def draw_resolution():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Screen
    d.rounded_rectangle([24, 32, 168, 136], radius=20, outline=color, width=stroke)
    # Stand neck
    d.line([(96, 136), (96, 162)], fill=color, width=stroke)
    # Stand foot
    d.line([(64, 162), (128, 162)], fill=color, width=stroke)
    save_icon(img, "nav_resolution")

# 3. Network: Globe circle with latitude & longitude
def draw_network():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Circle
    d.ellipse([26, 26, 166, 166], outline=color, width=stroke)
    # Equator line
    d.line([(26, 96), (166, 96)], fill=color, width=stroke)
    # Center vertical line
    d.line([(96, 26), (96, 166)], fill=color, width=stroke)
    # Longitude ellipse
    d.ellipse([60, 26, 132, 166], outline=color, width=stroke)
    save_icon(img, "nav_network")

# 4. Latency: Sharp Lightning Bolt
def draw_latency():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    
    # Lightning bolt polygon
    points = [
        (110, 22),
        (56, 102),
        (96, 102),
        (82, 170),
        (138, 90),
        (98, 90)
    ]
    d.polygon(points, fill=color)
    save_icon(img, "nav_latency")

# 5. Services: Server rack (two horizontal units with LEDs)
def draw_services():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Unit 1
    d.rounded_rectangle([24, 36, 168, 86], radius=16, outline=color, width=stroke)
    d.ellipse([48, 56, 60, 68], fill=color)
    d.line([(80, 61), (144, 61)], fill=color, width=10)
    
    # Unit 2
    d.rounded_rectangle([24, 106, 168, 156], radius=16, outline=color, width=stroke)
    d.ellipse([48, 126, 60, 138], fill=color)
    d.line([(80, 131), (144, 131)], fill=color, width=10)
    save_icon(img, "nav_services")

# 6. Tweaks: Horizontal adjustment sliders
def draw_tweaks():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Top track
    d.line([(30, 56), (162, 56)], fill=color, width=stroke)
    d.rounded_rectangle([68, 40, 94, 72], radius=8, fill=color)
    
    # Middle track
    d.line([(30, 96), (162, 96)], fill=color, width=stroke)
    d.rounded_rectangle([118, 80, 144, 112], radius=8, fill=color)
    
    # Bottom track
    d.line([(30, 136), (162, 136)], fill=color, width=stroke)
    d.rounded_rectangle([48, 120, 74, 152], radius=8, fill=color)
    save_icon(img, "nav_tweaks")

# 7. Presets: Folder / Profile cards
def draw_presets():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Back card
    d.rounded_rectangle([52, 28, 164, 136], radius=16, outline=(100, 116, 139, 255), width=stroke)
    # Front card
    d.rounded_rectangle([28, 56, 140, 164], radius=16, outline=color, width=stroke)
    save_icon(img, "nav_presets")

# 8. Ping: Signal bars
def draw_ping():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    w = 22
    
    # 4 bars of ascending heights
    d.rounded_rectangle([32, 128, 32 + w, 160], radius=8, fill=color)
    d.rounded_rectangle([68, 98, 68 + w, 160], radius=8, fill=color)
    d.rounded_rectangle([104, 68, 104 + w, 160], radius=8, fill=color)
    d.rounded_rectangle([140, 38, 140 + w, 160], radius=8, fill=color)
    save_icon(img, "nav_ping")

# 9. Cleanup: Clean Broom / Sweep sparkle
def draw_cleanup():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Sparkle stars
    # Center star
    d.line([(96, 32), (96, 128)], fill=color, width=stroke)
    d.line([(48, 80), (144, 80)], fill=color, width=stroke)
    d.line([(62, 46), (130, 114)], fill=color, width=stroke)
    d.line([(62, 114), (130, 46)], fill=color, width=stroke)
    
    # Small star bottom right
    d.line([(140, 130), (140, 166)], fill=color, width=10)
    d.line([(122, 148), (158, 148)], fill=color, width=10)
    save_icon(img, "nav_cleanup")

# 10. Restore: Circular Reset arrow
def draw_restore():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (148, 163, 184, 255)
    stroke = 14
    
    # Arc (approx 270 degrees)
    d.arc([32, 32, 160, 160], start=45, end=330, fill=color, width=stroke)
    # Arrow head
    d.polygon([(160, 32), (180, 68), (140, 68)], fill=color)
    save_icon(img, "nav_restore")

# 11. Quick RAM icon (Memory chip)
def draw_action_ram():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (56, 189, 248, 255) # #38BDF8
    stroke = 14
    
    # Central chip
    d.rounded_rectangle([44, 44, 148, 148], radius=16, outline=color, width=stroke)
    # Inner core
    d.rounded_rectangle([72, 72, 120, 120], radius=8, fill=color)
    
    # Pins top, bottom, left, right
    for offset in [66, 96, 126]:
        d.line([(offset, 22), (offset, 44)], fill=color, width=10)
        d.line([(offset, 148), (offset, 170)], fill=color, width=10)
        d.line([(22, offset), (44, offset)], fill=color, width=10)
        d.line([(148, offset), (170, offset)], fill=color, width=10)
    save_icon(img, "action_ram")

# 12. Quick DNS icon
def draw_action_dns():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (52, 211, 153, 255) # #34D399
    stroke = 14
    
    d.arc([32, 32, 160, 160], start=30, end=300, fill=color, width=stroke)
    d.polygon([(160, 32), (180, 68), (140, 68)], fill=color)
    d.ellipse([76, 76, 116, 116], outline=color, width=stroke)
    save_icon(img, "action_dns")

# 13. Quick Timer icon (Stopwatch)
def draw_action_timer():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (251, 191, 36, 255) # #FBBF24
    stroke = 14
    
    # Main clock body
    d.ellipse([34, 46, 158, 170], outline=color, width=stroke)
    # Top button
    d.line([(96, 22), (96, 46)], fill=color, width=stroke)
    d.line([(80, 22), (112, 22)], fill=color, width=10)
    # Clock hands (at 12 and 3)
    d.line([(96, 108), (96, 70)], fill=color, width=12)
    d.line([(96, 108), (126, 108)], fill=color, width=12)
    save_icon(img, "action_timer")

# 14. Quick Services icon (Epic server signal)
def draw_action_servers():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    color = (167, 139, 250, 255) # #A78BFA
    stroke = 14
    
    # Two stacked server slabs
    d.rounded_rectangle([28, 44, 164, 94], radius=14, outline=color, width=stroke)
    d.ellipse([50, 62, 64, 76], fill=color)
    d.line([(84, 69), (144, 69)], fill=color, width=10)
    
    d.rounded_rectangle([28, 108, 164, 158], radius=14, outline=color, width=stroke)
    d.ellipse([50, 126, 64, 140], fill=color)
    d.line([(84, 133), (144, 133)], fill=color, width=10)
    save_icon(img, "action_servers")

# 15. VORTEX Brand Logo (Stylized bold V)
def draw_vortex_logo():
    img = create_base_canvas()
    d = ImageDraw.Draw(img)
    
    # Stylized sharp V with speed bevel
    # Left wing
    d.polygon([(32, 36), (68, 36), (96, 128), (76, 158), (32, 36)], fill=(37, 99, 235, 255))
    # Right wing
    d.polygon([(160, 36), (124, 36), (96, 128), (116, 158), (160, 36)], fill=(96, 165, 250, 255))
    save_icon(img, "vortex_logo")

if __name__ == "__main__":
    draw_dashboard()
    draw_resolution()
    draw_network()
    draw_latency()
    draw_services()
    draw_tweaks()
    draw_presets()
    draw_ping()
    draw_cleanup()
    draw_restore()
    draw_action_ram()
    draw_action_dns()
    draw_action_timer()
    draw_action_servers()
    draw_vortex_logo()
    print("All VORTEX icons successfully generated!")
