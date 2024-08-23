import concurrent.futures
import os
import subprocess
from csv import QUOTE_NONNUMERIC

import pandas as pd
import typer
from dotenv import load_dotenv
from loguru import logger


class PasswordExporter:
    def __init__(self, passphrase: str, password_store_dir: str, output_csv: str):
        self.passphrase = passphrase
        self.password_store_dir = os.path.expanduser(password_store_dir)
        self.output_csv = output_csv

    def load_environment(self):
        load_dotenv()

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

    def extract_password_details(self, file_path: str) -> dict[str, str] | None:
        """Extract password details from a decrypted GPG file."""
        decrypted_content = self.decrypt_gpg_file(file_path)

        if not decrypted_content:
            return None

        lines = decrypted_content.splitlines()
        return {
            "name": os.path.relpath(file_path, self.password_store_dir),
            "url": "",
            "email": "",
            "username": "",
            "password": lines[0] if lines else "",
            "note": "\n".join(lines[1:]),
            "totp": "",
            "vault": "Personal",
        }

    def export_passwords(self):
        self.load_environment()

        gpg_files = self.list_gpg_files(self.password_store_dir)[:3]
        logger.info(f"Found {len(gpg_files)} GPG files.")

        if not gpg_files:
            typer.echo(
                "No password entries found. Ensure GnuPG is set up correctly.", err=True
            )
            raise typer.Exit(code=1)

        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.extract_password_details, gpg_files))

        # Filter out any None results from failed decryptions
        filtered_results = [result for result in results if result]

        # Create a DataFrame and export to CSV
        df = pd.DataFrame(filtered_results)
        df.to_csv(self.output_csv, index=False, quoting=QUOTE_NONNUMERIC)

        typer.echo(f"Passwords exported successfully to {self.output_csv}")


app = typer.Typer()


@app.command()
def convert(
    passphrase: str = typer.Option(
        ..., prompt=True, hide_input=True, help="GPG passphrase"
    ),
    password_store_dir: str = typer.Option(
        "~/.password-store", help="Password store directory"
    ),
    output_csv: str = typer.Option(
        "../data/passwords_export.csv", help="Output CSV file path"
    ),
):
    exporter = PasswordExporter(passphrase, password_store_dir, output_csv)
    exporter.export_passwords()


if __name__ == "__main__":
    app()
