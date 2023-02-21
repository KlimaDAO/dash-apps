import pandas as pd
import datetime as dt
import os
import json
from ...util import load_abi
from .constants import (
    BCT_ADDRESS,
    MCO2_ADDRESS,
    NCT_ADDRESS,
    UBO_ADDRESS,
    NBO_ADDRESS,
    KLIMA_USDC_ADDRESS,
    USDC_DECIMALS,
    KLIMA_DECIMALS,
)
from io import StringIO
import boto3
from botocore.client import Config


def pct_change(first, second):
    diff = second - first
    change = 0
    try:
        if diff > 0:
            change = (diff / first) * 100
        elif diff < 0:
            diff = first - second
            change = -((diff / first) * 100)
    except ZeroDivisionError:
        return float("inf")
    return change


def add_px_figure(pxfig, layout, row, col):
    for trace in pxfig["data"]:
        layout.add_trace(trace, row=row, col=col)


def drop_duplicates(df):
    df = df.drop_duplicates(subset=["Token Address"], keep="first")
    df = df.reset_index(drop=True)
    return df


def date_manipulations(df):
    if not (df.empty):
        if "Vintage" in df.columns:
            df["Vintage"] = (
                pd.to_datetime(df["Vintage"], unit="s").dt.tz_localize(None).dt.year
            )
        df["Date"] = (
            pd.to_datetime(df["Date"], unit="s")
            .dt.tz_localize(None)
            .dt.floor("D")
            .dt.date
        )
        datelist = pd.date_range(
            start=df["Date"].min() + pd.DateOffset(-1),
            end=pd.to_datetime("today"),
            freq="d",
        )
        df_date = pd.DataFrame()
        df_date["Date_continous"] = datelist
        df_date["Date_continous"] = (
            pd.to_datetime(df_date["Date_continous"], unit="s")
            .dt.tz_localize(None)
            .dt.floor("D")
            .dt.date
        )
        df = df.merge(
            df_date, how="right", left_on="Date", right_on="Date_continous"
        ).reset_index(drop=True)
        df["Date"] = df["Date_continous"]
        for i in df.columns:
            if "Quantity" in i:
                df[i] = df[i].fillna(0)
            else:
                df[i] = df[i].fillna("missing")
                df[i] = df[i].replace("", "missing")
    return df


def date_manipulations_verra(df):
    if not (df.empty):
        df["Date"] = (
            pd.to_datetime(df["Date"], unit="s")
            .dt.tz_localize(None)
            .dt.floor("D")
            .dt.date
        )
        datelist = pd.date_range(
            start=df["Date"].min() + pd.DateOffset(-1),
            end=pd.to_datetime("today"),
            freq="d",
        )
        df_date = pd.DataFrame()
        df_date["Date_continous"] = datelist
        df_date["Date_continous"] = (
            pd.to_datetime(df_date["Date_continous"], unit="s")
            .dt.tz_localize(None)
            .dt.floor("D")
            .dt.date
        )
        df = df.merge(
            df_date, how="right", left_on="Date", right_on="Date_continous"
        ).reset_index(drop=True)
        df["Date"] = df["Date_continous"]
        for i in df.columns:
            if "Quantity" in i:
                df[i] = df[i].fillna(0)
            else:
                df[i] = df[i].fillna("missing")
                df[i] = df[i].replace("", "missing")
    return df


def black_list_manipulations(df):
    # Dropping rows where Region = "", these tokenized carbon credits are black-listed
    # Black listed because their methodology = "AM0001"
    df = df[df["Region"] != ""].reset_index()
    return df


def bridge_manipulations(df, bridge):
    # Filter dataframe based on bridge
    df = df[df["Bridge"] == bridge].reset_index()
    return df


def merge_verra(df, df_verra, merge_columns, drop_columns):
    df["Project ID Key"] = df["Project ID"].astype(str).str[4:]
    df_verra["ID"] = df_verra["ID"].astype(str)
    df_verra = df_verra[merge_columns]
    df_verra = df_verra.drop_duplicates(subset=["ID"]).reset_index(drop=True)
    for i in drop_columns:
        if i in df.columns:
            df = df.drop(columns=i)
    df = df.merge(
        df_verra,
        how="left",
        left_on="Project ID Key",
        right_on="ID",
        suffixes=("", "_Verra"),
    )

    return df


# def merge_verra_mco2(df, df_verra, merge_columns, drop_columns):
#     # df["Project ID Key"] = df["Project ID"].astype(str).str[4:]
#     df_verra = df_verra[merge_columns]
#     for i in drop_columns:
#         if i in df.columns:
#             df = df.drop(columns=i)
#     df = df.merge(df_verra, how='left', left_on="Serial Number",
#                   right_on='Serial Number', suffixes=('', '_Verra'))
#     return df


def region_manipulations(df):
    df["Region"] = df["Region"].replace("South Korea", "Korea, Republic of")
    # Belize country credits are categorized under Latin America. Confirmed this with Verra Registry
    df["Region"] = df["Region"].replace("Latin America", "Belize")
    df["Region"] = df["Region"].replace("Oceania", "Indonesia")
    df["Region"] = df["Region"].replace("Asia", "Cambodia")
    return df


def subsets(df):

    # 7-day, last 7-day, 30-day and last 30 day time
    current_time = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
    seven_day_start = current_time - dt.timedelta(days=7)
    last_seven_day_start = seven_day_start - dt.timedelta(days=7)
    thirty_day_start = current_time - dt.timedelta(days=30)
    last_thirty_day_start = thirty_day_start - dt.timedelta(days=30)

    # Seven day pool subsets
    sd_pool = df[
        (df["Date"] <= current_time.date()) & (df["Date"] > seven_day_start.date())
    ]
    last_sd_pool = df[
        (df["Date"] <= seven_day_start.date())
        & (df["Date"] > last_seven_day_start.date())
    ]
    # # Thirty day pool subsets
    td_pool = df[
        (df["Date"] <= current_time.date()) & (df["Date"] > thirty_day_start.date())
    ]
    last_td_pool = df[
        (df["Date"] <= thirty_day_start.date())
        & (df["Date"] > last_thirty_day_start.date())
    ]

    return sd_pool, last_sd_pool, td_pool, last_td_pool


def filter_df_by_pool(df, pool_address):
    df["Pool"] = df["Pool"].str.lower()
    df = df[(df["Pool"] == pool_address)].reset_index()
    return df


def verra_manipulations(df_verra):
    df_verra["Vintage"] = df_verra["Vintage Start"]
    df_verra["Vintage"] = (
        pd.to_datetime(df_verra["Vintage Start"]).dt.tz_localize(None).dt.year
    )
    df_verra["Quantity"] = df_verra["Quantity Issued"]
    df_verra["Retirement/Cancellation Date"] = pd.to_datetime(
        df_verra["Retirement/Cancellation Date"]
    )
    df_verra["Date"] = df_verra["Retirement/Cancellation Date"]
    df_verra.loc[
        df_verra["Retirement Details"].str.contains("TOUCAN").fillna(False), "Toucan"
    ] = True
    df_verra["Toucan"] = df_verra["Toucan"].fillna(False)
    df_verra.loc[
        df_verra["Retirement Details"].str.contains("C3T").fillna(False), "C3"
    ] = True
    df_verra["C3"] = df_verra["C3"].fillna(False)
    df_verra_c3 = df_verra.query("C3")
    df_verra_toucan = df_verra.query("Toucan")
    return df_verra, df_verra_toucan, df_verra_c3


def verra_retired(df_verra, df_bridged_mco2):
    df_verra["Issuance Date"] = pd.to_datetime(df_verra["Issuance Date"])
    df_verra["Retirement/Cancellation Date"] = pd.to_datetime(
        df_verra["Retirement/Cancellation Date"]
    )
    df_verra["Days to Retirement"] = (
        df_verra["Retirement/Cancellation Date"] - df_verra["Issuance Date"]
    ).dt.days
    df_verra.loc[df_verra["Days to Retirement"] > 0, "Status"] = "Retired"
    df_verra["Status"] = df_verra["Status"].fillna("Available")
    lst_sn = list(df_bridged_mco2["Serial Number"])
    df_verra.loc[df_verra["Serial Number"].isin(lst_sn), "Moss"] = True
    df_verra["Moss"] = df_verra["Moss"].fillna(False)
    df_verra_retired = df_verra.query("~Toucan & ~C3 & ~Moss")
    df_verra_retired = df_verra_retired[df_verra_retired["Status"] == "Retired"]
    df_verra_retired = df_verra_retired.reset_index(drop=True)
    return df_verra_retired


def mco2_verra_manipulations(df_mco2_bridged):
    df_mco2_bridged = df_mco2_bridged[df_mco2_bridged["Project ID"] != "missing"]
    df_mco2_bridged["Quantity"] = df_mco2_bridged["Quantity"].astype(int)
    pat = r"VCS-(?P<id>\d+)"
    repl = (
        lambda m: "[VCS-"
        + m.group("id")
        + "](https://registry.verra.org/app/projectDetail/VCS/"
        + m.group("id")
        + ")"
    )
    df_mco2_bridged["Project ID"] = (
        df_mco2_bridged["Project ID"].astype(str).str.replace(pat, repl, regex=True)
    )
    return df_mco2_bridged


def filter_carbon_pool(pool_address, *dfs):
    filtered = []
    for df in dfs:
        filtered.append(filter_df_by_pool(df, pool_address))

    return filtered


def filter_pool_quantity(df, quantity_column):
    filtered = df[df[quantity_column] > 0]
    filtered["Quantity"] = filtered[quantity_column]
    filtered = filtered[
        [
            "Project ID",
            "Vintage",
            "Quantity",
            "Country",
            "Name",
            "Project Type",
            "Methodology",
            "Token Address",
        ]
    ]
    pat = r"VCS-(?P<id>\d+)"
    repl = (
        lambda m: "[VCS-"
        + m.group("id")
        + "](https://registry.verra.org/app/projectDetail/VCS/"
        + m.group("id")
        + ")"
    )
    filtered["Project ID"] = filtered["Project ID"].str.replace(pat, repl, regex=True)
    filtered["View on PolygonScan"] = (
        "["
        + "Click Here"
        + "](https://polygonscan.com/address/"
        + filtered["Token Address"]
        + ")"
    )
    filtered = filtered[
        [
            "Project ID",
            "Token Address",
            "View on PolygonScan",
            "Quantity",
            "Vintage",
            "Country",
            "Project Type",
            "Methodology",
            "Name",
        ]
    ].reset_index(drop=True)
    return filtered


def read_csv(filename):
    """READ a csv file from the 'data' folder"""
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, "data")
    df = pd.read_csv(os.path.join(file_dir, filename), thousands=",")

    return df


def to_csv(df, filename):
    """Write a dataframe to a csv file in 'data' folder"""
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, "data")
    df.to_csv(os.path.join(file_dir, filename), escapechar="\\")


def dump_to_json(data, filename):
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, "data")
    with open(os.path.join(file_dir, filename), "w") as outfile:
        json_string = json.dumps(data)
        json.dump(json_string, outfile)


def read_from_json(filename):
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, "data")
    with open(os.path.join(file_dir, filename)) as json_file:
        data = json.load(json_file)
        data = json.loads(data)
    return data


def adjust_mco2_bridges(df, df_tx):
    df_tx = df_tx[["Date", "Tx Address"]]
    df = df.merge(
        df_tx,
        how="left",
        left_on="Original Tx Address",
        right_on="Tx Address",
        suffixes=("", "_new"),
    ).reset_index(drop=True)
    df.loc[
        df["Original Tx Address"]
        != "0x0000000000000000000000000000000000000000000000000000000000000000",
        "Date",
    ] = df.loc[
        df["Original Tx Address"]
        != "0x0000000000000000000000000000000000000000000000000000000000000000",
        "Date_new",
    ]
    df = df.drop(columns=["Tx Address", "Date_new"])
    return df


def group_data_monthly(i):
    i = i[["Date", "Quantity"]]
    i["Date"] = pd.to_datetime(i["Date"]).dt.to_period("m")
    i = i.groupby("Date")["Quantity"].sum().to_frame().reset_index()
    i = i.sort_values(by="Date", ascending=True)
    i["Quantity"] = i["Quantity"].cumsum()
    return i


def off_vs_on_data(df_verra, df_verra_retired, bridges_info_dict, retires_info_dict):
    bridge_df = pd.concat(
        [i["Dataframe"][["Date", "Quantity"]] for i in bridges_info_dict.values()]
    )
    retire_df = pd.concat(
        [i["Dataframe"][["Date", "Quantity"]] for i in retires_info_dict.values()]
    )
    df_verra = group_data_monthly(df_verra)
    bridge_df = group_data_monthly(bridge_df)
    df_verra_retired = group_data_monthly(df_verra_retired)
    retire_df = group_data_monthly(retire_df)

    df_verra = df_verra.merge(
        bridge_df,
        how="left",
        left_on="Date",
        right_on="Date",
        suffixes=("", "_onchain"),
    ).reset_index(drop=True)
    df_verra["Quantity_onchain"] = df_verra["Quantity_onchain"].fillna(0)
    df_verra["Quantity"] = df_verra["Quantity"] - df_verra["Quantity_onchain"]
    return df_verra, df_verra_retired, bridge_df, retire_df


def merge_retirements_data_for_retirement_chart(
    df_retired_polygon, df_klima_agg_retired, df_retired_eth, df_retired_moss
):

    df_retired_polygon = df_retired_polygon[df_retired_polygon["Quantity"] > 0]
    df_klima_agg_retired = df_klima_agg_retired[df_klima_agg_retired["Quantity"] > 0]
    df_retired_eth = df_retired_eth[df_retired_eth["Quantity"] > 0]
    df_retired_moss = df_retired_moss[df_retired_moss["Quantity"] > 0]

    df_retired_polygon["Quantity"] = df_retired_polygon["Quantity"].round(4)
    df_klima_agg_retired["Quantity"] = df_klima_agg_retired["Quantity"].round(4)
    df_retired_polygon["Key"] = (
        df_retired_polygon["Quantity"].astype(str) + "_" + df_retired_polygon["Tx ID"]
    )
    df_klima_agg_retired["Key"] = (
        df_klima_agg_retired["Quantity"].astype(str)
        + "_"
        + df_klima_agg_retired["Tx ID"]
    )

    df_retired_polygon_merged = df_retired_polygon.merge(
        df_klima_agg_retired,
        how="outer",
        left_on="Key",
        right_on="Key",
        suffixes=("", "_klima_agg"),
    )
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    df_retired_polygon_merged.loc[
        df_retired_polygon_merged["Beneficiary"].isna(),
        "Beneficiary",
    ] = df_retired_polygon_merged["Tx From Address"]
    df_retired_polygon_merged.loc[
        df_retired_polygon_merged["Beneficiary"].str.contains("Polygon", case=False),
        "Beneficiary",
    ] = "Polygon"

    df_retired_polygon_merged.loc[
        df_retired_polygon_merged["Quantity"].isna(),
        "Quantity",
    ] = df_retired_polygon_merged["Quantity_klima_agg"]

    df_retired_polygon_merged.loc[
        df_retired_polygon_merged["Beneficiary"].str.contains("Polygon", case=False),
        "Beneficiary",
    ] = "Polygon"

    df_retired_polygon_merged = df_retired_polygon_merged.sort_values(
        by="Quantity", ascending=False
    ).reset_index()

    df_retired_eth_merged = df_retired_eth.merge(
        df_retired_moss,
        how="left",
        left_on="Tx ID",
        right_on="Tx ID",
        suffixes=("", "_moss"),
    )

    df_retired_eth_merged["Beneficiary"] = df_retired_eth_merged["Retiree_moss"]
    moss_corporate_wallet_list = [
        "0x3424b93bda014d41b828f6b31ef08134f983a8fc",
        "0x70d5eadcb367bcf733fc98b441def1c7c5eec187",
        "0x225e489114291d74bd3960e3e5383e523ce8a462",
    ]
    klima_retire_wallet = "0xedaefcf60e12bd331c092341d5b3d8901c1c05a8"
    df_retired_eth_merged = df_retired_eth_merged[
        df_retired_eth_merged["Retiree_moss"] != klima_retire_wallet
    ]
    df_retired_eth_merged.loc[
        df_retired_eth_merged["Retiree_moss"].isin(moss_corporate_wallet_list),
        "Beneficiary",
    ] = df_retired_eth_merged["Receipt ID"]
    df_retired_eth_merged = df_retired_eth_merged.loc[
        (df_retired_eth_merged["Beneficiary"].notna())
    ]
    df_retired_eth_merged.loc[
        df_retired_eth_merged["Beneficiary"].str.contains("ifood|IFOOD", case=False),
        "Beneficiary",
    ] = "iFood"
    df_retired_eth_merged.loc[
        df_retired_eth_merged["Beneficiary"].str.contains("SKYBRIDGE", case=False),
        "Beneficiary",
    ] = "SkyBridge Capital"

    df_retired_eth_merged = df_retired_eth_merged.sort_values(
        by="Quantity", ascending=False
    ).reset_index()

    df_retired_final = pd.concat(
        [
            df_retired_eth_merged[["Quantity", "Beneficiary"]],
            df_retired_polygon_merged[["Quantity", "Beneficiary"]],
        ]
    ).reset_index()

    return df_retired_final


def create_retirements_data(df_retired):
    df_retired = (
        df_retired.groupby("Beneficiary")["Quantity"].sum().to_frame().reset_index()
    )
    df_retired = (
        df_retired.sort_values(by="Quantity", ascending=False).reset_index().head(4)
    )
    data = [{"id": "World", "datum": df_retired["Quantity"].sum(), "children": []}]
    retiree_list = []
    # df_retired["Retiree Name"] = df_retired["Tx From Address"]
    for index, i in enumerate(df_retired["Beneficiary"].tolist()):
        if i[:2] == "0x":
            retiree_list.append(i[:4] + "..." + i[-1])
        else:
            retiree_list.append(i)
    quantity_list = df_retired["Quantity"].tolist()
    dummy_retiree_list = ["..."] * 20
    dummy_quantity_list = [1000] * 20
    retiree_list = retiree_list + dummy_retiree_list
    quantity_list = quantity_list + dummy_quantity_list
    style_dict = {}
    for i in range(len(retiree_list)):
        if i == 0:
            style_dict[retiree_list[i]] = {
                "scale_r": 0.9,
                "alpha": 1,
                "color": "#00CC33",
            }
        elif i == 1:
            style_dict[retiree_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.8,
                "color": "#00CC33",
            }
        elif i == 2:
            style_dict[retiree_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.7,
                "color": "#00CC33",
            }
        elif i == 3:
            style_dict[retiree_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.6,
                "color": "#00CC33",
            }
        else:
            style_dict[retiree_list[i]] = {
                "scale_r": 0.7,
                "alpha": 0.4,
                "color": "#00CC33",
            }
        data[0]["children"].append({"id": retiree_list[i], "datum": quantity_list[i]})

    return df_retired, data, style_dict


def create_holders_data(df_holdings):
    df_holdings["Key"] = df_holdings["Klimate_Address"] + "-" + df_holdings["Token"]
    df_holdings = df_holdings.sort_values(by=["Key", "Date"], ascending=False)
    df_holdings = df_holdings.drop_duplicates(subset=["Key"], keep="first")
    df_holdings = (
        df_holdings.groupby("Klimate_Address")["Quantity"]
        .sum()
        .to_frame()
        .reset_index()
    )
    df_holdings = (
        df_holdings.sort_values(by="Quantity", ascending=False).reset_index().head(4)
    )
    data = [{"id": "World", "datum": df_holdings["Quantity"].sum(), "children": []}]
    holders_list = []
    df_holdings["Klimate Name"] = df_holdings["Klimate_Address"]
    for index, i in enumerate(df_holdings["Klimate_Address"].tolist()):
        if i == "0x7dd4f0b986f032a44f913bf92c9e8b7c17d77ad7":
            holders_list.append("KlimaDAO")
            df_holdings.loc[index, "Klimate Name"] = "KlimaDAO"
        elif i == "0x1e67124681b402064cd0abe8ed1b5c79d2e02f64":
            holders_list.append("Olympus DAO")
            df_holdings.loc[index, "Klimate Name"] = "Olympus DAO"
        else:
            holders_list.append(i[:4] + "..." + i[-1])
    quantity_list = df_holdings["Quantity"].tolist()
    dummy_holders_list = ["..."] * 20
    dummy_quantity_list = [100000] * 20
    holders_list = holders_list + dummy_holders_list
    quantity_list = quantity_list + dummy_quantity_list
    style_dict = {}
    for i in range(len(holders_list)):
        if i == 0:
            style_dict[holders_list[i]] = {
                "scale_r": 0.9,
                "alpha": 1,
                "color": "#00CC33",
            }
        elif i == 1:
            style_dict[holders_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.7,
                "color": "#00CC33",
            }
        elif i == 2:
            style_dict[holders_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.6,
                "color": "#00CC33",
            }
        elif i == 3:
            style_dict[holders_list[i]] = {
                "scale_r": 0.9,
                "alpha": 0.5,
                "color": "#00CC33",
            }
        else:
            style_dict[holders_list[i]] = {
                "scale_r": 0.7,
                "alpha": 0.4,
                "color": "#00CC33",
            }
        data[0]["children"].append({"id": holders_list[i], "datum": quantity_list[i]})

    return df_holdings, data, style_dict


def retirmentManualAdjustments(df_retired):
    # Remove DAO MultiSig Address
    df_retired = df_retired[
        df_retired["Tx From Address"] != "0x693ad12dba5f6e07de86faa21098b691f60a1bea"
    ]

    return df_retired


def get_fee_redeem_factors(token_address, web3):
    if web3 is not None:
        if token_address == BCT_ADDRESS or token_address == NCT_ADDRESS:
            contract = web3.eth.contract(
                address=web3.toChecksumAddress(token_address),
                abi=load_abi("toucanPoolToken.json"),
            )
            feeRedeemDivider = contract.functions.feeRedeemDivider().call()
            feeRedeemFactor = (
                contract.functions.feeRedeemPercentageInBase().call() / feeRedeemDivider
            )
        elif token_address == UBO_ADDRESS or token_address == NBO_ADDRESS:
            contract = web3.eth.contract(
                address=web3.toChecksumAddress(token_address),
                abi=load_abi("c3PoolToken.json"),
            )
            feeRedeemFactor = contract.functions.feeRedeem().call() / 10000
        elif token_address == MCO2_ADDRESS:
            feeRedeemFactor = 0

        return feeRedeemFactor
    else:
        # If web3 is not connected, just return an invalid value
        return -1


def add_fee_redeem_factors_to_dict(token_dict, web3):
    for i in token_dict.keys():
        token_dict[i]["Fee Redeem Factor"] = get_fee_redeem_factors(
            token_dict[i]["Token Address"], web3
        )


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def uni_v2_pool_price(web3, pool_address, decimals, base_price=1):
    """
    Calculate the price of a SushiSwap liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    base_price if provided for computing multiple pool hops.
    """
    uni_v2_abi = load_abi("uni_v2_pool.json")
    pool_contract = web3.eth.contract(address=pool_address, abi=uni_v2_abi)

    reserves = pool_contract.functions.getReserves().call()
    token_price = reserves[0] * base_price * 10**decimals / reserves[1]

    return token_price


def klima_usdc_price(web3):
    return uni_v2_pool_price(web3, KLIMA_USDC_ADDRESS, USDC_DECIMALS - KLIMA_DECIMALS)


def upload_file_to_DO_Space(client, bucket, df, filename):
    buffer = StringIO()
    if "Verra" in filename:
        df.to_json(buffer)
        keyname = f"{filename}.json"
    else:
        df.to_csv(buffer, index=False)
        keyname = f"{filename}.csv"
    print(f"Starting upload of file: {keyname}")
    client.put_object(
        ACL="public-read",
        Bucket=bucket,
        Body=buffer.getvalue(),
        Key=keyname,
    )
    print(f"Upload successful of file: {keyname}")


def download_file_from_DO_Space(endpoint, bucket, filename):
    if "Verra" in filename:
        keyname = f"https://{bucket}.{endpoint[8:]}/{filename}.json"
        print(f"Starting download of file: {keyname}")
        df = pd.read_json(keyname)
    else:
        keyname = f"https://{bucket}.{endpoint[8:]}/{filename}.csv"
        print(f"Starting download of file: {keyname}")
        df = pd.read_csv(keyname)
    print(f"Download successful of file: {keyname}")
    return df


def update_backup_time(client, bucket, filename, endpoint, backup_day, backup_time):
    print(f"Updating Exact Backup Time for Backup Day: {backup_day}")
    df = download_file_from_DO_Space(endpoint, bucket, filename).astype(str)
    df.loc[df["Backup_Day"] == backup_day, "Backup_Time"] = backup_time
    upload_file_to_DO_Space(client, bucket, df, filename)


def get_backup_time(bucket, filename, endpoint, backup_day):
    print(f"Getting Exact Backup Time for Backup Day: {backup_day}")
    df = download_file_from_DO_Space(endpoint, bucket, filename).astype(str)
    backup_time = df.loc[df["Backup_Day"] == backup_day, "Backup_Time"].values[0]
    print(f"Exact Backup Time : {backup_time}")
    return backup_time


def initialize_client_s3(region_name, endpoint_url):
    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=region_name,
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ.get("DO_SPACES_ACCESS_ID"),
        aws_secret_access_key=os.environ.get("DO_SPACES_SECRET_KEY"),
        config=Config(s3={"addressing_style": "virtual"}),
    )
    try:
        client.list_buckets()
        print("Client initialization successful")
    except:
        print("Client initialization failed")
    return client


def calculate_backup_day(backup_data_days_list, curr_day_str):
    for index, day in enumerate(backup_data_days_list):
        if int(curr_day_str) == int(day):
            return day
        elif int(curr_day_str) < int(day):
            return backup_data_days_list[index - 1]
