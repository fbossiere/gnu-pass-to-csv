---

# GNU GPG Password Dumper

This project is a Python 3.12 tool designed to export all passwords managed by GNU GPG into a properly formatted CSV file. It leverages Poetry for dependency management and packaging, ensuring a clean and reproducible environment.

## Features

- **Export GPG passwords**: Dumps all passwords managed by GNU GPG into a CSV format.
- **CSV Formatting**: Outputs the data in a well-structured CSV file for easy import into other password managers or storage systems.
- **Simple and Efficient**: Written in Python 3.12, the tool is efficient and easy to use.

## Prerequisites

- **Python 3.12**: Ensure you have Python 3.12 installed on your system.
- **GNU GPG**: The tool interacts with GNU GPG, so GPG must be installed and configured on your system.
- **Poetry**: This project uses Poetry for dependency management. You can install Poetry via pip:

  ```bash
  pip install poetry
  ```

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://gitlab.com/yourusername/gnu-gpg-password-dumper.git
    cd gnu-gpg-password-dumper
    ```

2. **Install dependencies**:

    Use Poetry to install all the necessary dependencies:

    ```bash
    poetry install
    ```

3. **Activate the virtual environment**:

    ```bash
    poetry shell
    ```

## Usage

Once the dependencies are installed and the virtual environment is activated, you can run the script to dump your GPG-managed passwords to a CSV file.

```bash
python dump_gpg_passwords.py output.csv
```

- `output.csv`: The name of the CSV file where the passwords will be stored.

### Example

To export your passwords to a file named `my_passwords.csv`:

```bash
python dump_gpg_passwords.py my_passwords.csv
```

## CSV Format

The generated CSV file will have the following structure:

| Name        | URL | Email | Username | Password | Note | TOTP | Vault |
|-------------|-----|-------|----------|----------|------|------|-------|
| Entry Name  | URL | Email | Username | Password | Notes | TOTP | Personal |

- **Name**: The name or title of the password entry.
- **URL**: The URL associated with the entry (if available).
- **Email**: The email associated with the entry (if available).
- **Username**: The username associated with the entry (if available).
- **Password**: The password (assumed to be the first line of the entry).
- **Note**: Any additional notes or remaining lines from the password entry.
- **TOTP**: The Time-based One-Time Password (TOTP) if used (if available).
- **Vault**: The category of the vault (default is "Personal").

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a Merge Request.

Please ensure your code adheres to the existing code style and includes appropriate test coverage.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the GNU GPG community for their extensive documentation and support.
- This project was inspired by the need for a simple tool to export GPG passwords into a more universally usable format.

---