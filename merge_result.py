# drag & drop output folder here

import json
import os
import sys

import pandas as pd
from loguru import logger


def merge(src_dpath: str):
    try:
        if not os.path.isdir(src_dpath):
            print(f"[-] not directory: {src_dpath}")

        dst_dpath = os.path.dirname(src_dpath)
        src_dname = os.path.basename(src_dpath)
        dst_fpath = os.path.join(dst_dpath, f"{src_dname}")

        res_df = pd.DataFrame(
            {
                "id": [],
                "name": [],
                "link": [],
                "popularity": [],
                "service_level": [],
                "latency": [],
                "test": [],
                "category": [],
                "subscribers": [],
                "version": [],
                "description": [],
                "website": [],
                "created": [],
                "updated": [],
                "reviewers": [],
                "creator_name": [],
                "creator_link": [],
                "pricing_basic": [],
                "pricing_basic_requests": [],
                "pricing_basic_features": [],
                "pricing_basic_rate_limit": [],
                "pricing_pro": [],
                "pricing_pro_requests": [],
                "pricing_pro_features": [],
                "pricing_pro_rate_limit": [],
                "pricing_ultra": [],
                "pricing_ultra_requests": [],
                "pricing_ultra_features": [],
                "pricing_ultra_rate_limit": [],
                "pricing_mega": [],
                "pricing_mega_requests": [],
                "pricing_mega_features": [],
                "pricing_mega_rate_limit": [],
                "discussions": [],
                "discussions_answered": [],
                "discussions_avg_msgs": [],
            }
        )

        print(f"[*] merge: {src_dpath} > {dst_fpath}.*")
        file_number = 0
        for dpath, _, fnames in os.walk(src_dpath):
            for fname in fnames:
                if fname.lower().endswith("_discuss.json"):
                    continue

                if fname.lower().endswith(".json"):
                    fpath = os.path.join(dpath, fname)
                    print(f"[*] {file_number} > {fpath[len(src_dpath):]}")

                    discuss_fpath = os.path.join(
                        dpath,
                        fname.replace(".json", "_discuss.json"),
                    )
                    with open(fpath, mode="r") as f:
                        info: dict[str, str] = json.load(f)
                        with open(discuss_fpath, mode="r") as discuss_file:
                            discuss: dict = json.load(discuss_file)

                            info["discussions"] = int(discuss["total"])
                            info["discussions_answered"] = int(0)
                            total_msgs = 0
                            for item in discuss["list"]:
                                if item["isAnswered"]:
                                    info["discussions_answered"] += 1
                                total_msgs += (
                                    item["commentsCount"]
                                    if item["commentsCount"] is not None
                                    else 0
                                )
                            info["discussions_avg_msgs"] = (
                                (total_msgs / discuss["total"])
                                if discuss["total"] != 0
                                else 0
                            )

                            res_df = pd.concat(
                                [res_df, pd.DataFrame([info])],
                                ignore_index=True,
                            )
                    file_number += 1
        res_df.to_csv(dst_fpath + ".csv", index=False)

    except Exception as ex:
        logger.exception(ex)


def main():
    try:
        if len(sys.argv) > 1:
            src_dlist = sys.argv[1:]
            for src_dir in src_dlist:
                merge(src_dir)
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
