# GNU GPG Password Exporter

`gnu-pass-to-csv` is a Python tool designed to decrypt and export your GPG-encrypted passwords stored in a pass-compatible directory to a CSV file. This tool is ideal for users who manage their passwords using `pass` and need to export them for backup, migration, or integration purposes.

## Features

- **Automatic GPG Decryption:** Seamlessly decrypts `.gpg` files in your password store directory.
- **Parallel Processing:** Leverages concurrent processing to accelerate the decryption and export operations.
- **Customizable Output:** Easily export password data to a CSV file with a customizable structure.

## Requirements

- **Python 3.12** or higher
- **GnuPG (GPG):** Ensure GPG is installed and properly configured on your system.

## Installation

You can install `gnu-pass-to-csv` directly from PyPI:

```bash
pip install gnu-pass-to-csv
```

Alternatively, if you prefer using the source code:

1. **Clone the repository:**

   ```bash
   git clone git@gitlab.com:fbossiere/gnu-pass-to-csv.git
   cd gnu-pass-to-csv
   ```

2. **Install dependencies with Poetry:**

   Make sure Poetry is installed. If not, install it using the [Poetry Installation Guide](https://python-poetry.org/docs/#installation).

   ```bash
   poetry install
   ```

   This command sets up a virtual environment and installs all required dependencies.

## CSV File Structure

The tool exports your passwords to a CSV file with the following structure:

```json
{
    "name": "relative/path/to/password/file",
    "url": "",
    "email": "",
    "username": "",
    "password": "first line of the decrypted file (usually the password)",
    "note": "additional lines concatenated as a single string",
    "totp": "",
    "vault": "Personal"
}
```

### Field Descriptions

- **name**: Relative path to the password file from the base password store directory.
- **url**: URL associated with the password (if available).
- **email**: Email address associated with the password (if available).
- **username**: Username associated with the password (if available).
- **password**: The first line of the decrypted file, typically the password.
- **note**: Additional lines from the decrypted file concatenated into a single string.
- **totp**: Field for storing Time-based One-Time Passwords (TOTP) (if available).
- **vault**: The vault category to which the password belongs (default is "Personal").

## Usage

After installing the package, you can use the tool to decrypt your GPG-encrypted passwords and export them to a CSV file.

### Option 1: Using the Installed Script Directly

Simply run the installed script:

```bash
gnu-pass-to-csv
```

This command processes the `.gpg` files in your password store directory and generates a CSV file according to the structure described above.

### Option 2: Running with Poetry

If you've installed the dependencies using Poetry, you can run the script as follows:

```bash
poetry run gnu-pass-to-csv
```

### Additional Options

The script supports several options to customize its behavior:

- `--password-store-dir`: Specify a custom password store directory (default: `~/.password-store`).
- `--output-csv`: Specify the output CSV file path (default: `~/Documents/passwords_export.csv`).
- `--max-workers`: Define the number of concurrent workers to speed up processing (default: 4).
- `--passphrase`: Provide the GPG passphrase directly as an argument. If omitted, the script will use the `GPG_PASSPHRASE` environment variable.
- `--vault`: Define the vault category for the exported passwords (default: "Personal").

To see all available options, use the `--help` flag:

```bash
gnu-pass-to-csv --help
```

## Contributing

Contributions are highly encouraged! Please feel free to submit a Pull Request or open an issue to discuss any improvements or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
