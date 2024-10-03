import json
import os
import sys
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INDEXING_LINK = "https://rapidapi.com/search?sortBy%3DByRelevance"
OUTPUT_DIR = CUR_PATH / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def navigate(page, link: str) -> bool:
    ret = True

    try:  # noqa: SIM105
        page.goto(link, wait_until="networkidle", timeout=10000)
    except:  # noqa: E722, S110
        pass

    if page.url != link:
        ret = False

    return ret


def wait_for_selector(page, selector: str) -> None:
    page.wait_for_selector(selector, timeout=10000, state="attached")


def scrap_one(page, api_info: dict) -> bool:
    ret = False
    try:
        output_file_name = api_info["id"] + "_score.json"
        output_file_path = OUTPUT_DIR / output_file_name

        already_done = False
        if output_file_path.exists():
            with open(output_file_path) as output_file:
                try:
                    saved_info = json.load(output_file)
                    if saved_info["id"] == api_info["id"]:
                        already_done = True
                except:  # noqa: E722, S110
                    output_file_path.unlink()

        api_link = f'https://rapidapi.com/{api_info["user"]["slugifiedName"]}/api/{api_info["slugifiedName"]}'
        if already_done:
            logger.info("already done")
        elif navigate(page, api_link):
            store_info = {}

            # id
            store_info["id"] = api_info["id"]

            # name
            wait_for_selector(page, "div.rr--group")
            score_str = page.query_selector("div.rr--group").get_attribute("aria-label")
            store_info["score"] = (
                score_str.replace("Rated", "").replace("on 5", "").strip()
            )

            with open(output_file_path, "w") as output_file:  # noqa: PTH123
                json.dump(store_info, output_file, indent=2, default=str)
        else:
            logger.error("server error")

        ret = True
    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)
    return ret


def work(page, index_file_path: str) -> None:  # noqa: PLR0915
    index_file_name = os.path.basename(index_file_path)
    logger.info(f"index_file_name: {index_file_name}")
    with open(index_file_path, "r") as index_file:
        line_number = 0
        for line in index_file:
            api_info = json.loads(line)
            logger.info(f'{line_number} > {api_info["category"]} > {api_info["id"]}')
            scrap_one(page=page, api_info=api_info)
            line_number += 1


def main() -> None:
    try:
        if len(sys.argv) > 1:
            index_file_list = sys.argv[1:]
            for index_file_path in index_file_list:
                logger.info(f"index_file_path: {index_file_path}")

            with sync_playwright() as pw_ctx_man:
                browser = pw_ctx_man.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                page.goto(
                    "https://rapidapi.com/search?sortBy%3DByRelevance", timeout=60000
                )
                for index_file_path in index_file_list:
                    work(page, index_file_path)

                context.close()
                browser.close()

    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)


if __name__ == "__main__":
    main()
