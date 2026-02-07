import os
import subprocess
from PIL import Image, ImageDraw

def create_icon():
    print("🎨 Generating App Icon...")
    size = 1024
    
    # Warna Tema
    bg_color = (35, 35, 35, 255)    # Dark Grey (Elegan)
    red_color = (255, 0, 0, 255)    # YouTube Red
    white_color = (255, 255, 255, 255)

    # Buat Canvas Transparan
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Squircle (Kotak Sudut Tumpul Khas macOS)
    # Radius ~22% dari ukuran total
    r = int(size * 0.22) 
    draw.rounded_rectangle([0, 0, size, size], radius=r, fill=bg_color)

    # 2. Lingkaran Merah di Tengah
    center = size // 2
    circle_r = int(size * 0.35)
    draw.ellipse([center - circle_r, center - circle_r, center + circle_r, center + circle_r], fill=red_color)

    # 3. Panah Download Putih
    # Batang Panah
    stem_w = int(size * 0.12)
    stem_h = int(size * 0.25)
    stem_top = center - int(size * 0.15)
    draw.rectangle([center - stem_w//2, stem_top, center + stem_w//2, stem_top + stem_h], fill=white_color)

    # Kepala Panah (Segitiga)
    head_w = int(size * 0.25)
    head_h = int(size * 0.20)
    head_top = stem_top + stem_h
    triangle = [
        (center - head_w, head_top),       # Kiri
        (center + head_w, head_top),       # Kanan
        (center, head_top + head_h)        # Bawah (Ujung)
    ]
    draw.polygon(triangle, fill=white_color)

    # Simpan sementara
    img.save("temp_icon.png")

    # Konversi ke .icns menggunakan tools bawaan macOS (iconutil & sips)
    iconset_name = "icon.iconset"
    if os.path.exists(iconset_name):
        import shutil
        shutil.rmtree(iconset_name)
    os.makedirs(iconset_name)

    # Generate berbagai ukuran icon
    sizes = [16, 32, 64, 128, 256, 512]
    for s in sizes:
        subprocess.run(["sips", "-z", str(s), str(s), "temp_icon.png", "--out", f"{iconset_name}/icon_{s}x{s}.png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sips", "-z", str(s*2), str(s*2), "temp_icon.png", "--out", f"{iconset_name}/icon_{s}x{s}@2x.png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Pack menjadi .icns
    subprocess.run(["iconutil", "-c", "icns", iconset_name, "-o", "icon.icns"])
    
    # Bersih-bersih file sampah
    import shutil
    shutil.rmtree(iconset_name)
    os.remove("temp_icon.png")
    print("✅ icon.icns created successfully!")

if __name__ == "__main__":
    create_icon()