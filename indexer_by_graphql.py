import base64
import json
import time
from http import HTTPStatus
from pathlib import Path

import requests
from loguru import logger
from slugify import slugify

CUR_PATH = Path(__file__).parent

SORTING_FLIELDS = [
    "ByAlphabetical",
    "ByRelevance",
    "ByUpdatedAt",
    "ByTrending",
]

SORTING_ORDER = [
    "ASC",
    "DESC",
]

CATEGORY_LIST = [
    {"key": "Business", "count": 7324},
    {"key": "Data", "count": 3195},
    {"key": "Other", "count": 3117},
    {"key": "Tools", "count": 3041},
    {"key": "Advertising", "count": 2022},
    {"key": "Artificial Intelligence/Machine Learning", "count": 1654},
    {"key": "News, Media", "count": 1226},
    {"key": "Finance", "count": 902},
    {"key": "eCommerce", "count": 852},
    {"key": "Cybersecurity", "count": 713},
    {"key": "Sports", "count": 666},
    {"key": "Entertainment", "count": 656},
    {"key": "Social", "count": 645},
    {"key": "Text Analysis", "count": 632},
    {"key": "Business Software", "count": 592},
    {"key": "Education", "count": 517},
    {"key": "Video, Images", "count": 514},
    {"key": "Location", "count": 506},
    {"key": "Database", "count": 427},
    {"key": "Gaming", "count": 402},
    {"key": "Commerce", "count": 384},
    {"key": "Communication", "count": 382},
    {"key": "Financial", "count": 344},
    {"key": "Media", "count": 341},
    {"key": "Visual Recognition", "count": 335},
    {"key": "Email", "count": 309},
    {"key": "Search", "count": 278},
    {"key": "Travel", "count": 260},
    {"key": "Music", "count": 242},
    {"key": "Translation", "count": 232},
    {"key": "Weather", "count": 232},
    {"key": "Food", "count": 215},
    {"key": "Machine Learning", "count": 166},
    {"key": "Health and Fitness", "count": 152},
    {"key": "Mapping", "count": 143},
    {"key": "Transportation", "count": 143},
    {"key": "Movies", "count": 130},
    {"key": "SMS", "count": 119},
    {"key": "Monitoring", "count": 101},
    {"key": "Science", "count": 95},
    {"key": "Medical", "count": 94},
    {"key": "Logistics", "count": 86},
    {"key": "Payments", "count": 83},
    {"key": "Cryptography", "count": 78},
    {"key": "Events", "count": 71},
    {"key": "Jobs", "count": 65},
    {"key": "Devices", "count": 64},
    {"key": "Health, Fitness", "count": 56},
    {"key": "Travel, Transportation", "count": 53},
    {"key": "Storage", "count": 52},
    {"key": "Energy", "count": 48},
    {"key": "Reward", "count": 15},
    {"key": "Other-test category", "count": 1},
]


def fetch_graphql(
    category: str,
    sorting_flield: str,
    sorting_order: str,
    offset: int,
    size: int,
) -> list:
    ret = []
    while True:
        try:
            resp = requests.post(
                url="https://rapidapi.com/gateway/graphql",
                headers={
                    "Cookie": 'ajs_anonymous_id=B38083A2-6B71-46C9-BDF8-7A1674C742EB; __cflb=02DiuHPSNb326nZUQB6NoY4qqsJaLefLQ8dxRfMvN878G; _csrf=os5rHJCRUBQja4PTHYpbS5Xd; __stripe_mid=9afab05a-ac7e-4205-97e4-71fcacab74b3bb4f21; g_state={"i_p":1727523321762,"i_l":2}; __stripe_sid=3217535b-6865-4d6a-a8d9-2736e2b5aa4498c46a; cf_clearance=lTYsfmZ.3MArEWXr8SPpwPb9m5yIKz09Cs5lW_0K3us-1727437756-1.2.1.1-_nS6rwrE95dPxzliylwcs5qy185G7kLDmqdRbxcR16zxYJNswD1U1ZEEd7qO3yMAat__5RVkLQkXub_NxmCugXbAHYkVpJ4qPKbIiIkIr7LP8QECpqWkqamfT3aHEZ4s01UudjOaGFWPe9veUIkZ3U0Hxc1yvsZnezJrEMTKnz26XeHraf6gClCPvLvSmE92i5Qf.gegknNizTDEue0HmTUl7pN6GbDFyRnlzQoEdz4en3L0KCXPDvs2F_D5R6exyAdbGwSrHSsxeNijTrrDQGkaJOhO7G3404Um2TdDqZ1AyLD0QZC4vNSEdOWj.7mm9abfiqBJBMnGUqYwYkwF6TQYj.ik4tCGvJ0pwCVLrf2dk4tGN1wU4eqJuUimeeSJ2lZtQejZCXjX6W6poUJU7A; __variation__FFNewModalExperiment=0.24; __variation__FFPostSignupModalMarketplace=0.67; __variation__FFNewHero=0.71; __variation__FFNewOrgCreatePage=0.88; __variation__FFAskCompanyInfo=0.19; __variation__FFEmbedTeamsVideo=0.54; __variation__FFTeamsLandingPageOrgButtonText=0.8; __variation__FFOrgCreationWithUsersInvitaions=0.03; __variation__FFApiPlaygroundABTest=0.68; __variation__FF_SearchInput_PlaceHolder=0.97; __variation__FFSubscribeModalDirectNavToPricing=0.97; __variation__FFNewPricingPage=0.36; __variation__FFPricingPaymentsAdminsInvite=0.43; __variation__FFPricingPersonalNoOrg=0.4; __variation__FFTryItFreeBottomMPTeamsPage=0.21; __variation__FFFastSubscribeToFreePlanOnMarketplace=0.38; __variation__FFNewPaymentPage=0.33; __variation__FFNewMarketplaceHomepageContent=0.07; __variation__FFAPILimitModalExperiment=0.15; jwt_auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OTU5MTMxNywibWFzaGFwZUlkIjoiNjZmNjlkYTYxNTQ4MjAwMDFmZTY4ZTIxIiwib3JpZ2luX3NpdGUiOiJkZWZhdWx0IiwiaXNOZXdVc2VyIjp0cnVlLCJpc0F1dGhlbnRpY2F0ZWRCeVNTTyI6dHJ1ZSwiZW1haWwiOiJhbHBoYTU2MTEzMzFAZ21haWwuY29tIiwid2FzU2Vzc2lvbklzc3VlZCI6dHJ1ZSwiaWF0IjoxNzI3NDM4MjQ2LCJleHAiOjE3MzUyMTQyNDZ9.rIxL7H5k8exh7wvaHDjGkWnWedo1nHh35hFCbjyhJrs; connect.sid=s%3AXwuJJFVWz68Dg6WhHNHU4cy9gSwKuU_C.6banUh8%2Bqg2eBd6LspDO5OfWfNlcozslsgUtxkpgabs; rapidapi-context={%22entityId%22:%229591317%22%2C%22type%22:%22User%22}',
                    "csrf-token": "kqBldmSp-eLiWoIOpnk2DXzCmkYJNeWlBaTM",
                },
                json={
                    "query": "query searchApis($searchApiWhereInput: SearchApiWhereInput!, $paginationInput: PaginationInput, $searchApiOrderByInput: SearchApiOrderByInput) {\n  products: searchApis(\n    where: $searchApiWhereInput\n    pagination: $paginationInput\n    orderBy: $searchApiOrderByInput\n  ) {\n    nodes {\n      id\n      thumbnail\n      name\n      description\n      slugifiedName\n      pricing\n      updatedAt\n      categoryName\n      isSavedApi\n      title\n      visibility\n      category: categoryName\n      apiCategory {\n        name\n        color\n      }\n      score {\n        popularityScore\n        avgLatency\n        avgServiceLevel\n        avgSuccessRate\n      }\n      version {\n        tags {\n          id\n          status\n          tagdefinition\n          type\n          value\n        }\n      }\n      user: User {\n        id\n        username\n        slugifiedName: username\n        name\n        type\n        parents {\n          id\n          name\n          slugifiedName\n          type\n          thumbnail\n        }\n      }\n    }\n    facets {\n      category {\n        key\n        count\n      }\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      hasPreviousPage\n      startCursor\n    }\n    total\n    queryID\n    replicaIndex\n  }\n}",
                    "variables": {
                        "paginationInput": {
                            "first": size,
                            "after": base64.b64encode(str(offset).encode()).decode(),
                        },
                        "searchApiOrderByInput": {
                            "sortingFields": [
                                {
                                    "fieldName": sorting_flield,
                                    "by": sorting_order,
                                }
                            ]
                        },
                        "searchApiWhereInput": {
                            "privateApisJwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbnZpdGVkQVBJc0lEcyI6e30sImlhdCI6MTcyNzYxMzEwNX0.iQZQWkAXYgmxMHMaawicGrP_1jE7yX_LYqIpR7ULhA0",
                            "term": "",
                            "categoryNames": [category],
                            "tags": [],
                        },
                    },
                    "operationName": "searchApis",
                },
            )
            if resp.status_code == HTTPStatus.OK:
                resp_json = resp.json()
                ret = resp_json["data"]["products"]["nodes"]
                break
            else:
                logger.warning(f"not 200 ok: {resp.status_code}")
        except Exception as ex:
            logger.exception(ex)

        time.sleep(1)
    return ret


def work():
    for category in CATEGORY_LIST:
        category_key = category["key"]

        api_info_dict = {}

        for sorting_field in SORTING_FLIELDS:
            for sorting_order in SORTING_ORDER:
                offset = 0
                while True:
                    page_size = 100

                    logger.info(
                        f"{category_key} > {sorting_field} > {sorting_order} > {offset} > {page_size}"
                    )

                    resp = fetch_graphql(
                        category=category_key,
                        sorting_flield=sorting_field,
                        sorting_order=sorting_order,
                        offset=offset,
                        size=page_size,
                    )
                    fetched_count = len(resp)
                    logger.info(f"fetched: {fetched_count}")
                    if fetched_count == 0:
                        break

                    for api_info in resp:
                        api_info_dict[api_info["id"]] = api_info

                    offset += fetched_count

        output_file_name = f"index_category_{slugify(category_key)}.jsonl"
        logger.info(f"saving {len(api_info_dict)} infos into > {output_file_name}")
        output_file_path = CUR_PATH / output_file_name
        with output_file_path.open("w") as output_file:
            for _, value in api_info_dict.items():
                output_file.write(json.dumps(value) + "\n")


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
