# Manga Image Converter and Package Creator

A lightweight Python utility for converting manga page images and packaging each manga subfolder into a selected archive format.

## Features

- Process every immediate subfolder inside a configured source directory.
- Convert supported images to JPEG, PNG, WEBP, BMP, or TIFF.
- Create ZIP, CBZ, RAR, or 7Z packages.
- Assign sequential page names inside each package.
- Verify package integrity before publishing the final output.
- Optionally delete a source manga folder after successful package creation and verification.
- Configure source paths, output paths, image format, image quality, and package format in `config.json`.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or later
- Pillow
- WinRAR or a RAR command-line executable for RAR output
- 7-Zip for 7Z output

ZIP and CBZ creation use Python's standard library and do not require external archive software.

## Project Structure

```text
MangaCBZ/
├── main.py
├── config.json
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    └── manga_cbz/
        ├── __init__.py
        ├── image_converter.py
        └── package_creator.py
```

## Installation

Open Command Prompt in the project directory.

Install the dependencies:

```bat
py -m pip install -r requirements.txt
```

If the `py` command is unavailable, try:

```bat
python -m pip install -r requirements.txt
```

If neither command works, install Python from the official Python website and enable the option to add Python to PATH during installation.

## Configuration

Edit `config.json` before running the program.

| Setting | Description |
|---|---|
| `parent_folder` | Root folder containing manga subfolders |
| `cbz_output_in_parent` | `true` saves packages in the source root; `false` uses `output_folder` |
| `output_folder` | Separate destination directory for packages |
| `output_image_format` | Converted image format |
| `output_image_quality` | Quality from 1 to 100 for JPEG and WEBP |
| `package_format` | Package type: `ZIP`, `CBZ`, `RAR`, or `7Z` |
| `delete_original_after_success` | Deletes the complete source manga folder after successful packaging and verification |
| `rar_executable` | Optional full path to `rar.exe` or `WinRAR.exe` |
| `seven_zip_executable` | Optional full path to `7z.exe` or `7zz.exe` |

Example:

```json
{
  "parent_folder": "D:\\Manga",
  "cbz_output_in_parent": false,
  "output_folder": "D:\\Manga_Packages",
  "output_image_format": "WEBP",
  "output_image_quality": 92,
  "package_format": "CBZ",
  "delete_original_after_success": false,
  "rar_executable": "",
  "seven_zip_executable": ""
}
```

### Package Formats

- `ZIP`: Creates standard `.zip` files.
- `CBZ`: Creates ZIP-compatible `.cbz` files commonly used by comic readers.
- `RAR`: Requires WinRAR or a compatible RAR command-line executable.
- `7Z`: Requires 7-Zip.

External archive utilities must be installed separately for RAR and 7Z. If automatic detection fails, set the appropriate executable path in `config.json`.

Not every comic reader supports every image format. For broad compatibility, JPEG images inside CBZ packages are a safe default. WEBP and TIFF support depends on the reader.

## Source Folder Example

```text
D:\Manga\
├── Manga One\
│   ├── 001.png
│   ├── 002.png
│   └── 003.png
├── Manga Two\
│   ├── 001.jpg
│   └── 002.jpg
└── Manga Three\
    └── chapter1\
        ├── 001.png
        └── 002.png
```

Each immediate subfolder is processed independently. Image files are discovered recursively, including images in nested subfolders.

## Output Example

With `package_format` set to `CBZ` and `output_folder` set to `D:\\Manga_Packages`:

```text
D:\Manga_Packages\
├── Manga One.cbz
├── Manga Two.cbz
└── Manga Three.cbz
```

Changing `package_format` to `ZIP`, `RAR`, or `7Z` changes the output extension and archive creation method.

Pages inside each archive receive sequential names, such as:

```text
000001.webp
000002.webp
000003.webp
```

## Run

From the project root:

```bat
py main.py
```

The program prints progress and reports any folder that fails to process.

## Source Deletion Warning

By default, `delete_original_after_success` is `false`.

When enabled, the program deletes the entire source manga folder only after the package has been created and its integrity check has passed. This includes original images, converted images, and nested files.

Keep this option disabled until you have verified your output packages and backups.

If a package with the expected name already exists, that manga folder is skipped. The program does not automatically replace an existing package.

## Troubleshooting

### `pip` is not recognized

Use:

```bat
py -m pip install -r requirements.txt
```

If Python is installed but pip is missing, try:

```bat
py -m ensurepip --upgrade
py -m pip install -r requirements.txt
```

### RAR executable not found

Install WinRAR or configure the full executable path in `rar_executable`.

### 7-Zip executable not found

Install 7-Zip or configure the full executable path in `seven_zip_executable`.

### No pages found

Check `output_image_format`. The package creator searches for images matching the configured output format. Also check whether image conversion completed successfully.

### Package already exists

The program skips folders whose output package already exists. Move or rename the existing package if you want to process that folder again.

### Package fails verification

The program removes its temporary archive when packaging fails. The source folder is retained by the processing routine unless it was successfully packaged and verified.

## Dependencies

The Python dependency list is maintained in `requirements.txt`.

External archive utilities are required only when using RAR or 7Z output.
