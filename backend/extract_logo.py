from PIL import Image
import os

try:
    img_path = r"c:\Users\NuzhatKhan\Downloads\paySlip generator\Images\WhatsApp Image 2026-03-07 at 8.19.10 PM.jpeg" # The first image
    if not os.path.exists(img_path):
        print(f"Error: image not found at {img_path}")
    else:
        img = Image.open(img_path)
        # Approximate crop coordinates for the logo. The user provided standard WhatsApp JPEGs.
        # We might need to guess or do it interactively. For now let's just do a rough crop and see.
        # However, a better way is to see if I can just use CSS and an img tag for them to put the logo, or I can generate a 
        # base64 crop. I'll write a script to crop the top left corner.
        
        # WhatsApp images are usually around 1000-1200px wide. 
        # Top left corner contains the logo.
        # x, y, x_end, y_end (let's say 0,0 to 300, 300)
        width, height = img.size
        print(f"Image size: {width}x{height}")
        
        # Let's crop a bit and save it to public folder
        crop_box = (20, 20, 300, 300)
        logo = img.crop(crop_box)
        
        out_path = r"c:\Users\NuzhatKhan\Downloads\paySlip generator\frontend\public\logo.png"
        logo.save(out_path)
        print("Cropped logo saved to public/logo.png")
except Exception as e:
    import traceback
    traceback.print_exc()
