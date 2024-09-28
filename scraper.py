import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INDEXING_LINK = "https://rapidapi.com/search?sortBy%3DByRelevance"
OUTPUT_DIR = CUR_PATH / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOMAIN = "https://rapidapi.com"


def calc_md5(data: str) -> str:
    md5 = hashlib.md5()  # noqa: S324
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def navigate(page, link: str) -> None:
    try:  # noqa: SIM105
        page.goto(link, wait_until="networkidle", timeout=10000)
    except:  # noqa: E722, S110
        pass


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


def scrap_one(page, updated: str, api_link: str) -> bool:
    ret = False
    try:
        logger.info(f"link >> {api_link}")

        output_file_name = calc_md5(api_link) + ".json"
        output_file_path = OUTPUT_DIR / output_file_name
        logger.info(f"file_name >> {output_file_name}")

        already_done = False
        if output_file_path.exists():
            with open(output_file_path) as output_file:
                try:
                    json.load(output_file)
                    already_done = True
                except:  # noqa: E722, S110
                    output_file_path.unlink()

        if already_done:
            logger.info("already done")
        else:
            navigate(page, api_link)

            api_info = {}

            # name
            api_info["name"] = page.query_selector("h1.truncate").inner_text().strip()

            # link
            api_info["link"] = api_link

            elems = page.query_selector_all("div.h-6.items-center.px-1\\.5")
            # popularity
            api_info["popularity"] = (
                elems[0].inner_text().replace("Popularity", "").strip()
            )
            # service-level
            api_info["service_level"] = (
                elems[1].inner_text().replace("Service Level", "").strip()
            )
            # latency
            api_info["latency"] = elems[2].inner_text().replace("Latency", "").strip()
            # test
            api_info["test"] = elems[3].inner_text().replace("Test", "").strip()

            # description
            api_info["description"] = (
                page.query_selector("p.italic.text-muted-foreground")
                .inner_text()
                .strip()
            )

            elems = page.query_selector_all("div.flex.w-full.flex-col.justify-between")
            # creator-name
            api_info["creator_name"] = (
                elems[0]
                .inner_text()
                .replace("API Creator", "")
                .replace("by", "")
                .strip()
            )
            # subscribers
            api_info["subscribers"] = (
                elems[1]
                .inner_text()
                .replace("Subscribers", "")
                .replace("Subs", "")
                .strip()
            )
            # category
            api_info["category"] = elems[2].inner_text().replace("Category", "").strip()
            # website
            api_info["website"] = ""
            if len(elems) >= 4:
                website_elem = elems[3].query_selector("a")
                if website_elem is not None:
                    api_info["website"] = website_elem.get_attribute("href")

            # version
            api_info["version"] = (
                page.query_selector("div.rapid-select__single-value")
                .inner_text()
                .replace("(", "")
                .replace(")", "")
                .replace("current", "")
                .strip()
            )

            # created
            api_info["created"] = ""

            # updated
            api_info["updated"] = datetime.fromtimestamp(updated, UTC)

            # reviewers
            api_info["reviewers"] = (
                page.query_selector("div.text-xs.font-medium")
                .inner_text()
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

            pricing_link = api_link + "/pricing"
            navigate(page, pricing_link)
            cards = page.query_selector_all("div.flex.min-w-\\[256px\\]")
            for card in cards:
                plan, price = get_pricing_price(card)
                api_info[f"pricing_{plan}"] = price

                plan, requests = get_pricing_requests(card)
                api_info[f"pricing_{plan}_requests"] = requests

                plan, features = get_pricing_features(card)
                api_info[f"pricing_{plan}_features"] = features

                plan, rate_limit = get_pricing_rate_limit(card)
                api_info[f"pricing_{plan}_rate_limit"] = rate_limit

            with open(output_file_path, "w") as output_file:  # noqa: PTH123
                json.dump(api_info, output_file, indent=2, default=str)

        ret = True
    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)
    return ret


def work(list_file_path: str) -> None:  # noqa: PLR0915
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False, timeout=60000)
        context = browser.new_context()
        page = context.new_page()

        with open(list_file_path) as list_file:  # noqa: PTH123
            for line in list_file:
                index = json.loads(line)
                api_link = DOMAIN + index["link"]
                api_link = "/".join(api_link.split("/")[:-1])

                while not scrap_one(
                    page=page,
                    updated=index["updated"],
                    api_link=api_link,
                ):
                    pass

        context.close()
        browser.close()


def main() -> None:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-f",
            dest="file",
            required=False,
            default="test_list.jsonl",
            help="API link list file path.",
        )
        args = parser.parse_args()
        work(args.file)
    except Exception as ex:  # noqa: BLE001
        logger.exception(ex)


if __name__ == "__main__":
    main()
