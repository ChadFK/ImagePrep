import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ExifTags

def resize_images(input_dir: str, output_dir: str, target_size: int, strip_exif: bool, add_copyright: str, watermark: str):
    # Create output directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over files in the input directory
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)

        if os.path.isfile(file_path) and (file_path.endswith('jpg') or file_path.endswith('jpeg')):
            #try:
            # Open the image
            image = Image.open(file_path)
            if strip_exif:
                image = remove_exif(image)
            if add_copyright:
                image = add_right_holder(image, add_copyright)
            if watermark or add_copyright:
                if not watermark:
                    watermark = add_copyright
                image = apply_watermark(image, watermark)
            # Resize for 1080x1080 keeping aspect ratio
            resized_image = image.copy()
            resized_image.thumbnail((target_size, target_size))
            resized_image.save(output_path)
               
            #except IOError:
            #    print(f"Failed to resize image: {file_name}")

def apply_watermark(image, watermark_text):
    '''Applys a watermark to the image'''
    watermark = Image.new("RGBA", image.size, (1, 1, 1, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Calculate the font size to fit horizontally in the image
    font_size = 1
    font = ImageFont.truetype("arial.ttf", font_size)
    x, y, w, h = font.getbbox(watermark_text)
    while w < (image.width * 0.9) :
        #print(f'Font Size: {font_size}, Text Width: {w}, Image Width: {image.width}') #uncomment to figure out a growth rate to speed up.
        font_size += 1
        if (image.width/5)*4 > w: #grow faster if it is less than 2/3s the width.
            font_size += 10
        font = ImageFont.truetype("arial.ttf", font_size)
        x, y, w, h = font.getbbox(watermark_text)

    # Calculate the position to center the text on the watermark image
    watermark_position = (
        (image.width - w) // 2,
        (image.height - h) // 2
    )    
    
    draw.text(watermark_position, watermark_text, fill=(255, 255, 255, 50), font=font, align='center')
    watermarked_image = Image.alpha_composite(image.convert("RGBA"), watermark)
    return watermarked_image.convert('RGB')

def remove_exif(image: Image):
    ''' Strip EXIF data if requested'''
    
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    return image_without_exif
    
def add_right_holder(image: Image, copyright_holder: str):
    ''' Add copyright holder name to EXIF data if provided'''
    exif_data = image.info.get("exif", {})
    
    #for key, value in enumerate(ExifTags.TAGS.items()):
    #    if key == 39 or key == 89:
    #        print(f'{key} == {value}') 
    
    #89 is copyright
    #39 is artist
    exif_data[(315, 'Artist')] = copyright_holder
    image.info["exif"] = exif_data
    return image

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser('Usage: %prog [options]')
    parser.add_argument('--input_directory', '-i', help='Root path for image gallery.')
    parser.add_argument('--output_directory', '-o', help='Root path for resized image gallery.')
    parser.add_argument('--max_size', '-s', type=int, default=1080, help='Resize the image to max_size:max_size maximum')
    parser.add_argument('--strip_exif', '-x', type=bool, default=True, help='Removes all exif data to save file size.')
    parser.add_argument('--rights', '-r', default=None, help='Add copyright holder exif data [after remove all others if strip_exif is True].')
    parser.add_argument('--watermark', '-w', default=None, help='Adds semi-transparent watermark to the image.  If empty but rights are populated uses rights holder as watermark.')
    args = parser.parse_args()
    outdir = args.output_directory
    if args.output_directory is None:
        outdir = args.input_directory + '\\output'
    
    resize_images(args.input_directory, outdir, args.max_size, args.strip_exif, args.rights, args.watermark)