import json
import time
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
OUTPUT_FILE_PATH = CUR_PATH / "index_collections.jsonl"


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        if OUTPUT_FILE_PATH.exists():
            OUTPUT_FILE_PATH.unlink()

        try:
            page.goto(
                "https://rapidapi.com/collections",
                wait_until="networkidle",
                timeout=10000,
            )
        except:  # noqa: E722
            pass

        while True:
            cards = page.query_selector_all("div.h-\\[200px\\]")
            for card in cards:
                collection_name = card.query_selector("div.line-clamp-1").inner_text()
                parent = card.evaluate_handle("element => element.parentElement")
                collection_link = parent.as_element().get_attribute("href")
                with OUTPUT_FILE_PATH.open("a") as file:
                    file.write(
                        json.dumps(
                            {
                                "name": collection_name,
                                "link": collection_link,
                            }
                        )
                        + "\n"
                    )

            btns = page.query_selector_all("button.justify-center.flex")
            next_btn = btns[1]
            if next_btn.is_disabled():
                break
            else:
                next_btn.click()
                time.sleep(1)

        context.close()
        browser.close()


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
