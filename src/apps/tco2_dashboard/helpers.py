import os
import pandas as pd
import numpy as np
import datetime as dt
import json


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


# def merge_verra_mco2(df, df_verra, merge_columns, drop_columns):
#     # df["Project ID Key"] = df["Project ID"].astype(str).str[4:]
#     df_verra = df_verra[merge_columns]
#     for i in drop_columns:
#         if i in df.columns:
#             df = df.drop(columns=i)
#     df = df.merge(df_verra, how='left', left_on="Serial Number",
#                   right_on='Serial Number', suffixes=('', '_Verra'))
#     return df


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


def verra_retired(df_verra):
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

    # Merge Moss Data (Beneficiary)
    df_retired_eth_merged = df_retired_eth.merge(
        df_retired_moss,
        how="left",
        left_on="Tx ID",
        right_on="Tx ID",
        suffixes=("", "_moss"),
    )
    # Remove retirements made from the Klima wallet
    klima_retire_wallet = "0xedaefcf60e12bd331c092341d5b3d8901c1c05a8"
    df_retired_eth_merged = df_retired_eth_merged[
        df_retired_eth_merged["Retiree_moss"] != klima_retire_wallet
    ]

    # Fallback to the Moss retiree field if the Moss Beneficiary field is empty
    df_retired_eth_merged.loc[
        df_retired_eth_merged["Beneficiary"].isna(),
        "Beneficiary",
    ] = df_retired_eth_merged["Retiree_moss"]

    # Remove rows where we do not know the Beneficiary
    df_retired_eth_merged = df_retired_eth_merged.loc[
        (df_retired_eth_merged["Beneficiary"] != "")
    ]

    # Prettify known beneficiaries
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


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def retirements_all_data_process(retirements_all):
    retirements_all["dailyKlimaRetirements_datetime"] = (
        pd.to_datetime(retirements_all["dailyKlimaRetirements_datetime"])
    )
    retirements_all['month'] = (
        retirements_all['dailyKlimaRetirements_datetime'].dt.month_name()
    )
    retirements_all['year'] = (
        retirements_all["dailyKlimaRetirements_datetime"].dt.year
    )
    retirements_all['year'] = retirements_all['year'].apply(str)
    retirements_all['month_year'] = (
        retirements_all.month.str.cat(retirements_all.year, sep='-')
    )
    retirements_all = retirements_all.drop(
        ['year', 'month', 'dailyKlimaRetirements_datetime'], axis=1
    )
    return retirements_all


def stacked_bar_chart_data_process(retirements_all):

    retirements_sumed = (
        retirements_all.groupby(
            ['month_year', 'dailyKlimaRetirements_token']
        )['dailyKlimaRetirements_amount'].sum().to_frame().reset_index()
    )

    wide_retirements_sumed = (
        pd.pivot(
            retirements_sumed,
            index=['month_year'],
            columns='dailyKlimaRetirements_token',
            values='dailyKlimaRetirements_amount'
            )
    )

    wide_retirements_sumed = wide_retirements_sumed.fillna(0).reset_index()

    wide_retirements_sumed['month_year_dt_formated'] = (
        pd.to_datetime(
            wide_retirements_sumed['month_year']
        ).dt.strftime("%Y%m%d")
    )

    wide_retirements_sumed = wide_retirements_sumed.sort_values(
        ['month_year_dt_formated']
        )

    wrs = wide_retirements_sumed

    totals = wrs['BCT'] + wrs['MCO2'] + wrs['NBO'] + wrs['NCT'] + wrs['UBO']

    totals = (
        totals.to_frame().rename(columns={0: "total_retired"})
    )

    wrs = pd.concat([wrs, totals], axis=1)

    wrs['BCT_%'] = wrs['BCT'] / wrs['total_retired'] * 100
    wrs['MCO2_%'] = wrs['MCO2'] / wrs['total_retired'] * 100
    wrs['NBO_%'] = wrs['NBO'] / wrs['total_retired'] * 100
    wrs['NCT_%'] = wrs['NCT'] / wrs['total_retired'] * 100
    wrs['UBO_%'] = wrs['UBO'] / wrs['total_retired'] * 100

    wrs['month_year_dt'] = pd.to_datetime(
            wide_retirements_sumed['month_year_dt_formated']
        ).dt.strftime("%b-%g")

    if 'Jan-22' in wrs['month_year_dt'].values:
        wrs['month_year_dt'] = np.where(
            wrs.month_year_dt == 'Jan-22',
            'Jan-23',
            wrs.month_year_dt)

    return wrs


def verra_project_id_to_link(df):
    df['Project_num'] = df['Project'].str.split("-", expand=True)[1]
    df["Project"].fillna('N/A', inplace=True)

    verra_l = 'https://registry.verra.org/app/projectDetail/VCS/'

    df['Project_Link'] = verra_l

    df["Project_Link"] = df["Project_Link"] + df["Project_num"]

    missing_condition_1 = df['Project_Link'].str.match(
        'https://registry.verra.org/app/projectDetail/VCS/N/A')

    df['Project_Link'] = np.where(
        missing_condition_1, "N/A",
        "[" + df['Project'] + "]" + "(" + df['Project_Link'] + ")"
        )
    if "Token" in df:
        mco2_condition = df['Token'].str.match('MCO2')
        df['Project_Link'] = np.where(
            mco2_condition, 'N/A', df['Project_Link'])

    df.drop(['Project', 'Project_num'], axis=1, inplace=True)

    df = df.rename(
            columns={
                'Project_Link': "Project"
            }
    )
    return df


def summary_table_data_process(retirements_all):

    monthly_transactions = retirements_all.groupby(
        ['month_year']
        )['dailyKlimaRetirements_id'].count().to_frame().reset_index()

    monthly_transactions.rename(
            columns={'dailyKlimaRetirements_id': 'Number of transactions'},
            inplace=True)

    monthly_total_retired = retirements_all.groupby(
            ['month_year']
            )['dailyKlimaRetirements_amount'].sum().to_frame().reset_index()

    monthly_total_retired.rename(
            columns={'dailyKlimaRetirements_amount': 'Total tonnes retired'},
            inplace=True)

    summary_table = pd.merge(
            monthly_transactions,
            monthly_total_retired,
            left_on=['month_year'],
            right_on=['month_year'],
            how='inner')

    summary_table['Average tonnes per transaction'] = (
            summary_table['Total tonnes retired'] /
            summary_table['Number of transactions']
        )

    summary_table['month_year_dt_format'] = pd.to_datetime(
            summary_table['month_year']).dt.strftime('%Y%m%d')

    summary_table = pd.melt(
            summary_table,
            id_vars=['month_year', 'month_year_dt_format'],
            value_vars=['Number of transactions',
                        'Total tonnes retired',
                        'Average tonnes per transaction']
            )

    summary_table = summary_table.sort_values(['month_year_dt_format'])

    summary_table['value'] = summary_table['value'].astype(int)

    summary_table['value'] = summary_table['value'].apply(
        lambda x: '{0:,}'.format(x))

    summary_table['month_year_dt'] = pd.to_datetime(
            summary_table['month_year_dt_format']
            ).dt.strftime("%b-%g")

    summary_table = pd.pivot(
            summary_table,
            index=['variable'],
            columns=['month_year', 'month_year_dt'],
            values='value'
            )

    summary_table = summary_table.reindex(
        ["Total tonnes retired",
         "Number of transactions",
         "Average tonnes per transaction"])

    summary_table = summary_table.reset_index()

    summary_table.rename(
             columns={'variable': ''},
             inplace=True)

    summary_table.columns = summary_table.columns.droplevel(-2)

    if 'Jan-22' in summary_table.columns:
        summary_table = summary_table.rename(
            columns={'Jan-22': 'Jan-23'})

    return summary_table
