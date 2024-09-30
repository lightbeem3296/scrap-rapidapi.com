import hashlib
import json
import sys
from pathlib import Path

from loguru import logger

CUR_PATH = Path(__file__).parent
OUTPUT_FILE_PATH = CUR_PATH / "index.jsonl"


def calc_md5(data: str) -> str:
    md5 = hashlib.md5()  # noqa: S324
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def main():
    try:
        if len(sys.argv) > 1:
            src_flist = sys.argv[1:]

            index_dict = {}

            for src_fname in src_flist:
                with open(src_fname, "r") as src_file:
                    for line in src_file:
                        api_info = json.loads(line)

                        if "category" in api_info:
                            category = api_info["category"]
                        else:
                            category = ""

                        if "collection" in api_info:
                            collection = api_info["collection"]
                        else:
                            collection = ""

                        link = api_info["link"]

                        updated = api_info["updated"]

                        key = calc_md5(link)

                        if key in index_dict:
                            index_dict[key]["category"] = category
                            index_dict[key]["collection"] = collection
                            index_dict[key]["link"] = link
                            index_dict[key]["updated"] = updated
                        else:
                            index_dict[key] = {
                                "category": category,
                                "collection": collection,
                                "link": link,
                                "updated": updated,
                            }

            with OUTPUT_FILE_PATH.open("w") as output_file:
                json.dump(index_dict, output_file, indent=2, default=str)

    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
