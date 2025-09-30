from PIL import Image
import pyperclipimg
import sys
import os


def crop_white_background(img):
    """
    Crops the white background from a PIL Image.

    Parameters:
        img (PIL.Image.Image): The input image to crop.

    Returns:
        PIL.Image.Image: The cropped image with the white background removed.
    """
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    # Find bounding box of non-white pixels
    left, top, right, bottom = width, height, 0, 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if not (r > 250 and g > 250 and b > 250):  # Not white
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)

    if right < left or bottom < top:
        # No non-white pixels found, return original image
        return img

    bbox = (left, top, right + 1, bottom + 1)
    return img.crop(bbox)


def process_image_to_clipboard(image_path):
    """
    Removes the white background from an image and copies it to the clipboard.

    Parameters:
        image_path (str): Path to the image file
    """
    try:
        # Open the image
        img = Image.open(image_path)

        # Remove white background
        cropped_img = crop_white_background(img)

        # Copy to clipboard
        pyperclipimg.copy(cropped_img)

        print(f"Successfully processed and copied {image_path} to clipboard")

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")


def main():
    """
    Main function to process command line arguments and execute the program.

    Usage:
        python remove_bg_to_clipboard.py [image_path]

    If no image path is provided, it will look for the first image file in the current directory.
    """
    if len(sys.argv) > 1:
        # Use the provided image path
        image_path = sys.argv[1]
        process_image_to_clipboard(image_path)
    else:
        # Look for image files in the current directory
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        for file in os.listdir("."):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                print(f"Found image: {file}")
                process_image_to_clipboard(file)
                break
        else:
            print("No image file provided and none found in the current directory.")
            print("Usage: python remove_bg_to_clipboard.py [image_path]")


if __name__ == "__main__":
    main()
