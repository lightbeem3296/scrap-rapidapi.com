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


def navigate(page, link: str) -> None:
    try:  # noqa: SIM105
        page.goto(link, wait_until="networkidle", timeout=10000)
    except:  # noqa: E722, S110
        pass


def wait_for_selector(page, selector: str) -> None:
    page.wait_for_selector(selector, timeout=30000)


def get_pricing_price(card) -> tuple[str, str]:
    """returns tuple[plan, price]"""

    price = ""
    plan = card.query_selector("div.text-sm.font-semibold").inner_text().strip().lower()

    price = (
        card.query_selector_all("div.inline-flex")[0]
        .inner_text()
        .replace("\n", "")
        .strip()
    )
    return plan, price


def get_pricing_features(card) -> tuple[str, str]:
    """returns tuple[plan, features]"""

    features = ""
    plan = card.query_selector("div.text-sm.font-semibold").inner_text().strip().lower()

    features_elem = card.query_selector("div.flex.flex-col.gap-3")
    if features_elem is not None and "Features" in features_elem.inner_text():
        feature_elems = features_elem.query_selector_all("div.inline-flex.flex-col")
        for feature_elem in feature_elems:
            if (
                feature_elem.query_selector("svg").get_attribute("class")
                == "stroke-green-600"
            ):
                features += feature_elem.inner_text().replace("\n", " ").strip() + " | "

    return plan, features.strip(" |")


def get_pricing_requests(card) -> tuple[str, str]:
    """returns tuple[plan, requests]"""

    requests = ""
    plan = card.query_selector("div.text-sm.font-semibold").inner_text().strip().lower()

    elems = card.query_selector_all("div.flex.grow.basis-full.flex-col")
    for elem in elems:
        elem_text = elem.inner_text()
        requests += elem_text.strip().replace("\n", " - ") + " | "

    return plan, requests.strip(" |")


def get_pricing_rate_limit(card) -> tuple[str, str]:
    """returns tuple[plan, rate_limit]"""

    rate_limit = ""
    plan = card.query_selector("div.text-sm.font-semibold").inner_text().strip().lower()

    elems = card.query_selector_all("div.flex.flex-col.gap-3")
    for elem in elems:
        elem_text = elem.inner_text()
        if "Rate Limit" in elem_text:
            rate_limit = elem_text.replace("Rate Limit", "").replace("\n", "").strip()
            break

    return plan, rate_limit


def scrap_one(page, api_info: dict) -> bool:
    ret = False
    try:
        output_file_name = api_info["id"] + ".json"
        output_file_path = OUTPUT_DIR / output_file_name
        logger.info(f"file_name >> {output_file_name}")

        already_done = False
        if output_file_path.exists():
            with open(output_file_path) as output_file:
                try:
                    saved_info = json.load(output_file)
                    if saved_info["id"] == api_info["id"]:
                        already_done = True
                except:  # noqa: E722, S110
                    output_file_path.unlink()

        if already_done:
            logger.info("already done")
        else:
            api_link = f"https://rapidapi.com/{api_info["user"]["slugifiedName"]}/api/{api_info["slugifiedName"]}"
            navigate(page, api_link)

            store_info = {}

            # name
            store_info["name"] = api_info["name"]

            # link
            store_info["link"] = api_link

            if api_info["score"] is not None:
                # popularity
                store_info["popularity"] = api_info["score"]["popularityScore"]
                # service-level
                store_info["service_level"] = api_info["score"]["avgServiceLevel"]
                # latency
                store_info["latency"] = api_info["score"]["avgLatency"]
                # test
                store_info["test"] = api_info["score"]["avgSuccessRate"]
            else:
                store_info["popularity"] = 0
                store_info["service_level"] = 0
                store_info["latency"] = 0
                store_info["test"] = 0

            # description
            store_info["description"] = api_info["description"]

            wait_for_selector(page, "div.flex.w-full.flex-col.justify-between")
            elems = page.query_selector_all("div.flex.w-full.flex-col.justify-between")
            # creator-name
            store_info["creator_name"] = api_info["user"]["name"]
            store_info["creator_link"] = (
                f"https://rapidapi.com/user/{api_info["user"]["slugifiedName"]}"
            )
            # subscribers
            store_info["subscribers"] = (
                elems[1]
                .inner_text()
                .replace("Subscribers", "")
                .replace("Subs", "")
                .strip()
            )
            # category
            store_info["category"] = api_info["category"]
            # website
            store_info["website"] = ""
            if len(elems) >= 4:
                website_elem = elems[3].query_selector("a")
                if website_elem is not None:
                    store_info["website"] = website_elem.get_attribute("href")

            # version
            wait_for_selector(page, "div.rapid-select__single-value")
            store_info["version"] = (
                page.query_selector("div.rapid-select__single-value")
                .inner_text()
                .replace("(", "")
                .replace(")", "")
                .replace("current", "")
                .strip()
            )

            # created
            store_info["created"] = ""

            # updated
            store_info["updated"] = api_info["updatedAt"]

            # reviewers
            wait_for_selector(page, "div.text-xs.font-medium")
            store_info["reviewers"] = (
                page.query_selector("div.text-xs.font-medium")
                .inner_text()
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

            pricing_link = store_info + "/pricing"
            navigate(page, pricing_link)
            wait_for_selector(page, "div.flex.min-w-\\[256px\\]")
            cards = page.query_selector_all("div.flex.min-w-\\[256px\\]")
            for card in cards:
                plan, price = get_pricing_price(card)
                store_info[f"pricing_{plan}"] = price

                plan, requests = get_pricing_requests(card)
                store_info[f"pricing_{plan}_requests"] = requests

                plan, features = get_pricing_features(card)
                store_info[f"pricing_{plan}_features"] = features

                plan, rate_limit = get_pricing_rate_limit(card)
                store_info[f"pricing_{plan}_rate_limit"] = rate_limit

            with open(output_file_path, "w") as output_file:  # noqa: PTH123
                json.dump(store_info, output_file, indent=2, default=str)

        ret = True
    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)
    return ret


def work(index_file_path: str) -> None:  # noqa: PLR0915
    index_file_name = os.path.basename(index_file_path)
    logger.info(f"index_file_name: {index_file_name}")
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False, timeout=60000)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://rapidapi.com/search?sortBy%3DByRelevance")

        with open(index_file_path, "r") as index_file:
            line_number = 0
            for line in index_file:
                api_info = json.loads(line)

                while not scrap_one(
                    page=page,
                    api_info=api_info,
                ):
                    pass

                line_number += 1

        context.close()
        browser.close()


def main() -> None:
    try:
        if len(sys.argv) > 1:
            index_file_list = sys.argv[1:]
            for index_file_path in index_file_list:
                logger.info(f"index_file_path: {index_file_path}")
            for index_file_path in index_file_list:
                work(index_file_path)
    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)


if __name__ == "__main__":
    main()
