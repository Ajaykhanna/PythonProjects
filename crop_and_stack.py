from PIL import Image
import matplotlib.pyplot as plt

# File paths of the uploaded orbital images
files = [
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_474_converted.png",
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_475_converted.png",
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_476_converted.png",
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_477_converted.png",
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_478_converted.png",
    "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Orbitals_479_converted.png",
]


# Function to crop white background from an image
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


# Load, crop and resize images to the same size
processed_images = [crop_white_background(Image.open(f)) for f in files]

# Determine a common size (based on the smallest image)
min_width = min(img.width for img in processed_images)
min_height = min(img.height for img in processed_images)
common_size = (min_width, min_height)

# Resize all images to the common size
resized_images = [img.resize(common_size, Image.LANCZOS) for img in processed_images]

# Stack images vertically in the correct order (474 at bottom to 479 at top)
stacked_height = common_size[1] * len(resized_images)
stacked_image = Image.new("RGB", (common_size[0], stacked_height))

# Paste images in reverse order so 474 is at bottom
for idx, img in enumerate(reversed(resized_images)):
    stacked_image.paste(img, (0, idx * common_size[1]))

# Save the final stacked image
output_path = "/data/TSM/wB97xD2/solvent/charged/cube_out/S1_Stacked_Orbitals.png"
stacked_image.save(output_path)

# Show preview
plt.imshow(stacked_image)
plt.axis("off")
plt.show()
