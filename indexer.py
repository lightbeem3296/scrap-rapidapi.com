from datetime import datetime, timedelta
import json
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INDEXING_LINK = "https://rapidapi.com/search?sortBy%3DByRelevance"
OUTPUT_FILE_PATH = CUR_PATH / "index.jsonl"


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(INDEXING_LINK, wait_until="networkidle")

        if OUTPUT_FILE_PATH.exists():
            OUTPUT_FILE_PATH.unlink()

        last_link = ""
        while True:
            cards = page.query_selector_all(selector="div.flex.bg-card.flex-col")
            if len(cards) == 0:
                break

            last_card = cards[-1]

            with OUTPUT_FILE_PATH.open("a") as output_file:
                for card in reversed(cards):
                    link_elem = card.query_selector("a")
                    link = link_elem.get_attribute("href")
                    if link != last_link:
                        now = datetime.now()
                        updated_str = (
                            card.query_selector("span.truncate.text-card-tertiary")
                            .inner_text()
                            .replace("Updated", "")
                            .replace("ago", "")
                            .strip()
                        )
                        words = updated_str.split(" ")
                        num = int(words[0])
                        delta = timedelta(0)
                        if words[1] == "seconds":
                            delta = timedelta(seconds=num)
                        elif words[1] == "minutes":
                            delta = timedelta(minutes=num)
                        elif words[1] == "hours":
                            delta = timedelta(hours=num)
                        elif words[1] == "days":
                            delta = timedelta(days=num)
                        elif words[1] == "months":
                            delta = timedelta(days=num * 30)
                        elif words[1] == "years":
                            delta = timedelta(days=num * 365)
                        updated = now - delta
                        index = {
                            "link": link,
                            "updated": updated.timestamp(),
                        }
                        line = json.dumps(index)

                        output_file.write(f"{line}\n")
                    else:
                        break
            last_link = last_card.query_selector("a").get_attribute("href")
            last_card.scroll_into_view_if_needed()

        context.close()
        browser.close()


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
