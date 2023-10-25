import requests
import sys

BASE_URL = sys.argv[1]
paths = [
    "credits/raw",
    "credits/raw?status=bridged",
    "credits/agg",
    "credits/agg/daily",
    "credits/agg/daily?status=retired&retirement_date_gt=2021-10-30T00:38:28&retirement_date_lt=2022-10-30T00:38:28&sort_by=retirement_date&operator=cumsum",  # noqa
    "credits/agg/monthly",
    "credits/agg/country",
    "credits/agg/projects",
    "credits/agg/methodology",
    "credits/agg/vintage",
    "credits/agg/pool",
    "credits/agg/pool/vintage",
    "credits/agg/pool/methodology",
    "credits/agg/pool/project",
    "credits/agg/pool/daily",
    "credits/agg/pool/monthly",
    "credits/agg/bridge/project",
    "credits/agg/bridge/vintage",
    "credits/agg/bridge/country",
    "pools/raw",
    "pools/agg",
    "pools/agg/daily",
    "pools/agg/daily?pool=ubo&status=redeemed&redeemed_date_gt=2022-09-30T00:38:28&redeemed_date_lt=2022-10-30T00:38:28&sort_by=redeemed_date&sort_order=desc&operator=sum",  # noqa
    "pools/agg/monthly",
    "holders",
    "prices",
    "tokens",
    "carbon_metrics/polygon",
    "carbon_metrics/eth",
    "carbon_metrics/celo",
    "carbon_metrics/all",
    "retirements/all/raw",
    "retirements/all/agg",
    "retirements/all/agg/daily",
    "retirements/all/agg/monthly",
    "retirements/all/agg/beneficiary",
    "retirements/all/agg/origin/daily",
    "retirements/all/agg/origin/monthly",
    "retirements/klima/raw",
    "retirements/klima/agg",
    "retirements/klima/agg/daily",
    "retirements/klima/agg/monthly",
    "retirements/klima/agg/beneficiary",
    "retirements/klima/agg/tokens",
    "retirements/klima/agg/tokens/daily",
    "retirements/klima/agg/tokens/monthly"
]

for path in paths:
    url = f"{BASE_URL}/{path}"
    response = requests.get(url)
    if response.status_code != 200:
        print("---")
        print(response.text)
        print("---")
        print(f"{url} => Failed ({response.status_code})")
        exit(1)
    print(f"{url} => OK")

exit(0)
