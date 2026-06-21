"""
Génère favicon.ico depuis favicon.svg
Nécessite : pip install cairosvg Pillow
Usage : python pipeline/generate_favicon.py
"""
import os

PUBLIC = os.path.join(os.path.dirname(__file__), '..', 'public')
SVG_PATH = os.path.join(PUBLIC, 'favicon.svg')
ICO_PATH = os.path.join(PUBLIC, 'favicon.ico')
PNG_PATH = os.path.join(PUBLIC, 'apple-touch-icon.png')

def main():
    try:
        import cairosvg
        from PIL import Image
        import io

        print("Génération favicon.ico depuis favicon.svg...")

        # Générer PNG 256×256
        png_data = cairosvg.svg2png(url=SVG_PATH, output_width=256, output_height=256)

        # Générer apple-touch-icon 180×180
        png_180 = cairosvg.svg2png(url=SVG_PATH, output_width=180, output_height=180)
        with open(PNG_PATH, 'wb') as f:
            f.write(png_180)
        print(f"✅ apple-touch-icon.png créé ({PNG_PATH})")

        # Créer ico multi-taille (16, 32, 48, 256)
        img = Image.open(io.BytesIO(png_data)).convert('RGBA')
        sizes = [(16,16), (32,32), (48,48), (256,256)]
        imgs = [img.resize(s, Image.LANCZOS) for s in sizes]
        imgs[0].save(ICO_PATH, format='ICO', sizes=sizes, append_images=imgs[1:])
        print(f"✅ favicon.ico créé ({ICO_PATH})")

    except ImportError:
        print("⚠  cairosvg ou Pillow manquant.")
        print("   Installez : pip install cairosvg Pillow")
        print("   OU utilisez https://realfavicongenerator.net en uploadant public/favicon.svg")

if __name__ == '__main__':
    main()
