# TRD GTX Daily Export

Automatically logs into TRD GTX every day at 03:00 UTC, exports the
"Price & Availability" grid to Excel, and commits the refreshed file
back into this repo at a fixed path — giving you one stable public
link that always serves the latest data.

## One-time setup

1. Create a **public** GitHub repository and push these files to it.
2. Go to the repo's **Settings > Secrets and variables > Actions** and
   add two repository secrets:
   - `TRD_USERNAME` — your TRD login email
   - `TRD_PASSWORD` — your TRD password
3. That's it. The workflow in `.github/workflows/daily_export.yml`
   will run automatically every day at 03:00 UTC, and can also be
   triggered manually from the **Actions** tab (`Run workflow` button)
   to test it immediately without waiting for 3am.

## Your permanent download link

Once the workflow has run at least once, the file is available at:

```
https://raw.githubusercontent.com/<your-username>/<your-repo>/main/data/price_and_availability.xlsx
```

Replace `<your-username>` and `<your-repo>` with your actual GitHub
username and repository name. This URL never changes — every day's
run overwrites the same file, so the link always serves the freshest
export. (GitHub's CDN caches raw files for a few minutes, so there
may be a short delay right after each run before the new version is
visible.)

## Local testing

```
pip install -r requirements.txt
playwright install chromium
TRD_USERNAME=you@example.com TRD_PASSWORD=yourpassword TRD_HEADLESS=false python trd_export.py
```

Setting `TRD_HEADLESS=false` opens a visible browser window so you
can watch it run and confirm the selectors still match the site.

## Notes

- Because this is a **public** repository, anyone with the link can
  download the exported pricing/stock data. Only use this setup if
  that's acceptable for your use case.
- If TRD GTX changes its login form or grid layout, the selectors in
  `trd_export.py` may need updating.
