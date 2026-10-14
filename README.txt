# PixPack

**A lightweight batch image converter and archive packer for Windows.**

Convert images into your preferred format, organize them by folder, and package entire directories into ZIP, CBZ, RAR, or 7Z archives using a simple configuration file.

## ✨ Features

- **Batch image conversion** — Convert multiple images recursively across folders.
- **Multiple image formats** — Configure the target format and image quality.
- **Archive creation** — Package folders into ZIP, CBZ, RAR, or 7Z files.
- **Flexible output paths** — Choose where converted images and archives are saved.
- **Configurable workflow** — Control behavior through `config.json` without editing source code.
- **Optional cleanup** — Configure whether original files are deleted after successful processing.
- **Lightweight dependencies** — Uses Python and Pillow for image processing.

## 📦 Supported Formats

### Image conversion

The available output formats depend on the formats supported by Pillow. Common choices include:

- JPEG / JPG
- PNG
- WebP
- BMP
- TIFF

### Archive packaging

| Format | Requirements |
|---|---|
| ZIP | Built-in Python support |
| CBZ | Built-in Python support; ZIP-compatible archive |
| RAR | WinRAR or a compatible RAR command-line executable |
| 7Z | 7-Zip command-line executable |

External archive tools must be installed and configured for RAR and 7Z output.

## 🚀 Getting Started

### 1. Requirements

- Windows
- Python 3.10 or later recommended
- Git (optional)

Check your Python installation:

```powershell
py --version
```

### 2. Clone the repository

```powershell
git clone https://github.com/YOUR_USERNAME/pixpack.git
cd pixpack
```

Replace `YOUR_USERNAME` with your GitHub username.

Alternatively, download the repository as a ZIP file and extract it.

### 3. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 4. Configure the application

Edit `config.json` to set your input directory, output directory, image format, and archive format.

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

### 5. Run PixPack

From the project root:

```powershell
py main.py
```

## ⚙️ Configuration

| Setting | Description |
|---|---|
| `parent_folder` | Root directory containing the folders to process |
| `cbz_output_in_parent` | Controls whether CBZ output is placed in the parent directory |
| `output_folder` | Destination directory for archive output when applicable |
| `output_image_format` | Target image format, such as `WEBP`, `JPEG`, or `PNG` |
| `output_image_quality` | Image quality setting for formats that support it |
| `package_format` | Archive format: `ZIP`, `CBZ`, `RAR`, or `7Z` |
| `delete_original_after_success` | Whether original files may be deleted after successful processing |
| `rar_executable` | Path to the RAR command-line executable |
| `seven_zip_executable` | Path to the 7-Zip command-line executable |

**Important:** Back up important files before enabling automatic deletion. Test the workflow with a small sample directory first.

Use escaped backslashes (`\\`) in Windows paths inside JSON strings.

## 📁 Project Structure

```text
pixpack/
├── main.py
├── config.json
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    └── image_batch_tool/
        ├── __init__.py
        ├── image_converter.py
        └── package_creator.py
```

## 🛠️ Dependencies

- [Python](https://www.python.org/)
- [Pillow](https://python-pillow.org/) — Image loading, processing, and conversion
- [7-Zip](https://www.7-zip.org/) — Required for 7Z packaging
- [WinRAR](https://www.win-rar.com/) — Required for RAR packaging

Only Pillow is listed as a Python dependency. External archive utilities are optional and are needed only for their respective archive formats.

## 🔒 Safety Notes

- Keep `delete_original_after_success` set to `false` until you have verified the results.
- Use a test directory before processing large collections.
- Ensure the configured external executable paths are correct when using RAR or 7Z.
- Avoid committing private paths or other sensitive local configuration to a public repository.

## 🗺️ Roadmap

Potential future improvements:

- [ ] Desktop graphical interface
- [ ] Processing progress and detailed logs
- [ ] Additional image-processing options
- [ ] Improved error recovery and reporting
- [ ] Build a standalone Windows executable

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome. Please include steps to reproduce issues and relevant error messages when reporting bugs.

## 📄 License

No license has been specified yet. Add a `LICENSE` file before distributing the project or accepting contributions under a particular license.