import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from src.image_batch_tool.image_converter import get_output_extension


PACKAGE_EXTENSIONS = {
    "ZIP": ".zip",
    "CBZ": ".cbz",
    "RAR": ".rar",
    "7Z": ".7z",
}


def normalize_package_format(package_format: str) -> str:
    """Validate and normalize the requested package format."""
    if not isinstance(package_format, str):
        raise ValueError("Package format must be a string.")

    normalized = package_format.strip().upper()

    if normalized not in PACKAGE_EXTENSIONS:
        supported = ", ".join(PACKAGE_EXTENSIONS)
        raise ValueError(
            f"Unsupported package format: {normalized}. "
            f"Supported formats: {supported}"
        )

    return normalized


def get_package_extension(package_format: str) -> str:
    """Return the extension for the requested package format."""
    normalized = normalize_package_format(package_format)
    return PACKAGE_EXTENSIONS[normalized]


def find_archive_executable(
    package_format: str,
    configured_path: str = ""
) -> str:
    """Find an external archive utility."""
    if configured_path:
        executable = Path(configured_path).expanduser()

        if executable.is_file():
            return str(executable.resolve())

        raise FileNotFoundError(
            f"Configured archive executable not found: {configured_path}"
        )

    if package_format == "RAR":
        candidates = [
            "rar",
            "rar.exe",
            "WinRAR",
            "WinRAR.exe",
        ]

        common_paths = [
            Path("C:/Program Files/WinRAR/rar.exe"),
            Path("C:/Program Files/WinRAR/WinRAR.exe"),
            Path("C:/Program Files (x86)/WinRAR/rar.exe"),
            Path("C:/Program Files (x86)/WinRAR/WinRAR.exe"),
        ]

    elif package_format == "7Z":
        candidates = [
            "7z",
            "7z.exe",
            "7zz",
            "7zz.exe",
        ]

        common_paths = [
            Path("C:/Program Files/7-Zip/7z.exe"),
            Path("C:/Program Files (x86)/7-Zip/7z.exe"),
        ]

    else:
        raise ValueError(
            f"No external executable is required for {package_format}."
        )

    for candidate in candidates:
        found = shutil.which(candidate)

        if found:
            return found

    for candidate in common_paths:
        if candidate.is_file():
            return str(candidate)

    software_name = "WinRAR" if package_format == "RAR" else "7-Zip"

    raise FileNotFoundError(
        f"{software_name} was not found. Install it or configure "
        f"the executable path in config.json."
    )


def run_archive_command(
    executable: str,
    arguments: list[str],
    working_directory: Path
) -> None:
    """Execute an archive utility and report any failure."""
    result = subprocess.run(
        [executable, *arguments],
        cwd=str(working_directory),
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        details = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Exit code: {result.returncode}"
        )

        raise RuntimeError(
            f"Archive utility failed: {details}"
        )


def create_zip_archive(
    image_files: list[Path],
    output_path: Path,
    extension: str
) -> None:
    """Create a ZIP-compatible archive with sequential page names."""
    with zipfile.ZipFile(
        output_path,
        mode="w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for index, image_path in enumerate(image_files, start=1):
            archive_name = f"{index:06d}{extension}"

            archive.write(
                image_path,
                arcname=archive_name,
            )


def create_external_archive(
    image_files: list[Path],
    output_path: Path,
    package_format: str,
    executable: str,
    extension: str,
) -> None:
    """Create a RAR or 7Z archive using an external utility."""
    with tempfile.TemporaryDirectory(
        prefix="manga_package_"
    ) as temporary_directory:
        staging_folder = Path(temporary_directory)

        for index, image_path in enumerate(image_files, start=1):
            staged_name = f"{index:06d}{extension}"

            shutil.copy2(
                image_path,
                staging_folder / staged_name,
            )

        if package_format == "RAR":
            arguments = [
                "a",
                "-ep",
                str(output_path),
                *sorted(
                    path.name
                    for path in staging_folder.iterdir()
                    if path.is_file()
                ),
            ]
        else:
            arguments = [
                "a",
                "-t7z",
                str(output_path),
                *sorted(
                    path.name
                    for path in staging_folder.iterdir()
                    if path.is_file()
                ),
            ]

        run_archive_command(
            executable=executable,
            arguments=arguments,
            working_directory=staging_folder,
        )

        if package_format == "RAR":
            test_arguments = ["t", str(output_path)]
        else:
            test_arguments = ["t", str(output_path)]

        run_archive_command(
            executable=executable,
            arguments=test_arguments,
            working_directory=staging_folder,
        )


def verify_package(
    package_path: Path,
    package_format: str,
    expected_page_count: int,
    executable: str = "",
) -> None:
    """Verify package integrity and its expected page count."""
    if package_format in {"ZIP", "CBZ"}:
        with zipfile.ZipFile(package_path, mode="r") as archive:
            damaged_entry = archive.testzip()

            if damaged_entry is not None:
                raise RuntimeError(
                    f"Package validation failed at: {damaged_entry}"
                )

            entries = archive.namelist()

            if len(entries) != expected_page_count:
                raise RuntimeError(
                    "Package validation failed: page count mismatch."
                )

            if len(entries) != len(set(entries)):
                raise RuntimeError(
                    "Package validation failed: duplicate entry names."
                )

            return

    if not executable:
        raise ValueError(
            "An archive executable is required to verify this format."
        )

    if package_format == "RAR":
        arguments = ["t", str(package_path)]
    elif package_format == "7Z":
        arguments = ["t", str(package_path)]
    else:
        raise ValueError(
            f"Unsupported package format: {package_format}"
        )

    run_archive_command(
        executable=executable,
        arguments=arguments,
        working_directory=package_path.parent,
    )


def create_package(
    source_folder: Path,
    output_path: Path,
    image_format: str = "JPEG",
    package_format: str = "CBZ",
    rar_executable: str = "",
    seven_zip_executable: str = "",
) -> int:
    """Create and verify an archive containing converted manga pages."""
    if not source_folder.is_dir():
        raise NotADirectoryError(
            f"Source folder not found: {source_folder}"
        )

    package_format = normalize_package_format(package_format)
    extension = get_output_extension(image_format)
    expected_package_extension = get_package_extension(package_format)

    if output_path.suffix.lower() != expected_package_extension:
        raise ValueError(
            f"Output path must use the {expected_package_extension} extension."
        )

    if output_path.exists():
        raise FileExistsError(
            f"Output package already exists: {output_path}"
        )

    image_files = sorted(
        (
            path
            for path in source_folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() == extension
        ),
        key=lambda path: str(
            path.relative_to(source_folder)
        ).casefold(),
    )

    if not image_files:
        raise ValueError(
            f"No {extension} pages found in {source_folder}. "
            "Check the output image format and conversion results."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = output_path.with_name(
        f"{output_path.stem}.tmp{output_path.suffix}"
    )

    if temporary_path.exists():
        temporary_path.unlink()

    executable = ""

    try:
        if package_format in {"ZIP", "CBZ"}:
            create_zip_archive(
                image_files=image_files,
                output_path=temporary_path,
                extension=extension,
            )
        else:
            configured_executable = (
                rar_executable
                if package_format == "RAR"
                else seven_zip_executable
            )

            executable = find_archive_executable(
                package_format=package_format,
                configured_path=configured_executable,
            )

            create_external_archive(
                image_files=image_files,
                output_path=temporary_path,
                package_format=package_format,
                executable=executable,
                extension=extension,
            )

        verify_package(
            package_path=temporary_path,
            package_format=package_format,
            expected_page_count=len(image_files),
            executable=executable,
        )

        if output_path.exists():
            raise FileExistsError(
                f"Output package already exists: {output_path}"
            )

        temporary_path.replace(output_path)

        print(
            f"[PACKAGED] {output_path} "
            f"({len(image_files)} pages, {package_format})"
        )

        return len(image_files)

    except Exception:
        if temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                pass

        raise
