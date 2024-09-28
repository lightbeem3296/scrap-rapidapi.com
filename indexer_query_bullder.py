import json
import re
import time
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
OUTPUT_FILE_PATH = CUR_PATH / "index_query_list.jsonl"


def search_by_query(page, query: str) -> None:
    page.fill("input.relative", f'"{query}"')
    page.query_selector("div.flex.h-5.w-auto.cursor-default").click()
    time.sleep(1)
    page.wait_for_selector("span.text-xl.font-semibold", state="visible")
    res_str = page.query_selector_all("span.text-xl.font-semibold")[1].inner_text()
    res_count = int(re.search(r"\((\d+)\)", res_str).group(1))
    logger.info(f"{query}: {res_count}")
    if res_count <= 1000 and res_count > 0:
        with OUTPUT_FILE_PATH.open("a") as file:
            file.write(
                json.dumps(
                    {
                        "query": query,
                        "count": res_count,
                    }
                )
                + "\n"
            )
    else:
        for ch in "abcdefghijklmnopqrstuvwxyz":
            search_by_query(page=page, query=query + ch)


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://rapidapi.com/search")

        if OUTPUT_FILE_PATH.exists():
            OUTPUT_FILE_PATH.unlink()

        search_by_query(
            page=page,
            query="",
        )

        context.close()
        browser.close()


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
