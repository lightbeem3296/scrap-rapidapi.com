import hashlib
import json
import time
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent

CATEGORY_LIST = [
    {"key": "Business", "count": 7243},
    # {"key": "Data", "count": 3194}, # done
    # {"key": "Other", "count": 3114}, # done
    # {"key": "Tools", "count": 3044}, # done
    # {"key": "Advertising", "count": 2011}, # done
    # {"key": "Artificial Intelligence/Machine Learning", "count": 1651}, # done
    # {"key": "News, Media", "count": 1227}, # done
    # {"key": "Finance", "count": 905}, # done
    # {"key": "eCommerce", "count": 852}, # done
    # {"key": "Cybersecurity", "count": 712}, # done
    # {"key": "Sports", "count": 667}, # done
    # {"key": "Entertainment", "count": 656}, # done
    # {"key": "Social", "count": 645}, # done
    # {"key": "Text Analysis", "count": 633}, # done
    # {"key": "Business Software", "count": 592}, # done
    # {"key": "Education", "count": 517}, # done
    # {"key": "Video, Images", "count": 514}, # done
    # {"key": "Location", "count": 507}, # done
    # {"key": "Database", "count": 427}, # done
    # {"key": "Gaming", "count": 402}, # done
    # {"key": "Commerce", "count": 384}, # done
    # {"key": "Communication", "count": 382}, # done
    # {"key": "Financial", "count": 343}, # done
    # {"key": "Media", "count": 341}, # done
    # {"key": "Visual Recognition", "count": 335}, # done
    # {"key": "Email", "count": 308}, # done
    # {"key": "Search", "count": 278},# done
    # {"key": "Travel", "count": 260}, # done
    # {"key": "Music", "count": 242}, # done
    # {"key": "Translation", "count": 232}, # done
    # {"key": "Weather", "count": 232}, # done
    # {"key": "Food", "count": 215}, # done
    # {"key": "Health and Fitness", "count": 152}, # done
    # {"key": "Mapping", "count": 143}, # done
    # {"key": "Transportation", "count": 143}, # done
    # {"key": "Movies", "count": 130}, # done
    # {"key": "SMS", "count": 119}, # done
    # {"key": "Monitoring", "count": 101}, # done
    # {"key": "Science", "count": 95}, # done
    # {"key": "Medical", "count": 94}, # done
    # {"key": "Logistics", "count": 86}, # done
    # {"key": "Payments", "count": 83}, # done
    # {"key": "Cryptography", "count": 78}, # done
    # {"key": "Events", "count": 71}, # done
    # {"key": "Jobs", "count": 65}, # done
    # {"key": "Devices", "count": 64}, # done
    # {"key": "Storage", "count": 52}, # done
    # {"key": "Energy", "count": 48}, # done
    # {"key": "Reward", "count": 15}, # done
]


def calc_md5(data: str) -> str:
    md5 = hashlib.md5()  # noqa: S324
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for category in CATEGORY_LIST:
            key = category["key"]

            output_file_path = CUR_PATH / f"index_category_{calc_md5(key)}.jsonl"
            if output_file_path.exists():
                output_file_path.unlink()

            link = f"https://rapidapi.com/search/{urllib.parse.quote(key, safe="")}?sortBy=ByRelevance"

            try:
                page.goto(link, wait_until="networkidle", timeout=60000)
            except:  # noqa: E722
                pass

            last_link = ""
            while True:
                cards = page.query_selector_all(selector="div.flex.bg-card.flex-col")
                if len(cards) == 0:
                    logger.info("no cards found")
                    break

                last_card = cards[-1]

                new_cards = 0
                with output_file_path.open("a") as output_file:
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
                                "category": key,
                                "link": link,
                                "updated": updated.timestamp(),
                            }
                            line = json.dumps(index)

                            output_file.write(f"{line}\n")
                            new_cards += 1
                        else:
                            break
                last_link = last_card.query_selector("a").get_attribute("href")
                last_card.scroll_into_view_if_needed()
                time.sleep(2)

                if new_cards == 0:
                    logger.info("no more cards")
                    break

        context.close()
        browser.close()


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
