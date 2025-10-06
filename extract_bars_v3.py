"""
extract_bars.py
================

This script takes a bar chart image and isolates each stacked bar as its
own image.  The primary motivation is to work with charts like the one
provided by the user where charge‐transfer (CT) and local excitation (LE)
contributions are shown as stacked bars.  The script detects the bar
regions using their distinctive colours, crops each bar out of the
original image and writes the resulting images to disk.  If the
``pyperclipimg`` module is available, the cropped images are also
copied to the system clipboard.

Usage:

    python extract_bars.py /path/to/chart.png [output_dir]

If ``output_dir`` is not provided it defaults to the current working
directory.  The script will emit files named ``bar_1.png``,
``bar_2.png`` and so on.

Internally the script performs the following steps:

1. It loads the input image via PIL and converts it to a NumPy array.
2. It determines the two most common non‑white colours; these
   correspond to the colours of the CT and LE bars.
3. A mask is constructed that marks pixels close to either bar colour.
   A simple Euclidean distance threshold on RGB values is used to
   decide if a pixel belongs to a bar.
4. A vertical morphological closing operation is applied to merge
   segments of a bar separated by a dashed horizontal line.  This
   ensures that each bar becomes a single connected component.
5. Connected components are extracted and filtered by width/height so
   that tiny elements like the legend swatches are ignored.
6. The remaining components (bars) are sorted by their horizontal
   position and each region is saved.  The optional white‑background
   trimming function from the user's original script is provided but
   unused by default because white text inside the bars would
   otherwise be clipped away.  If you wish to trim pure white borders
   around each bar, you can call ``crop_white_background`` before
   saving.

Note: The script will attempt to import ``pyperclipimg`` to copy the
cropped images to the clipboard.  If the module is not available the
images will simply be saved to disk.
"""

import sys
import os
from typing import List, Tuple

import numpy as np
from PIL import Image

try:
    # ``pyperclipimg`` is a third‑party helper for copying PIL images
    # to the clipboard.  It may not be available in all environments.
    import pyperclipimg  # type: ignore
except Exception:
    pyperclipimg = None

try:
    import cv2  # OpenCV is used for connected component analysis
except Exception as e:
    raise RuntimeError("This script requires OpenCV (`cv2`) to be installed.") from e


def crop_white_background(img: Image.Image) -> Image.Image:
    """Crop away pure white borders from ``img``.

    The function scans every pixel and finds the minimal bounding box
    containing all pixels that are not pure white (i.e., R, G and B
    components > 250).  If no non‑white pixels are found, the original
    image is returned unmodified.

    Args:
        img: A PIL image.

    Returns:
        A new PIL image with white margins removed.
    """
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    left, top, right, bottom = width, height, 0, 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if not (r > 250 and g > 250 and b > 250):  # non‑white
                if x < left:
                    left = x
                if y < top:
                    top = y
                if x > right:
                    right = x
                if y > bottom:
                    bottom = y
    if right < left or bottom < top:
        # no non‑white pixels found
        return img
    bbox = (left, top, right + 1, bottom + 1)
    return img.crop(bbox)


def find_bar_colours(image_array: np.ndarray) -> List[np.ndarray]:
    """Determine the two dominant non‑white colours in the image.

    The bar chart uses two specific colours for the CT and LE portions
    of each bar.  To locate these colours automatically, all pixels
    that are not pure white are extracted and counted.  The two most
    frequent colours are returned in descending order of occurrence.

    Args:
        image_array: An H×W×3 RGB array.

    Returns:
        A list containing two RGB arrays representing the bar colours.
    """
    pixels = image_array.reshape(-1, 3)
    # mask out pure white pixels (>=250 on all channels)
    mask = ~(np.all(pixels >= 250, axis=1))
    coloured = pixels[mask]
    colours, counts = np.unique(coloured, axis=0, return_counts=True)
    idx = np.argsort(-counts)
    # return top two colours
    top_colours = colours[idx[:2]].astype(np.int32)
    return [top_colours[0], top_colours[1]]


def detect_bar_bounding_boxes(
    image_array: np.ndarray,
    ct_colour: np.ndarray,
    le_colour: np.ndarray,
    threshold: float = 60.0,
) -> List[Tuple[int, int, int, int]]:
    """Detect bounding boxes for each stacked bar in the chart.

    Args:
        image_array: H×W×3 RGB array of the chart.
        ct_colour: RGB array for the CT bar colour.
        le_colour: RGB array for the LE bar colour.
        threshold: Maximum Euclidean distance in RGB space for a pixel
            to be considered part of a bar.

    Returns:
        A list of bounding boxes as (x1, y1, x2, y2), sorted left to right.
    """
    diff_ct = np.linalg.norm(image_array - ct_colour, axis=2)
    diff_le = np.linalg.norm(image_array - le_colour, axis=2)
    bar_mask = (diff_ct < threshold) | (diff_le < threshold)
    bar_mask_u8 = bar_mask.astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 9))
    closed = cv2.morphologyEx(bar_mask_u8, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        closed, connectivity=8
    )
    boxes = []
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        if w > 100 and h > 100 and area > 5000:
            x1, y1, x2, y2 = x, y, x + w, y + h
            boxes.append((x1, y1, x2, y2))
    boxes.sort(key=lambda b: b[0])
    return boxes


def save_and_clip_bars(
    input_path: str,
    output_dir: str,
    trim_whitespace: bool = False,
    include_annotation: bool = False,
) -> None:
    """Extract and save each bar from the chart image.

    Args:
        input_path: Path to the input bar chart image.
        output_dir: Directory where the cropped bar images will be saved.
        trim_whitespace: Whether to call ``crop_white_background`` on
            each bar before saving.  Disabled by default because
            white numbers inside the bars would otherwise be cut away.
        include_annotation: If ``True``, the function will attempt to
            extend each bar's bounding box upwards to include text
            annotations that sit immediately above the bar.  This is
            particularly useful when annotations are drawn on top of
            the bar chart but outside the coloured bar regions.
    """
    os.makedirs(output_dir, exist_ok=True)
    img_pil = Image.open(input_path).convert("RGB")
    img_arr = np.array(img_pil)
    ct_colour, le_colour = find_bar_colours(img_arr)
    boxes = detect_bar_bounding_boxes(img_arr, ct_colour, le_colour)
    if not boxes:
        print("No bar regions detected.")
        return
    height, width = img_arr.shape[:2]
    for idx, (x1, y1, x2, y2) in enumerate(boxes, start=1):
        # Optionally extend the top of the bounding box to include annotation text
        if include_annotation:
            # start from the row above the top of the bar
            new_y1 = y1
            # maximum distance to search upwards.  Text annotations above bars
            # can be placed a significant distance above the bar top.  At the
            # same time we want to avoid including the chart title or other
            # header elements.  Limit the search to the smaller of 40% of the
            # bar height and 100 pixels.  Ensure a minimum of 30 pixels.
            max_up = int(min((y2 - y1) * 0.4, 100))
            if max_up < 30:
                max_up = 30
            # iterate upward row by row
            for offset in range(1, max_up + 1):
                row = y1 - offset
                if row < 0:
                    break
                # extract the row segment over the bar's x-range
                row_pixels = img_arr[row, x1:x2]
                # consider a pixel to be background if all channels are >245 (near white)
                # if any pixel is not background, treat this row as part of the annotation
                if np.any(
                    ~(
                        (row_pixels[:, 0] > 245)
                        & (row_pixels[:, 1] > 245)
                        & (row_pixels[:, 2] > 245)
                    )
                ):
                    new_y1 = row
                else:
                    # if we encounter background, continue searching up; but once we've
                    # already moved to a row containing annotation, we keep the lowest
                    # such row as the new top.  We do not break early to ensure we
                    # include the entire annotation bounding area.
                    pass
            # update the bounding box top
            y1 = max(0, new_y1)
        # crop the image using the (possibly adjusted) bounding box
        bar_img = img_pil.crop((x1, y1, x2, y2))
        if trim_whitespace:
            bar_img = crop_white_background(bar_img)
        out_path = os.path.join(output_dir, f"bar_{idx}.png")
        bar_img.save(out_path)
        print(f"Saved {out_path} (size: {bar_img.size})")
        if pyperclipimg is not None:
            try:
                pyperclipimg.copy(bar_img)
                print(f"Copied bar {idx} to clipboard.")
            except Exception as e:
                print(f"Failed to copy bar {idx} to clipboard: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python extract_bars.py <input_image_path> [output_dir]\n"
            "Extracts individual stacked bars from a bar chart image."
        )
        return
    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    save_and_clip_bars(input_path, output_dir, trim_whitespace=False)


if __name__ == "__main__":
    main()
