# Developer: Ajay Khanna
# Places: LANL
# Date: May.12.2025

"""
Streamlit GUI application for converting multiple image files between various formats.

Features:
- Supports multiple input formats including PNG, JPG, TGA, BMP, GIF, WEBP.
- Optionally supports SVG input if the 'CairoSVG' library and its dependencies are installed.
- Allows selecting output format (PNG, JPEG, WEBP, BMP, GIF, TGA), default is PNG.
  (Note: SVG output is not supported).
- Multi-file drag-and-drop upload.
- Optional resizing (to specific pixel dimensions) or rescaling (by percentage).
- Choice of resampling filters for resizing/rescaling (applies to raster images).
- Options configured in the sidebar.
- Handles errors gracefully during processing.
- Packages converted images into a downloadable ZIP archive.
- Provides a direct download button if only one image is converted successfully.

Requires: streamlit, Pillow
Optional for SVG support: CairoSVG
Installation: pip install streamlit Pillow CairoSVG
Note: CairoSVG may require system dependencies (Cairo graphics library). If not found,
      SVG support will be disabled, and a message will be printed to the console.
"""

import streamlit as st
from PIL import Image, UnidentifiedImageError
import os
import io
import zipfile
import time  # To provide progress feedback
import sys  # To check for modules

# --- Try importing CairoSVG and set a flag ---
cairosvg_available = False
try:
    import cairosvg

    # Perform a minimal check to see if the underlying library is likely present
    # This tries to render a tiny dummy SVG to PNG bytes
    dummy_svg = '<svg height="1" width="1"></svg>'
    cairosvg.svg2png(bytestring=dummy_svg.encode("utf-8"))
    cairosvg_available = True
    print(
        "CairoSVG library found. SVG input support enabled."
    )  # Optional console message
except ImportError:
    print(
        "INFO: 'CairoSVG' library not found. SVG input support will be disabled.",
        file=sys.stdout,
    )
    print(
        "      To enable SVG support, install it: pip install CairoSVG", file=sys.stdout
    )
    print(
        "      You may also need system dependencies (e.g., libcairo2-dev on Debian/Ubuntu, brew install cairo on macOS).",
        file=sys.stdout,
    )
except Exception as e:
    # Catch other potential issues during the check (e.g., missing system libs)
    print(
        f"WARNING: CairoSVG imported but failed runtime check. SVG input support disabled. Error: {e}",
        file=sys.stdout,
    )
    cairosvg_available = False  # Ensure it's False if the check fails

# --- Configuration ---
# Define supported formats based on library availability
SUPPORTED_RASTER_INPUT_FORMATS = ["png", "jpg", "jpeg", "tga", "bmp", "gif", "webp"]
SUPPORTED_INPUT_FORMATS = (
    SUPPORTED_RASTER_INPUT_FORMATS + ["svg"]
    if cairosvg_available
    else SUPPORTED_RASTER_INPUT_FORMATS
)
# SVG is NOT included as an output format
SUPPORTED_OUTPUT_FORMATS = ["PNG", "JPEG", "WEBP", "BMP", "GIF", "TGA"]
DEFAULT_OUTPUT_FORMAT = "PNG"

# Define resampling filters available in Pillow
RESIZE_METHODS = {
    "LANCZOS (High Quality)": Image.Resampling.LANCZOS,
    "BICUBIC": Image.Resampling.BICUBIC,
    "BILINEAR": Image.Resampling.BILINEAR,
    "NEAREST (Fastest)": Image.Resampling.NEAREST,
}

# MIME types for single file download
MIME_TYPES = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "tga": "image/x-tga",  # Common MIME type for TGA
}


# --- Helper Functions ---


def create_zip_archive(image_data_list):
    """
    Creates a ZIP archive in memory containing processed images.

    Args:
        image_data_list (list): A list of tuples, where each tuple contains
                                (filename (str), image_bytes (bytes)).

    Returns:
        io.BytesIO: A BytesIO object containing the ZIP archive data.
                    Returns None if the input list is empty or an error occurs.
    """
    if not image_data_list:
        return None

    zip_buffer = io.BytesIO()
    try:
        # Use 'w' mode to create a new zip file in the buffer, ZIP_DEFLATED for compression
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
            for filename, img_bytes in image_data_list:
                # Add each image file to the zip archive with its new name
                zip_file.writestr(filename, img_bytes)
    except Exception as e:
        st.error(f"Error creating ZIP file: {e}")
        return None
    # The buffer is ready to be read after closing the ZipFile context
    return zip_buffer


def generate_new_filename(original_filename, target_format):
    """
    Generates a new filename for the converted image, preserving the base name.

    Args:
        original_filename (str): The original name of the uploaded file.
        target_format (str): The desired output format (e.g., 'png', 'jpeg').

    Returns:
        str: The new filename with the updated extension.
    """
    base_name, _ = os.path.splitext(original_filename)
    # Ensure the target format is lowercase for the extension
    return f"{base_name}_converted.{target_format.lower()}"


# --- Streamlit App Layout ---

# Configure the page layout
st.set_page_config(layout="wide", page_title="Image Converter")

# Main title of the application - adjust based on SVG support
app_title = "🖼️ Multi-Format Image Converter"
if cairosvg_available:
    app_title += " (with SVG Input)"
st.title(app_title)

# Introductory text explaining the app's purpose and usage
st.markdown(
    f"""
Upload one or more images (including **TGA** files{' and **SVG**' if cairosvg_available else ''}).
Configure your desired conversion options in the sidebar on the left.
Supported input formats: **{", ".join(SUPPORTED_INPUT_FORMATS).upper()}**.
Supported output formats: **{", ".join(SUPPORTED_OUTPUT_FORMATS)}**.
Click 'Convert Images' to process and download the results.
"""
)
if not cairosvg_available:
    st.warning(
        "SVG input support is disabled because the 'CairoSVG' library or its dependencies were not found.",
        icon="⚠️",
    )
st.markdown("---")  # Visual separator

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Conversion Options")

    # 1. Output Format Selection
    output_format = st.selectbox(
        "Select Output Format:",
        options=SUPPORTED_OUTPUT_FORMATS,  # SVG removed from output
        index=SUPPORTED_OUTPUT_FORMATS.index(DEFAULT_OUTPUT_FORMAT),  # Default to PNG
        help="Choose the file format for the converted images (SVG output not supported).",
    )
    # Store lowercase version for consistent filename generation
    output_format_lower = output_format.lower()

    # Separator for visual grouping
    st.markdown("---")

    # 2. Resizing / Rescaling Options
    st.subheader("Resizing & Rescaling")
    resize_help_text = "Check this box to enable image dimension changes."
    if cairosvg_available:
        resize_help_text += " For SVG input, this sets the rendering size."
    enable_resize = st.checkbox(
        "Enable Resizing/Rescaling", value=False, help=resize_help_text
    )

    # Conditional options - only show if the checkbox is ticked
    resize_mode = None
    target_width = None
    target_height = None
    scale_percent = 100
    # Default resampling method key (Only applies to non-SVG inputs)
    resample_method_key = "LANCZOS (High Quality)"

    if enable_resize:
        resize_mode = st.radio(
            "Select Mode:",
            ("Resize (Pixels)", "Rescale (Percent)"),
            key="resize_mode_radio",  # Unique key helps maintain state
            help="Choose whether to set exact dimensions or scale by a percentage.",
        )

        # Resampling method selection - Note its limited applicability for SVG
        resample_method_help = (
            "Algorithm used for resizing raster images (PNG, JPG, etc.)."
        )
        if cairosvg_available:
            resample_method_help += " Not directly used for SVG rendering size."
        resample_method_key = st.selectbox(
            "Resampling Method (Raster only):",
            options=list(RESIZE_METHODS.keys()),
            index=0,  # Default to LANCZOS
            help=resample_method_help,
        )

        if resize_mode == "Resize (Pixels)":
            # Use columns for a more compact layout
            col1, col2 = st.columns(2)
            with col1:
                target_width = st.number_input(
                    "Target Width (px):",
                    min_value=1,
                    value=800,  # Sensible default
                    step=1,
                    key="target_width_input",
                )
            with col2:
                target_height = st.number_input(
                    "Target Height (px):",
                    min_value=1,
                    value=600,  # Sensible default
                    step=1,
                    key="target_height_input",
                )
        elif resize_mode == "Rescale (Percent)":
            scale_help = "Adjust the image size relative to its original dimensions (for raster)."
            if cairosvg_available:
                scale_help += " Sets render scale (for SVG)."
            scale_percent = st.slider(
                "Scale Percentage:",
                min_value=1,
                max_value=500,  # Allow upscaling up to 5x
                value=100,  # Default is no change
                step=1,
                format="%d%%",  # Display as percentage
                key="scale_percent_slider",
                help=scale_help,
            )

    # Add developer information at the bottom of the sidebar
    st.markdown("---")
    st.markdown(
        f"""
    *Developer: Ajay Khanna*
    *Place: LANL*
    *Date: May 12, 2025*
    """
    )
    st.markdown("---")
    # Update caption about requirements
    req_caption = "Requires: `streamlit`, `Pillow`"
    if cairosvg_available:
        req_caption += ", `CairoSVG` (+ system dependencies)"
    else:
        req_caption += " (Optional: `CairoSVG` for SVG support)"
    st.caption(req_caption)


# --- Main Area - File Upload and Processing ---

# File uploader uses the dynamically set SUPPORTED_INPUT_FORMATS
uploader_label = f"Upload Image Files ({', '.join(SUPPORTED_INPUT_FORMATS).upper()})"
uploader_help = "You can drag and drop multiple files here."
if cairosvg_available:
    uploader_help += " (including SVG)"

uploaded_files = st.file_uploader(
    uploader_label,
    type=SUPPORTED_INPUT_FORMATS,
    accept_multiple_files=True,
    help=uploader_help,
)

# Only proceed if files have been uploaded
if uploaded_files:
    st.info(
        f"✅ {len(uploaded_files)} file(s) selected. Review options in the sidebar and click 'Convert'."
    )

    # Button to trigger the conversion process
    if st.button("🚀 Convert Images"):
        start_time = time.time()  # Track processing time
        processed_images = []  # List to store results: (filename, bytes)
        error_messages = []  # List to store error details
        success_count = 0
        total_count = len(uploaded_files)

        # Placeholders for dynamic updates during processing
        progress_bar = st.progress(0)
        status_text = st.empty()  # To show which file is being processed

        # Loop through each uploaded file
        for i, uploaded_file in enumerate(uploaded_files):
            current_file_info = (
                f"Processing '{uploaded_file.name}' ({i+1}/{total_count})..."
            )
            status_text.text(current_file_info)
            progress_bar.progress((i + 1) / total_count)  # Update progress bar

            img = None  # Pillow Image object
            img_bytes = None  # Raw bytes for final output
            skip_pillow_save = False  # Flag to optimize SVG->PNG conversion

            try:
                # Get file extension
                _, file_extension = os.path.splitext(uploaded_file.name.lower())

                # --- Handle SVG Input (only if library is available) ---
                if file_extension == ".svg":
                    if not cairosvg_available:
                        # Skip SVG if library is not available
                        raise ValueError(
                            "SVG processing skipped: CairoSVG library not available."
                        )

                    # Proceed with SVG processing
                    svg_bytes = uploaded_file.getvalue()
                    if not svg_bytes:
                        raise ValueError("SVG file appears to be empty.")

                    render_width = None
                    render_height = None
                    scale_factor = 1.0  # Default scale

                    # Determine render size if resizing/rescaling is enabled
                    if enable_resize:
                        if resize_mode == "Resize (Pixels)":
                            if (
                                not target_width
                                or not target_height
                                or target_width < 1
                                or target_height < 1
                            ):
                                raise ValueError(
                                    "Invalid target width or height provided for SVG rendering."
                                )
                            render_width = target_width
                            render_height = target_height
                        elif resize_mode == "Rescale (Percent)":
                            if scale_percent <= 0:
                                raise ValueError("Scale percentage must be positive.")
                            scale_factor = scale_percent / 100.0
                            render_width = None  # Don't set fixed width/height if scaling by factor
                            render_height = None

                    # Convert SVG to the target format using CairoSVG
                    # Optimization: If target is PNG, directly use cairosvg.svg2png
                    if output_format_lower == "png":
                        png_bytes_io = io.BytesIO()
                        cairosvg.svg2png(
                            bytestring=svg_bytes,
                            write_to=png_bytes_io,
                            output_width=render_width,
                            output_height=render_height,
                            scale=scale_factor if render_width is None else 1.0,
                        )  # Pass scale only if fixed size isn't set
                        img_bytes = png_bytes_io.getvalue()
                        skip_pillow_save = True  # We already have the final PNG bytes
                    else:
                        # For other formats (JPEG, WEBP, etc.), first convert SVG to PNG bytes
                        png_bytes_io = io.BytesIO()
                        cairosvg.svg2png(
                            bytestring=svg_bytes,
                            write_to=png_bytes_io,
                            output_width=render_width,
                            output_height=render_height,
                            scale=scale_factor if render_width is None else 1.0,
                        )
                        png_bytes_io.seek(0)
                        # Then load the PNG bytes into Pillow to handle final conversion
                        img = Image.open(png_bytes_io)
                        if img is None:
                            raise ValueError(
                                "Failed to load intermediate PNG from SVG."
                            )

                # --- Handle Raster Input (using Pillow) ---
                else:
                    img = Image.open(uploaded_file)
                    # --- Apply Resizing/Rescaling (Pillow) ---
                    if enable_resize:
                        current_width, current_height = img.size
                        resample_filter = RESIZE_METHODS[resample_method_key]
                        new_width, new_height = current_width, current_height

                        if resize_mode == "Resize (Pixels)":
                            if (
                                not target_width
                                or not target_height
                                or target_width < 1
                                or target_height < 1
                            ):
                                raise ValueError(
                                    "Invalid target width or height provided for resizing."
                                )
                            new_width, new_height = target_width, target_height
                        elif resize_mode == "Rescale (Percent)":
                            if scale_percent <= 0:
                                raise ValueError("Scale percentage must be positive.")
                            scale_factor = scale_percent / 100.0
                            new_width = max(1, int(current_width * scale_factor))
                            new_height = max(1, int(current_height * scale_factor))

                        if (new_width, new_height) != (current_width, current_height):
                            try:
                                img = img.resize(
                                    (new_width, new_height), resample_filter
                                )
                            except Exception as resize_err:
                                raise ValueError(f"Failed to resize: {resize_err}")

                # --- Final Conversion and Saving (Pillow, if needed) ---
                if not skip_pillow_save:
                    if img is None:
                        raise ValueError("Image object is missing before final save.")

                    # Handle output format specifics (e.g., transparency for JPEG)
                    if output_format_lower in ["jpeg", "jpg"]:
                        if img.mode == "RGBA" or img.mode == "P":
                            st.warning(
                                f"'{uploaded_file.name}' has transparency; converting to RGB for JPEG output.",
                                icon="⚠️",
                            )
                            img = img.convert("RGB")

                    # Save processed image (from Pillow) to memory buffer
                    img_byte_arr = io.BytesIO()
                    try:
                        img.save(img_byte_arr, format=output_format.upper())
                    except KeyError:
                        raise ValueError(
                            f"Selected output format '{output_format.upper()}' is not supported by Pillow."
                        )
                    except Exception as save_err:
                        raise ValueError(
                            f"Failed to save image as {output_format.upper()}: {save_err}"
                        )
                    img_bytes = img_byte_arr.getvalue()

                # --- Prepare for ZIP ---
                if img_bytes:
                    new_filename = generate_new_filename(
                        uploaded_file.name, output_format_lower
                    )
                    processed_images.append((new_filename, img_bytes))
                    success_count += 1
                else:
                    raise ValueError("Failed to generate final image bytes.")

            except UnidentifiedImageError:
                error_msg = f"❌ Error: '{uploaded_file.name}' is not a valid or supported image file (excluding SVG issues), or it might be corrupted."
                error_messages.append(error_msg)
                st.error(error_msg, icon="❗")
            # Removed specific ImportError/FileNotFoundError for CairoSVG here, handled by initial check
            except ValueError as ve:
                error_msg = f"❌ Error processing '{uploaded_file.name}': {ve}"
                error_messages.append(error_msg)
                # Display specific errors like skipped SVG slightly differently
                if "SVG processing skipped" in str(ve):
                    st.warning(
                        f"Skipped '{uploaded_file.name}': SVG support disabled.",
                        icon="ℹ️",
                    )
                else:
                    st.error(error_msg, icon="❗")
            except Exception as e:
                # Catch any other unexpected errors
                error_msg = f"❌ An unexpected error occurred with '{uploaded_file.name}': {type(e).__name__} - {e}"
                error_messages.append(error_msg)
                st.error(error_msg, icon="❗")
            finally:
                # Close Pillow image object if it was opened
                if img:
                    try:
                        img.close()
                    except Exception:
                        pass  # Ignore errors during close

        # --- Processing Finished - Display Summary and Download ---
        end_time = time.time()
        processing_time = end_time - start_time
        status_text.text(f"Processing complete in {processing_time:.2f} seconds.")

        st.markdown("---")  # Separator
        st.subheader("📊 Conversion Summary")

        # Display success and error counts
        if success_count > 0:
            st.success(
                f"Successfully converted {success_count} out of {total_count} image(s)."
            )
        if error_messages:
            st.warning(
                f"Encountered errors or skipped files for {len(error_messages)} item(s). See messages above/below."
            )
            # Optionally provide a way to see all errors consolidated:
            with st.expander("Show Error/Skipped File Details"):
                for msg in error_messages:
                    # Distinguish between errors and skipped files visually
                    if "skipped" in msg.lower():
                        st.info(msg)
                    else:
                        st.error(msg)

        # --- Download Buttons ---
        if processed_images:
            # --- Add single file download button if exactly one file was converted ---
            if success_count == 1:
                single_filename, single_file_bytes = processed_images[0]
                single_file_ext = (
                    output_format_lower  # Already stored from sidebar selection
                )
                mime_type = MIME_TYPES.get(
                    single_file_ext, "application/octet-stream"
                )  # Default MIME type

                st.download_button(
                    label=f"📥 Download Converted File ({single_filename})",
                    data=single_file_bytes,
                    file_name=single_filename,
                    mime=mime_type,
                    key="download_single_button",
                )
                st.markdown(
                    "*(Or download as a ZIP archive below)*"
                )  # Clarify ZIP option still exists

            # --- Always offer the ZIP download button if any files were converted ---
            zip_buffer = create_zip_archive(processed_images)
            if zip_buffer:
                zip_label = f"📥 Download All {success_count} Converted Image(s) (ZIP)"
                st.download_button(
                    label=zip_label,
                    data=zip_buffer.getvalue(),  # Pass the bytes of the zip file
                    file_name=f"converted_images_{output_format_lower}.zip",  # Dynamic filename
                    mime="application/zip",  # Standard MIME type for ZIP files
                    key="download_zip_button",  # Changed key slightly
                )
            else:
                # This message appears if the create_zip_archive function failed
                st.error("Could not create the ZIP archive due to an internal error.")

        elif total_count > 0:
            # Message if files were uploaded but none could be processed
            st.warning("No images were successfully processed to download.")

else:
    # Initial message when no files are uploaded yet
    st.info("☝️ Upload image files using the uploader above to get started.")

# --- End of Streamlit Script ---
