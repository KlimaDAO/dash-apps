import requests
import sys

BASE_URL = sys.argv[1]
paths = [
    "offsets/raw",
    "offsets/raw?status=bridged",
    "offsets/agg",
    "offsets/agg/daily",
    "offsets/agg/daily?status=retired&retirement_date_gt=2021-10-30T00:38:28&retirement_date_lt=2022-10-30T00:38:28&sort_by=retirement_date&operator=cumsum",  # noqa
    "offsets/agg/monthly",
    "offsets/agg/countries",
    "offsets/agg/projects",
    "offsets/agg/methodologies",
    "offsets/agg/vintage",
    "pools/raw",
    "pools/agg",
    "pools/agg/daily",
    "pools/agg/daily?pool=ubo&status=redeemed&redeemed_date_gt=2022-09-30T00:38:28&redeemed_date_lt=2022-10-30T00:38:28&sort_by=redeemed_date&sort_order=desc&operator=sum",  # noqa
    "pools/agg/monthly",
    "holders",
    "prices",
    "carbon_metrics/polygon",
    "carbon_metrics/eth",
    "carbon_metrics/celo",
    "carbon_metrics/all",
    "retirements/all/raw",
    "retirements/all/agg",
    "retirements/all/agg/daily",
    "retirements/all/agg/monthly",
    "retirements/all/agg/beneficiaries",
    "retirements/klima/raw",
    "retirements/klima/agg",
    "retirements/klima/agg/daily",
    "retirements/klima/agg/monthly",
    "retirements/klima/agg/beneficiaries",
    "retirements/klima/agg/tokens",
    "retirements/klima/agg/tokens/daily",
    "retirements/klima/agg/tokens/monthly"
]

for path in paths:
    url = f"{BASE_URL}/{path}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"{url} => Failed ({response.status_code})")
        print("---")
        print(response.text)
        print("---")
        exit(1)
    print(f"{url} => OK")

exit(0)
