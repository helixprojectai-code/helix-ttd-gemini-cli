#!/usr/bin/env python3
"""Convert HTML presentation to PDF using Playwright."""

import os

from playwright.sync_api import sync_playwright


def convert_html_to_pdf(html_path, pdf_path):
    """Convert HTML file to PDF."""
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)

    # Convert Windows path to file URL
    url_path = html_path.replace(":", "|").replace("\\", "/")
    file_url = f"file:///{url_path}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url)
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"PDF generated: {pdf_path}")
    print(f"Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    html_file = "Z:/kimi/docs/DECK_HELIX_TTD_PROVIDER_PITCH.html"
    pdf_file = "Z:/kimi/docs/DECK_HELIX_TTD_PROVIDER_PITCH.pdf"
    convert_html_to_pdf(html_file, pdf_file)
