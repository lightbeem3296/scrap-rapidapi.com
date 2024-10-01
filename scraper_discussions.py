import argparse
import ctypes
import json
import os
import time
from http import HTTPStatus
from pathlib import Path

import requests
from loguru import logger

CUR_PATH = Path(__file__).parent
INDEX_DIR = CUR_PATH / "index_category_slug"
OUTPUT_DIR = CUR_PATH / "output"


def fetch_graphql(api_id: str, offset: int, limit: int) -> tuple[list, int]:
    ret = [], 0
    while True:
        try:
            resp = requests.post(
                url="https://rapidapi.com/gateway/graphql",
                headers={
                    "Cookie": 'ajs_anonymous_id=B38083A2-6B71-46C9-BDF8-7A1674C742EB; __cflb=02DiuHPSNb326nZUQB6NoY4qqsJaLefLQ8dxRfMvN878G; _csrf=os5rHJCRUBQja4PTHYpbS5Xd; __stripe_mid=9afab05a-ac7e-4205-97e4-71fcacab74b3bb4f21; g_state={"i_p":1727523321762,"i_l":2}; __stripe_sid=3217535b-6865-4d6a-a8d9-2736e2b5aa4498c46a; cf_clearance=lTYsfmZ.3MArEWXr8SPpwPb9m5yIKz09Cs5lW_0K3us-1727437756-1.2.1.1-_nS6rwrE95dPxzliylwcs5qy185G7kLDmqdRbxcR16zxYJNswD1U1ZEEd7qO3yMAat__5RVkLQkXub_NxmCugXbAHYkVpJ4qPKbIiIkIr7LP8QECpqWkqamfT3aHEZ4s01UudjOaGFWPe9veUIkZ3U0Hxc1yvsZnezJrEMTKnz26XeHraf6gClCPvLvSmE92i5Qf.gegknNizTDEue0HmTUl7pN6GbDFyRnlzQoEdz4en3L0KCXPDvs2F_D5R6exyAdbGwSrHSsxeNijTrrDQGkaJOhO7G3404Um2TdDqZ1AyLD0QZC4vNSEdOWj.7mm9abfiqBJBMnGUqYwYkwF6TQYj.ik4tCGvJ0pwCVLrf2dk4tGN1wU4eqJuUimeeSJ2lZtQejZCXjX6W6poUJU7A; __variation__FFNewModalExperiment=0.24; __variation__FFPostSignupModalMarketplace=0.67; __variation__FFNewHero=0.71; __variation__FFNewOrgCreatePage=0.88; __variation__FFAskCompanyInfo=0.19; __variation__FFEmbedTeamsVideo=0.54; __variation__FFTeamsLandingPageOrgButtonText=0.8; __variation__FFOrgCreationWithUsersInvitaions=0.03; __variation__FFApiPlaygroundABTest=0.68; __variation__FF_SearchInput_PlaceHolder=0.97; __variation__FFSubscribeModalDirectNavToPricing=0.97; __variation__FFNewPricingPage=0.36; __variation__FFPricingPaymentsAdminsInvite=0.43; __variation__FFPricingPersonalNoOrg=0.4; __variation__FFTryItFreeBottomMPTeamsPage=0.21; __variation__FFFastSubscribeToFreePlanOnMarketplace=0.38; __variation__FFNewPaymentPage=0.33; __variation__FFNewMarketplaceHomepageContent=0.07; __variation__FFAPILimitModalExperiment=0.15; jwt_auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OTU5MTMxNywibWFzaGFwZUlkIjoiNjZmNjlkYTYxNTQ4MjAwMDFmZTY4ZTIxIiwib3JpZ2luX3NpdGUiOiJkZWZhdWx0IiwiaXNOZXdVc2VyIjp0cnVlLCJpc0F1dGhlbnRpY2F0ZWRCeVNTTyI6dHJ1ZSwiZW1haWwiOiJhbHBoYTU2MTEzMzFAZ21haWwuY29tIiwid2FzU2Vzc2lvbklzc3VlZCI6dHJ1ZSwiaWF0IjoxNzI3NDM4MjQ2LCJleHAiOjE3MzUyMTQyNDZ9.rIxL7H5k8exh7wvaHDjGkWnWedo1nHh35hFCbjyhJrs; connect.sid=s%3AXwuJJFVWz68Dg6WhHNHU4cy9gSwKuU_C.6banUh8%2Bqg2eBd6LspDO5OfWfNlcozslsgUtxkpgabs; rapidapi-context={%22entityId%22:%229591317%22%2C%22type%22:%22User%22}',
                    "csrf-token": "kqBldmSp-eLiWoIOpnk2DXzCmkYJNeWlBaTM",
                },
                json={
                    "query": "query getIssuesByApiIdsV2($apiIds: [String!], $pagingArgs: PagingArgs, $filters: DiscussionsFilter) {\n  getIssuesByApiIdsV2(apiIds: $apiIds, pagingArgs: $pagingArgs, filters: $filters) {\n    data {\n      id\n      createdAt\n      updatedAt\n      title\n      status\n      rating\n      closed\n      body\n      commentsCount\n      isAnswered\n      comments {\n        top\n        body\n        status\n        rating\n        createdAt\n        isAnswer\n        user {\n          id\n          thumbnail\n          username\n        }\n      }\n      user {\n        id\n        username\n        thumbnail\n      }\n    }\n    total\n  }\n}",
                    "variables": {
                        "apiIds": [
                            api_id,
                        ],
                        "pagingArgs": {
                            "orderBy": "updatedAt",
                            "offset": offset,
                            "limit": limit,
                        },
                        "filters": {"searchTerms": ""},
                    },
                    "operationName": "getIssuesByApiIdsV2",
                },
            )
            if resp.status_code == HTTPStatus.OK:
                resp_json = resp.json()
                ret = (
                    resp_json["data"]["getIssuesByApiIdsV2"]["data"],
                    resp_json["data"]["getIssuesByApiIdsV2"]["total"],
                )
                break
            else:
                logger.warning(f"not 200 ok: {resp.status_code}")
        except Exception as ex:
            logger.exception(ex)

        time.sleep(1)
    return ret


def work(api_info) -> None:
    api_id = api_info["id"]

    output_file_name = f"{api_id}_discuss.json"
    output_file_path = OUTPUT_DIR / output_file_name

    already_done = False
    if output_file_path.exists():
        try:
            with output_file_path.open("r") as file:
                discuss = json.load(file)
                if "total" in discuss:
                    already_done = True
        except:  # noqa: E722
            pass

    if already_done:
        logger.info("already done")
    else:
        discussions = []
        total = 0
        offset = 0
        limit = 1000
        while True:
            resp, total = fetch_graphql(api_id=api_id, offset=offset, limit=limit)
            fetched_count = len(resp)
            logger.info(f"total: {total}, offset: {offset}, fetched: {fetched_count}")

            discussions.extend(resp)
            if total == len(discussions):
                break

            offset += fetched_count

        logger.info(f"saving {len(discussions)} infos into > {output_file_name}")
        with output_file_path.open("w") as output_file:
            json.dump(
                {
                    "total": total,
                    "list": discussions,
                },
                output_file,
                indent=2,
            )


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Process JSONL files from INDEX_DIR."
        )
        parser.add_argument(
            "--start",
            type=int,
            default=0,
            help="Start processing from this index.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=0,
            help="Number of items to process (0 for no limit).",
        )

        args = parser.parse_args()
        start, count = args.start, args.count

        ctypes.windll.kernel32.SetConsoleTitleW(f"start: {start}, count: {count}")

        cursor = 0
        processed = 0
        for dpath, _, fnames in os.walk(INDEX_DIR):
            for fname in fnames:
                if os.path.splitext(fname)[1] != ".jsonl":
                    continue

                logger.info(f"index_file: {fname}")
                fpath = os.path.join(dpath, fname)
                with open(fpath, "r") as index_file:
                    for line in index_file:
                        if cursor < start:
                            cursor += 1
                            continue  # Skip until we reach the start point

                        api_info = json.loads(line)
                        logger.info(
                            f"{cursor} > {api_info['category']} > {api_info['id']}"
                        )
                        work(api_info)
                        cursor += 1
                        processed += 1

                        if count > 0 and processed >= count:
                            return

    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
