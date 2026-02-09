import os
import urllib.request
import ssl

def download_font():
    # Using fonts.google.com API to get the font
    # Alternative: Try fontsquirrel or other CDN
    url = "https://fonts.gstatic.com/s/montserrat/v26/JTUSjIg1_i6t8kCHKm459WlhyyTh89Y.woff2"
    # Actually, let's use a direct TTF from a reliable CDN
    url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"
    output_dir = "assets/fonts"
    output_path = os.path.join(output_dir, "Montserrat-Bold.ttf")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Downloading {url} to {output_path}...")
    
    try:
        # Create unverified context to avoid SSL errors on some systems
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response, open(output_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            print(f"Downloaded {len(data)} bytes successfully.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    download_font()
