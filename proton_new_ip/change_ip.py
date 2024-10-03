import time
from pathlib import Path

import pyautogui
from loguru import logger
from playwright.sync_api import sync_playwright

CUR_DIR = Path(__file__).parent

# Load the image
IMAGE_PATH = CUR_DIR / "btn_fastest.png"


def find_and_click_image(image_path):
    try:
        # Locate the image on the screen
        image_box = pyautogui.locateOnScreen(str(image_path), confidence=0.99)

        if image_box:
            # Move the cursor to the image's right center
            pos_x = image_box.left + image_box.width - 20
            pos_y = image_box.top + image_box.height // 2
            logger.info(f"x: {pos_x}, y: {pos_y}")
            pyautogui.moveTo(x=pos_x, y=pos_y, duration=0.5)

            # Click on the image
            pyautogui.click()
            print(f"Clicked on the image at {image_box}")

            pyautogui.moveTo(x=pos_x, y=pos_y-100, duration=0.5)
        else:
            print("Image not found on the screen")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Repeat every 10 seconds
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        while True:
            try:
                logger.info("Checking ...")
                page.goto(
                    "https://rapidapi.com/search?sortBy%3DByRelevance",
                    timeout=60000,
                )

                # check if ip is blocked
                elem = page.query_selector("span[data-translate=error]")
                if elem is not None and elem.inner_text() == "Error":
                    logger.warning("IP is blocked. Reconnecting VPN ...")
                    # change ip address
                    find_and_click_image(image_path=IMAGE_PATH)
                else:
                    logger.info("Not blocked")
            except Exception as e:
                logger.exception(e)

            time.sleep(10)

        context.close()
        browser.close()


def test():
    for i in range(5):
        logger.info("change ip")
        find_and_click_image(image_path=IMAGE_PATH)


if __name__ == "__main__":
    main()
    # test()
