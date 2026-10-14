from pathlib import Path

from PIL import Image, ImageOps


FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "JPG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "TIF": ".tiff",
}

SUPPORTED_EXTENSIONS = {
    extension.lower()
    for extension in Image.registered_extensions()
}


def normalize_format(image_format: str) -> str:
    """Validate and normalize the requested output format."""
    if not isinstance(image_format, str):
        raise ValueError("Image format must be a string.")

    normalized = image_format.strip().upper()

    if normalized not in FORMAT_EXTENSIONS:
        supported = ", ".join(
            sorted({"JPEG", "PNG", "WEBP", "BMP", "TIFF"})
        )
        raise ValueError(
            f"Unsupported image format: {normalized}. "
            f"Supported formats: {supported}"
        )

    if normalized == "JPG":
        return "JPEG"

    if normalized == "TIF":
        return "TIFF"

    return normalized


def get_output_extension(image_format: str) -> str:
    """Return the canonical extension for an image format."""
    normalized = normalize_format(image_format)
    return FORMAT_EXTENSIONS[normalized]


def get_unique_output_path(
    source_path: Path,
    image_format: str,
) -> Path:
    """Generate a destination path without overwriting existing files."""
    extension = get_output_extension(image_format)

    output_path = source_path.with_name(
        f"{source_path.stem}_converted{extension}"
    )

    counter = 2

    while output_path.exists():
        output_path = source_path.with_name(
            f"{source_path.stem}_converted_{counter}{extension}"
        )
        counter += 1

    return output_path


def prepare_image(
    image: Image.Image,
    image_format: str,
) -> Image.Image:
    """Prepare image mode and transparency for the output format."""
    has_transparency = (
        image.mode in {"RGBA", "LA"}
        or (
            image.mode == "P"
            and "transparency" in image.info
        )
    )

    if has_transparency:
        image = image.convert("RGBA")

        if image_format in {"JPEG", "BMP"}:
            background = Image.new(
                "RGB",
                image.size,
                (255, 255, 255),
            )
            background.paste(
                image,
                mask=image.getchannel("A"),
            )
            return background

        return image

    if image_format in {"JPEG", "BMP"}:
        return image.convert("RGB")

    if image.mode not in {"RGB", "RGBA", "L", "LA"}:
        return image.convert("RGB")

    return image


def convert_image(
    source_path: Path,
    output_format: str = "JPEG",
    quality: int = 92,
) -> Path:
    """Convert a single image and return the generated file path."""
    output_format = normalize_format(output_format)

    if (
        not isinstance(quality, int)
        or isinstance(quality, bool)
        or not 1 <= quality <= 100
    ):
        raise ValueError(
            "Image quality must be an integer between 1 and 100."
        )

    output_path = get_unique_output_path(
        source_path,
        output_format,
    )

    try:
        with Image.open(source_path) as source_image:
            # Use the first frame of animated images.
            source_image.seek(0)

            image = ImageOps.exif_transpose(source_image)
            image = image.copy()

        image = prepare_image(image, output_format)

        save_options = {}

        if output_format == "JPEG":
            save_options = {
                "quality": quality,
                "optimize": True,
            }
        elif output_format == "WEBP":
            save_options = {
                "quality": quality,
                "method": 4,
            }
        elif output_format == "PNG":
            save_options = {
                "optimize": True,
            }

        image.save(
            output_path,
            format=output_format,
            **save_options,
        )

        return output_path

    except Exception as exc:
        if output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                pass

        raise RuntimeError(
            f"Failed to convert image: {source_path}"
        ) from exc


def convert_images_in_folder(
    folder: Path,
    output_format: str = "JPEG",
    quality: int = 92,
) -> list[Path]:
    """
    Convert supported images recursively.

    Preserve images already using the target extension.
    Return original paths successfully converted.
    """
    if not folder.is_dir():
        raise NotADirectoryError(
            f"Folder not found: {folder}"
        )

    output_format = normalize_format(output_format)

    if (
        not isinstance(quality, int)
        or isinstance(quality, bool)
        or not 1 <= quality <= 100
    ):
        raise ValueError(
            "Image quality must be an integer between 1 and 100."
        )

    target_extension = get_output_extension(output_format)

    image_files = sorted(
        (
            path
            for path in folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
            and path.suffix.lower() != target_extension
        ),
        key=lambda path: str(
            path.relative_to(folder)
        ).casefold(),
    )

    originals_to_delete = []

    for source_path in image_files:
        try:
            output_path = convert_image(
                source_path=source_path,
                output_format=output_format,
                quality=quality,
            )

            originals_to_delete.append(source_path)

            print(
                f"[CONVERTED] {source_path} -> {output_path}"
            )

        except Exception as exc:
            raise RuntimeError(
                f"Conversion failed for {source_path}"
            ) from exc

    print(
        f"[INFO] Converted {len(originals_to_delete)} images "
        f"to {output_format}."
    )

    return originals_to_delete
