import json
import shutil
from pathlib import Path

from src.image_batch_tool.image_converter import (
    normalize_format,
    convert_images_in_folder,
)
from src.image_batch_tool.package_creator import (
    create_package,
    get_package_extension,
    normalize_package_format,
)


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config() -> tuple[dict, Path]:
    """Load and validate application configuration."""
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    parent_value = config.get("parent_folder")

    if not isinstance(parent_value, str) or not parent_value.strip():
        raise ValueError(
            "Set a valid parent_folder in config.json."
        )

    parent_folder = Path(parent_value).expanduser().resolve()

    if not parent_folder.is_dir():
        raise NotADirectoryError(
            f"Parent folder does not exist: {parent_folder}"
        )

    output_format = normalize_format(
        config.get("output_image_format", "JPEG")
    )

    package_format = normalize_package_format(
        config.get("package_format", "CBZ")
    )

    quality = config.get("output_image_quality", 92)

    if (
        not isinstance(quality, int)
        or isinstance(quality, bool)
        or not 1 <= quality <= 100
    ):
        raise ValueError(
            "output_image_quality must be an integer between 1 and 100."
        )

    output_in_parent = config.get("cbz_output_in_parent", True)
    delete_originals = config.get(
        "delete_original_after_success", False
    )

    if not isinstance(output_in_parent, bool):
        raise ValueError(
            "cbz_output_in_parent must be true or false."
        )

    if not isinstance(delete_originals, bool):
        raise ValueError(
            "delete_original_after_success must be true or false."
        )

    for key in ("rar_executable", "seven_zip_executable"):
        value = config.get(key, "")

        if not isinstance(value, str):
            raise ValueError(
                f"{key} must be a string."
            )

    config["output_image_format"] = output_format
    config["package_format"] = package_format

    return config, parent_folder


def get_output_folder(
    config: dict,
    parent_folder: Path
) -> Path:
    """Resolve the configured package output directory."""
    if config.get("cbz_output_in_parent", True):
        return parent_folder

    output_value = config.get("output_folder")

    if not isinstance(output_value, str) or not output_value.strip():
        raise ValueError(
            "Set output_folder when cbz_output_in_parent is false."
        )

    return Path(output_value).expanduser().resolve()


def validate_paths(
    parent_folder: Path,
    output_folder: Path
) -> None:
    """Prevent the output directory from being nested inside the source root."""
    if output_folder == parent_folder:
        return

    if parent_folder in output_folder.parents:
        raise ValueError(
            "output_folder must not be inside parent_folder. "
            "Choose a separate destination directory."
        )


def process_folder(
    folder: Path,
    output_path: Path,
    output_format: str,
    quality: int,
    package_format: str,
    rar_executable: str,
    seven_zip_executable: str,
    delete_originals: bool,
) -> None:
    """Convert images, create a verified package, and optionally clean up."""
    if output_path.exists():
        print(f"[SKIPPED] Package already exists: {output_path}")
        return

    print(f"\n[PROCESSING] {folder.name}")
    print(f"[IMAGE FORMAT] {output_format}")
    print(f"[PACKAGE FORMAT] {package_format}")

    convert_images_in_folder(
        folder=folder,
        output_format=output_format,
        quality=quality,
    )

    page_count = create_package(
        source_folder=folder,
        output_path=output_path,
        image_format=output_format,
        package_format=package_format,
        rar_executable=rar_executable,
        seven_zip_executable=seven_zip_executable,
    )

    print(f"[VERIFIED] {page_count} pages: {output_path}")

    if delete_originals:
        try:
            shutil.rmtree(folder)
            print(f"[DELETED] Source folder: {folder}")
        except OSError as exc:
            print(
                "[WARNING] The package was created successfully, "
                f"but the source folder could not be deleted: {exc}"
            )

    print(f"[SUCCESS] {folder.name}")


def main() -> None:
    """Run the batch conversion and packaging process."""
    try:
        config, parent_folder = load_config()

        output_folder = get_output_folder(
            config,
            parent_folder,
        )

        validate_paths(
            parent_folder,
            output_folder,
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"[CONFIGURATION ERROR] {exc}")
        return

    output_format = config["output_image_format"]
    package_format = config["package_format"]
    package_extension = get_package_extension(package_format)
    quality = config.get("output_image_quality", 92)
    delete_originals = config.get(
        "delete_original_after_success", False
    )
    rar_executable = config.get("rar_executable", "")
    seven_zip_executable = config.get("seven_zip_executable", "")

    folders = sorted(
        (
            path
            for path in parent_folder.iterdir()
            if path.is_dir()
            and path.resolve() != output_folder.resolve()
        ),
        key=lambda path: path.name.casefold(),
    )

    if not folders:
        print("[INFO] No manga folders found.")
        return

    print(f"[SOURCE] {parent_folder}")
    print(f"[OUTPUT] {output_folder}")
    print(f"[IMAGE FORMAT] {output_format}")
    print(f"[IMAGE QUALITY] {quality}")
    print(f"[PACKAGE FORMAT] {package_format}")
    print(f"[DELETE SOURCE] {delete_originals}")

    for folder in folders:
        output_path = output_folder / (
            f"{folder.name}{package_extension}"
        )

        try:
            process_folder(
                folder=folder,
                output_path=output_path,
                output_format=output_format,
                quality=quality,
                package_format=package_format,
                rar_executable=rar_executable,
                seven_zip_executable=seven_zip_executable,
                delete_originals=delete_originals,
            )
        except Exception as exc:
            print(f"[ERROR] {folder.name}: {exc}")
            print(
                "[INFO] The source folder was not deleted "
                "by the processing routine."
            )

    print("\n[DONE] Batch processing finished.")


if __name__ == "__main__":
    main()
