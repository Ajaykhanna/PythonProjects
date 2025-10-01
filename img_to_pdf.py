import sys
import argparse
from PIL import Image
import os

# How to Run:
# python image_to_pdf.py <image_path> [-d DPI] [-w WIDTH] [-H HEIGHT] [-q QUALITY]
# Example:
# python image_to_pdf.py sample.jpg -d 300 -w 800 -q 90
# This will convert 'sample.jpg' to 'sample.pdf' with 300 DPI, width of 800 pixels, and quality of 90.


def convert_image_to_pdf(image_path, dpi=300, width=None, height=None, quality=95):
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)

    try:
        img = Image.open(image_path)

        if width or height:
            original_width, original_height = img.size
            if width and height:
                new_size = (width, height)
            elif width:
                aspect_ratio = original_height / original_width
                new_size = (width, int(width * aspect_ratio))
            else:
                aspect_ratio = original_width / original_height
                new_size = (int(height * aspect_ratio), height)

            img = img.resize(new_size, Image.LANCZOS)
            print(
                f"Resized from {original_width}x{original_height} to {new_size[0]}x{new_size[1]}"
            )

        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != "RGB":
            img = img.convert("RGB")

        output_path = os.path.splitext(image_path)[0] + ".pdf"

        img.save(output_path, "PDF", resolution=float(dpi), quality=quality)

        file_size = os.path.getsize(output_path) / 1024
        print(f"Successfully converted '{image_path}' to '{output_path}'")
        print(f"DPI: {dpi}, Quality: {quality}, File size: {file_size:.2f} KB")

    except Exception as e:
        print(f"Error converting image: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert an image to PDF with quality control options"
    )
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument(
        "-d",
        "--dpi",
        type=int,
        default=300,
        help="DPI/resolution for the PDF (default: 300)",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        help="Target width in pixels (maintains aspect ratio if height not specified)",
    )
    parser.add_argument(
        "-H",
        "--height",
        type=int,
        help="Target height in pixels (maintains aspect ratio if width not specified)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=95,
        help="JPEG quality for PDF (1-100, default: 95)",
    )

    args = parser.parse_args()

    convert_image_to_pdf(
        args.image_path, args.dpi, args.width, args.height, args.quality
    )
