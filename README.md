# GNU GPG Password Dumper

A Python tool to decrypt and export your GPG-encrypted passwords stored in a pass-compatible directory to a CSV file. This tool is ideal for users who manage their passwords using `pass` and need to export them for backup or migration purposes.

## Features

- **Decrypt GPG-encrypted passwords:** Automatically decrypts `.gpg` files in your password store directory.
- **Parallel processing:** Utilizes concurrent processing to speed up the decryption and export process.
- **Customizable output:** Exports password details to a customizable CSV file.
- **Environment variable support:** Load environment variables from a `.env` file.

## Requirements

- Python 3.12
- GnuPG (GPG) installed and configured on your system
- `Poetry` for dependency management

## Installation

1. **Clone the repository:**

   ```bash
   git clone git@gitlab.com:fbossiere/gnu-pass-to-csv.git
   cd gnu-pass-to-csv
   ```

2. **Install dependencies with Poetry:**

   Ensure you have Poetry installed. If not, install it following the [official guide](https://python-poetry.org/docs/#installation).

   ```bash
   poetry install
   ```

   This command will create a virtual environment and install all necessary dependencies.

## CSV File Format

The exported CSV file will contain the following fields:

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

- **name**: The relative path to the password file from the base password store directory.
- **url**: The URL associated with the password. (Currently left empty by default)
- **email**: The email address associated with the password. (Currently left empty by default)
- **username**: The username associated with the password. (Currently left empty by default)
- **password**: The first line of the decrypted file, which is typically the password itself.
- **note**: Any additional lines from the decrypted file are concatenated and stored in this field.
- **totp**: Field for storing Time-based One-Time Passwords (TOTP). (Currently left empty by default)
- **vault**: The vault to which the password belongs. The default value is "Personal".

## Usage

After installing the necessary dependencies, you can run the script to decrypt your GPG-encrypted passwords and export them to a CSV file.

### Option 1: Using Poetry

You can run the script directly using Poetry's run command:

```bash
poetry run password-exporter convert --passphrase "mypassphrase"
```

### Option 2: Using the Installed Script

If you prefer to use the installed script directly, you can run:

```bash
password-exporter convert --passphrase "mypassphrase"
```

This command will process the `.gpg` files in your password store directory and generate a CSV file with the structure described above.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue to discuss improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
