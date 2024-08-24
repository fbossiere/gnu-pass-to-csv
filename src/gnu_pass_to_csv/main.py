import concurrent.futures
import os
import re
import subprocess
from csv import QUOTE_NONNUMERIC
from pathlib import Path

import pandas as pd
import typer
from loguru import logger


class PasswordExporter:
    """Export passwords from GnuPG encrypted files to a CSV file."""

    EMAIL_PATTERN = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    URL_PATTERN = r"/([^/]+\.[^/]+)/"
    SECOND_URL_PATTERN = r"/([^/]+\.[^/]+).gpg"

    def __init__(
        self,
        password_store_dir: str,
        vault: str,
        output_csv: str,
        max_workers: int,
        passphrase: str | None,
    ):
        """Initialize the PasswordExporter class.

        Args:
            password_store_dir (str): The directory where the GnuPG encrypted files are stored.
            vault (str): Vault name.
            output_csv (str): The path to the output CSV file.
            max_workers (int): The number of concurrent workers to use.
            passphrase (str | None): The GPG passphrase. If not provided, will use the GPG_PASSPHRASE environment variable.

        Raises:
            typer.Exit: If the GPG passphrase is not provided.
        """
        self.password_store_dir = Path(os.path.expanduser(password_store_dir))
        self.vault = vault
        self.output_csv = Path(output_csv)
        self.max_workers = max_workers
        if passphrase is not None:
            self.passphrase = passphrase
        else:
            possible_passphrase = os.getenv("GPG_PASSPHRASE")
            if possible_passphrase is None:
                typer.echo("GPG passphrase not provided.", err=True)
                raise typer.Exit(1)
            else:
                self.passphrase = possible_passphrase

    def list_gpg_files(self, folder_path: Path) -> list[Path]:
        """List all GPG files in the provided directory.

        Args:
            folder_path (Path): Path to the directory containing GPG files

        Returns:
            list[Path]: List of GPG files
        """
        return list(folder_path.rglob("*.gpg"))

    def decrypt_gpg_file(self, file_path: Path) -> list[str]:
        """Decrypts a GPG file and returns the decrypted content as a list of lines.

        Args:
            file_path (Path): Path to the GPG file

        Returns:
            list[str]: Decrypted content of the GPG file
        """
        result = subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--pinentry-mode",
                "loopback",
                "--passphrase",
                self.passphrase,
                "--decrypt",
                str(file_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to decrypt {file_path}: {result.stderr.strip()}")
            return []

        return result.stdout.splitlines()

    @classmethod
    def extract_url(cls, file_path: Path) -> str:
        """Extract URL from the entry name.

        Args:
            file_path (Path):  Path to the GPG file

        Returns:
            str: URL extracted from the entry name
        """
        possible_url = re.search(cls.URL_PATTERN, str(file_path))
        if possible_url:
            return possible_url.group(1)
        else:
            other_possible_url = re.search(cls.SECOND_URL_PATTERN, str(file_path))
            return other_possible_url.group(1) if other_possible_url else ""

    @classmethod
    def extract_email(cls, file_path: Path, notes: list[str]) -> str:
        """Extract email from the decrypted content.

        Args:
            file_path (Path): Path to the GPG file
            notes (list[str]): Decrypted content of the GPG file

        Returns:
            str: Extracted email
        """
        possible_email_line = next((line for line in notes), "")
        email_match = re.search(cls.EMAIL_PATTERN, possible_email_line)
        if email_match:
            return email_match.group(1)
        email_match = re.search(cls.EMAIL_PATTERN, str(file_path))
        if email_match:
            return email_match.group(1)
        return ""

    @staticmethod
    def extract_username(notes: list[str]) -> str:
        """Extract username from the decrypted content.

        Args:
            notes (list[str]): Decrypted content of the GPG file

        Returns:
            str: Extracted username
        """
        username_line = next((line for line in notes if "username:" in line), "")
        return username_line.split(":")[1].strip() if username_line else ""

    @staticmethod
    def extract_notes(raw_notes: list[str]) -> str:
        """Extract notes from the decrypted content.

        Args:
            raw_notes (list[str]): Decrypted content of the GPG file

        Returns:
            str: Extracted notes
        """
        return "\n".join(
            [
                line
                for line in raw_notes[1:]
                if not any(keyword in line for keyword in ["login:", "username:"])
            ]
        )

    def extract_password_details(self, file_path: Path) -> dict[str, str] | None:
        """Extract password details from a decrypted GPG file.

        Args:
            file_path (Path): Path to the GPG file

        Returns:
            dict[str, str] | None: Extracted password details
        """
        decrypted_content = self.decrypt_gpg_file(file_path)

        if not decrypted_content:
            return None

        # Process decrypted lines to extract relevant details
        # Extract possible URL from the entry name
        url = self.extract_url(file_path)
        password = decrypted_content[0]
        email = self.extract_email(file_path, decrypted_content[1:])
        username = self.extract_username(decrypted_content[1:])
        notes = self.extract_notes(decrypted_content)

        # Construct the details dictionary
        return {
            "name": url,
            "url": url,
            "email": email,
            "username": username or email,
            "password": password,
            "note": notes,
            "totp": "",  # If TOTP is available, extract it
            "vault": self.vault,
        }

    def export_passwords(self):
        """Export passwords to a CSV file.

        Raises:
            typer.Exit: If no password entries are found
        """
        gpg_files = self.list_gpg_files(self.password_store_dir)
        logger.info(f"Found {len(gpg_files)} GPG files.")

        if not gpg_files:
            typer.echo(
                "No password entries found. Ensure GnuPG is set up correctly.", err=True
            )
            raise typer.Exit(code=1)

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            results = list(executor.map(self.extract_password_details, gpg_files))

        # Filter out any None results from failed decryptions
        filtered_results = [result for result in results if result]

        # Create a DataFrame and export to CSV
        df = pd.DataFrame(filtered_results)

        # Assuming `self.output_csv` is the path to your CSV file
        self.output_csv.expanduser().parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_csv, index=False, quoting=QUOTE_NONNUMERIC)

        typer.echo(f"Passwords exported successfully to {self.output_csv}")


app = typer.Typer()


@app.command()
def convert(
    password_store_dir: str = typer.Option(
        "~/.password-store", help="Password store directory"
    ),
    vault: str = typer.Option("Password Store", help="Vault name"),
    output_csv: str = typer.Option(
        "~/Documents/passwords_export.csv", help="Output CSV file path"
    ),
    max_workers: int = typer.Option(4, help="Number of concurrent workers"),
    passphrase: str | None = typer.Option(
        None,
        prompt=False,
        hide_input=True,
        help="GPG passphrase. If not provided, will use the GPG_PASSPHRASE environment variable.",
    ),
):
    """Export passwords from GnuPG encrypted files to a CSV file.

    Args:
        password_store_dir (str, optional): The directory where the GnuPG encrypted files are stored. Defaults to typer.Option( "~/.password-store", help="Password store directory" ).
        output_csv (str, optional): The path to the output CSV file. Defaults to typer.Option( "~/Documents/passwords_export.csv", help="Output CSV file path" ).
        max_workers (int, optional): The number of concurrent workers to use. Defaults to typer.Option( 4, help="Number of concurrent workers" ).
        passphrase (str | None, optional): The GPG passphrase. If not provided, will use the GPG_PASSPHRASE environment variable. Defaults to typer.Option( None, prompt=False, hide_input=True, help="GPG passphrase. If not provided, will use the GPG_PASSPHRASE environment variable." ).
    """
    exporter = PasswordExporter(
        password_store_dir, vault, output_csv, max_workers, passphrase
    )
    exporter.export_passwords()


if __name__ == "__main__":
    app()
