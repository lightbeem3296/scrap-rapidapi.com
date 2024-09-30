import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INPUT_FILE_PATH = CUR_PATH / "index_collections.jsonl"
OUTPUT_FILE_PATH = CUR_PATH / "index_apis.jsonl"


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        with INPUT_FILE_PATH.open("r") as input_file:
            for line in input_file:
                collection_info = json.loads(line)
                logger.info(f"name: {collection_info['name']}")
                try:
                    page.goto(
                        "https://rapidapi.com" + collection_info["link"],
                        timeout=10000,
                        wait_until="networkidle",
                    )
                except:  # noqa: E722
                    pass

                while True:
                    cards = page.query_selector_all(
                        selector="div.flex.bg-card.flex-col"
                    )
                    with OUTPUT_FILE_PATH.open("a") as output_file:
                        for card in cards:
                            link_elem = card.query_selector("a")
                            link = link_elem.get_attribute("href")

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
                                "collection": collection_info["name"],
                                "link": link,
                                "updated": updated.timestamp(),
                            }
                            line = json.dumps(index)

                            output_file.write(f"{line}\n")

                    btns = page.query_selector_all("button.justify-center.flex")
                    if len(btns) >= 2:
                        next_btn = btns[1]
                        if next_btn.is_disabled():
                            break
                        else:
                            next_btn.click()
                            time.sleep(1)
                    else:
                        break

        context.close()
        browser.close()


def main():
    try:
        if OUTPUT_FILE_PATH.exists():
            OUTPUT_FILE_PATH.unlink()

        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
