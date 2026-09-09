"""
TRD GTX - Automated login + Price & Availability export
---------------------------------------------------------
Designed to run headlessly in GitHub Actions (or locally).

Credentials are read from environment variables:
    TRD_USERNAME
    TRD_PASSWORD

Locally, you can either set those env vars yourself, or just
hardcode them below for quick testing (don't commit real
credentials to the repo if you do that).
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
USERNAME = os.environ.get("TRD_USERNAME", "")
PASSWORD = os.environ.get("TRD_PASSWORD", "")
TENANT = "TRD"

LOGIN_URL = "https://trd.grupatopex.com:5051/auth/login"

# Fixed output path/filename -> this is what makes the download link stable.
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_FILENAME = "price_and_availability.xlsx"

# In CI this should always be True. Locally, set env var TRD_HEADLESS=false to watch it run.
HEADLESS = os.environ.get("TRD_HEADLESS", "true").lower() != "false"

# ------------------------------------------------------------------


def run():
    OUTPUT_DIR.mkdir(exist_ok=True)
    final_path = OUTPUT_DIR / OUTPUT_FILENAME

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("Navigating to login page...")
        page.goto(LOGIN_URL, wait_until="networkidle")

        username_input = page.locator("input[name='username']")
        username_input.wait_for(state="visible", timeout=15000)
        username_input.fill(USERNAME)

        password_input = page.locator("input[name='password']")
        password_input.fill(PASSWORD)

        tenant_input = page.locator("input[placeholder='Select system']")
        tenant_input.click()
        tenant_option = page.locator("div.dx-list-item-content", has_text=TENANT)
        tenant_option.wait_for(state="visible", timeout=10000)
        tenant_option.click()

        password_input.press("Enter")

        try:
            page.wait_for_selector("text=Items", timeout=20000)
        except PlaywrightTimeoutError:
            sign_in_btn = page.get_by_role("button", name="Sign In")
            if sign_in_btn.count() > 0:
                sign_in_btn.click()
                page.wait_for_selector("text=Items", timeout=20000)

        print("Logged in. Navigating to Price & Availability...")

        items_node = page.locator("div.dx-treeview-item-content span", has_text="Items")
        items_node.click()

        price_avail_link = page.get_by_text("Price & Availability", exact=True)
        price_avail_link.wait_for(state="visible", timeout=15000)
        price_avail_link.click()

        page.wait_for_selector("text=Drag a column header here to group by that column", timeout=20000)
        time.sleep(1)

        print("Opening export menu...")
        export_button = page.locator("i.dx-icon-export").first
        export_button.click()

        export_all_option = page.get_by_text("Export all data to Excel", exact=True)
        export_all_option.wait_for(state="visible", timeout=10000)

        with page.expect_download(timeout=30000) as download_info:
            export_all_option.click()

        download = download_info.value

        # Save to a FIXED filename each time (overwrites previous day's file)
        # so the public download link never changes.
        download.save_as(final_path)

        print(f"Export complete. File saved to: {final_path}")

        browser.close()


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise SystemExit(
            "TRD_USERNAME and TRD_PASSWORD environment variables must be set."
        )
    run()
