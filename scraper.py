import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INDEXING_LINK = "https://rapidapi.com/search?sortBy%3DByRelevance"
OUTPUT_DIR = CUR_PATH / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOMAIN = "https://rapidapi.com"


def calculate_md5(data: str):
    md5 = hashlib.md5()
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def get_features(card) -> str:
    features = ""
    features_elem = card.query_selector("div.flex.flex-col.gap-3")
    if features_elem is not None:
        if "Features" in features_elem.inner_text():
            feature_elems = features_elem.query_selector_all("div.inline-flex.flex-col")
            for feature_elem in feature_elems:
                if (
                    feature_elem.query_selector("svg").get_attribute("class")
                    == "stroke-green-600"
                ):
                    features += feature_elem.inner_text().replace("\n", " ").strip() + " | "
    features = features.strip(" |")
    return features


def get_requests(card) -> str:
    requests = ""
    elems = card.query_selector_all("div.flex.grow.basis-full.flex-col")
    for elem in elems:
        elem_text = elem.inner_text()
        requests += elem_text.strip().replace("\n", " - ") + " | "
    requests = requests.strip(" |")
    return requests


def get_rate_limit(card) -> str:
    rate_limit = ""
    elems = card.query_selector_all("div.text-xs.font-semibold")
    if len(elems) >= 3:
        rate_limit = elems[2].inner_text().strip()
    return rate_limit


def work(list_file_path: str):
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.route(
            "**/*",
            lambda route, request: route.continue_()
            if request.resource_type not in ["image", "stylesheet"]
            else route.abort(),
        )

        with open(list_file_path, "r") as list_file:
            for line in list_file:
                try:
                    index = json.loads(line)
                    api_link = DOMAIN + index["link"]
                    api_link = "/".join(api_link.split("/")[:-1])
                    logger.info(f"link >> {api_link}")

                    output_file_name = calculate_md5(api_link) + ".json"
                    output_file_path = OUTPUT_DIR / output_file_name
                    logger.info(f"file_name >> {output_file_name}")

                    if output_file_path.exists():
                        with open(output_file_path, "r") as output_file:
                            try:
                                json.load(output_file)
                                logger.info("already done")
                                continue
                            except:  # noqa: E722
                                pass
                        output_file_path.unlink()

                    page.goto(api_link, wait_until="networkidle")

                    api_info = {}

                    # name
                    api_info["name"] = (
                        page.query_selector("h1.truncate").inner_text().strip()
                    )

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
                    api_info["latency"] = (
                        elems[2].inner_text().replace("Latency", "").strip()
                    )
                    # test
                    api_info["test"] = elems[3].inner_text().replace("Test", "").strip()

                    # description
                    api_info["description"] = (
                        page.query_selector("p.italic.text-muted-foreground")
                        .inner_text()
                        .strip()
                    )

                    elems = page.query_selector_all(
                        "div.flex.w-full.flex-col.justify-between"
                    )
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
                    api_info["category"] = (
                        elems[2].inner_text().replace("Category", "").strip()
                    )
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
                    api_info["updated"] = datetime.fromtimestamp(
                        index["updated"], timezone.utc
                    )

                    # reviewers
                    api_info["reviewers"] = (
                        page.query_selector("div.text-xs.font-medium")
                        .inner_text()
                        .replace("(", "")
                        .replace(")", "")
                        .strip()
                    )

                    pricing_link = api_link + "/pricing"
                    page.goto(pricing_link, wait_until="networkidle")
                    cards = page.query_selector_all("div.flex.min-w-\\[256px\\]")
                    # pricing-basic
                    api_info["pricing_basic"] = (
                        cards[0]
                        .query_selector_all("div.inline-flex")[0]
                        .inner_text()
                        .replace("\n", "")
                        .strip()
                    )
                    # pricing-basic-requests
                    api_info["pricing_basic_requests"] = get_requests(cards[0])
                    # pricing-basic-features
                    api_info["pricing_basic_features"] = get_features(card=cards[0])
                    # pricing-basic-rate-limit
                    api_info["pricing_basic_rate_limit"] = get_rate_limit(cards[0])
                    # pricing-pro
                    api_info["pricing_pro"] = (
                        cards[1]
                        .query_selector_all("div.inline-flex")[0]
                        .inner_text()
                        .replace("\n", "")
                        .strip()
                    )
                    # pricing-pro-requests
                    api_info["pricing_pro_requests"] = get_requests(cards[1])
                    # pricing-pro-features
                    api_info["pricing_pro_features"] = get_features(card=cards[1])
                    # pricing-pro-rate-limit
                    api_info["pricing_pro_rate_limit"] = get_rate_limit(cards[1])
                    # pricing-ultra
                    api_info["pricing_ultra"] = (
                        cards[2]
                        .query_selector_all("div.inline-flex")[0]
                        .inner_text()
                        .replace("\n", "")
                        .strip()
                    )
                    # pricing-ultra-requests
                    api_info["pricing_ultra_requests"] = get_requests(cards[2])
                    # pricing-ultra-features
                    api_info["pricing_ultra_features"] = get_features(card=cards[2])
                    # pricing-ultra-rate-limit
                    api_info["pricing_ultra_rate_limit"] = get_rate_limit(cards[2])
                    # pricing-mega
                    if len(cards) >= 4:
                        api_info["pricing_mega"] = (
                            cards[3]
                            .query_selector_all("div.inline-flex")[0]
                            .inner_text()
                            .replace("\n", "")
                            .strip()
                        )
                        # pricing-mega-requests
                        api_info["pricing_mega_requests"] = get_requests(cards[3])
                        # pricing-mega-features
                        api_info["pricing_mega_features"] = get_features(card=cards[3])
                        # pricing-mega-rate-limit
                        api_info["pricing_mega_rate_limit"] = get_rate_limit(cards[3])

                    with open(output_file_path, "w") as output_file:
                        json.dump(api_info, output_file, indent=2, default=str)
                except Exception as ex:
                    logger.exception(ex)

        context.close()
        browser.close()


def main():
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
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
