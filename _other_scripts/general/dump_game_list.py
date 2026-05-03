from playwright.sync_api import sync_playwright
import pandas as pd

BASE_URL = "https://www.serialstation.com/titles/?systems=683da1c8-1064-4e5d-a28f-765bb57d51f8&page={}"
OUTPUT_FILE = "ps5_titles_full.csv"

TOTAL_PAGES = 160  # safe upper bound (you said ~156)


def run():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, TOTAL_PAGES + 1):
            url = BASE_URL.format(page_num)
            print(f"Loading page {page_num}...")

            page.goto(url)

            # wait for table to load
            page.wait_for_selector("table tbody tr")

            table_rows = page.locator("table tbody tr")
            count = table_rows.count()

            if count == 0:
                print("No rows found, stopping early.")
                break

            for i in range(count):
                cols = table_rows.nth(i).locator("td")

                if cols.count() < 3:
                    continue

                rows.append({
                    "title_id": cols.nth(0).inner_text().strip(),
                    "content_id": cols.nth(1).inner_text().strip(),
                    "name": cols.nth(2).inner_text().strip()
                })

            print(f"Collected so far: {len(rows)}")

        browser.close()

    df = pd.DataFrame(rows).drop_duplicates()
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n DONE: {len(df)} rows saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()