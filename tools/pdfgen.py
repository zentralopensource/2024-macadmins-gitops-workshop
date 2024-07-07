# Tool to generate the PDF files with the first login info
#
# Dependencies:
#  - pandoc
#  - wkhtmltopdf
#  - ghostscript
#
import argparse
import csv
import os.path
import subprocess
import tempfile
import unicodedata
from urllib.parse import urlparse


def iter_instances(csv_source):
    with open(csv_source, newline="") as csvfile:
        for row in csv.reader(csvfile):
            if not row[0].startswith("https"):
                continue
            yield row


def create_markdown(instance):
    url, password = instance
    password = unicodedata.normalize('NFC', password)
    o = urlparse(url)
    slug = o.netloc.split(".", 1)[0]
    return slug, "\n".join((
        "# Welcome to the Zentral GitOps workshop!",
        "",
        "## Your Zentral instance:",
        "",
        f"**URL:** [{url}]({url})",
        "",
        "**Username:** support@zentral.com",
        "",
        f"**Password:** {password}",
        "",
    ))


def generate_first_login_pdf_file(instance, output_dir):
    slug, md = create_markdown(instance)
    pandoc_css = os.path.join(os.path.dirname(__file__), "pandoc.css")
    output_file = os.path.join(output_dir, f"{slug}.pdf")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md") as mdfile:
        mdfile.write(md)
        mdfile.flush()
        subprocess.run([
            "pandoc", mdfile.name,
            "--css", pandoc_css,
            "--pdf-engine", "wkhtmltopdf",
            "-V", "papersize:A4",
            "-o", output_file],
            capture_output=True,
            check=True
        )
    return output_file


def merge_pdf_files(output_files, output_dir):
    output_file = os.path.join(output_dir, "psumac24_zentral_gitops_workshop.pdf")
    args = [
        "gs", "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        f"-sOUTPUTFILE={output_file}",
        "-dBATCH"
    ]
    args.extend(output_files)
    subprocess.run(args, capture_output=True)
    return output_file


def generate_first_login_pdf_files(csv_source, output_dir):
    output_files = []
    for instance in iter_instances(csv_source):
        output_file = generate_first_login_pdf_file(instance, output_dir)
        print(output_file)
        output_files.append(output_file)
    print(merge_pdf_files(output_files, output_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("pdfgen.py")
    parser.add_argument('csv_source', help="CSV file containing the information about the instances")
    parser.add_argument('output_dir', help="Path to the directory where the PDF files will be written")
    args = parser.parse_args()
    generate_first_login_pdf_files(args.csv_source, args.output_dir)
