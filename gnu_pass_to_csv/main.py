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
    EMAIL_PATTERN = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    URL_PATTERN = r"/([^/]+\.[^/]+)/"
    SECOND_URL_PATTERN = r"/([^/]+\.[^/]+).gpg"

    def __init__(
        self,
        passphrase: str | None,
        password_store_dir: str,
        output_csv: str,
        max_workers: int,
    ):
        self.password_store_dir = os.path.expanduser(password_store_dir)
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

    def list_gpg_files(self, folder_path: str) -> list[str]:
        """List all GPG files in the provided directory."""
        return [
            os.path.join(root, file)
            for root, _, files in os.walk(folder_path)
            for file in files
            if file.endswith(".gpg")
        ]

    def decrypt_gpg_file(self, file_path: str) -> str:
        """Decrypts a GPG file and returns the decrypted content as a string."""
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
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to decrypt {file_path}: {result.stderr.strip()}")
            return ""

        return result.stdout

    @classmethod
    def extract_url(cls, entry_name):
        possible_url = re.search(cls.URL_PATTERN, entry_name)
        if possible_url:
            return possible_url.group(1)
        else:
            other_possible_url = re.search(cls.SECOND_URL_PATTERN, entry_name)
            return other_possible_url.group(1) if other_possible_url else ""

    @classmethod
    def extract_email(cls, password_details):
        login_line = next(
            (line for line in password_details[1:] if "login:" in line), ""
        )
        email_match = re.search(cls.EMAIL_PATTERN, login_line)
        return email_match.group(1) if email_match else ""

    @staticmethod
    def extract_username(password_details):
        username_line = next(
            (line for line in password_details[1:] if "username:" in line), ""
        )
        return username_line.split(":")[1].strip() if username_line else ""

    @staticmethod
    def extract_notes(password_details):
        return [
            line
            for line in password_details[1:]
            if not any(keyword in line for keyword in ["login:", "username:"])
        ]

    def extract_password_details(self, file_path: str) -> dict[str, str] | None:
        """Extract password details from a decrypted GPG file."""
        decrypted_content = self.decrypt_gpg_file(file_path)

        if not decrypted_content:
            return None

        # Process decrypted lines to extract relevant details
        # Extract possible URL from the entry name
        url = self.extract_url(file_path)
        password = decrypted_content[0]
        email = self.extract_email(decrypted_content)
        username = self.extract_username(decrypted_content)
        notes = self.extract_notes(decrypted_content)

        # Construct the details dictionary
        return {
            "name": url,
            "url": url,
            "email": email,
            "username": username,
            "password": password,
            "note": "\n".join(notes),
            "totp": "",  # If TOTP is available, extract it
            "vault": "Personal",
        }

    def export_passwords(self):
        gpg_files = self.list_gpg_files(self.password_store_dir)[:3]
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
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_csv, index=False, quoting=QUOTE_NONNUMERIC)

        typer.echo(f"Passwords exported successfully to {self.output_csv}")


app = typer.Typer()


@app.command()
def convert(
    password_store_dir: str = typer.Option(
        "~/.password-store", help="Password store directory"
    ),
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
    exporter = PasswordExporter(passphrase, password_store_dir, output_csv, max_workers)
    exporter.export_passwords()


if __name__ == "__main__":
    app()
