import pandas as pd
import datetime as dt


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
        return float('inf')
    return change


def add_px_figure(pxfig, layout, row, col):
    for trace in pxfig["data"]:
        layout.append_trace(trace, row=row, col=col)


def drop_duplicates(df):
    df = df.drop_duplicates(subset=['Token Address'], keep='first')
    df = df.reset_index(drop=True)
    return df


def date_manipulations(df):
    df["Date"] = pd.to_datetime(df["Date"], unit='s').dt.tz_localize(
        None).dt.floor('D').dt.date
    if "Vintage" in df.columns:
        df["Vintage"] = pd.to_datetime(
            df["Vintage"], unit='s').dt.tz_localize(None).dt.year
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


def merge_verra(df, df_verra_toucan, merge_columns):
    # Filter dataframe based on bridge
    df["Project ID Key"] = df["Project ID"].str[4:]
    df_verra_toucan = df_verra_toucan[merge_columns]
    df_verra_toucan = df_verra_toucan.drop_duplicates(subset=['ID']).reset_index(drop=True)
    # df_verra = df_verra[(df_verra["Toucan"] is True)
    #                     ].reset_index(drop=True)
    df = df.merge(df_verra_toucan, how='left', left_on="Project ID Key",
                  right_on='ID', suffixes=('', '_Verra'))
    return df


def region_manipulations(df):
    df['Region'] = df['Region'].replace('South Korea', 'Korea, Republic of')
    # Belize country credits are categorized under Latin America. Confirmed this with Verra Registry
    df['Region'] = df['Region'].replace('Latin America', 'Belize')
    df['Region'] = df['Region'].replace('Oceania', 'Indonesia')
    df['Region'] = df['Region'].replace('Asia', 'Cambodia')
    return df


def subsets(df):

    # 7-day, last 7-day, 30-day and last 30 day time
    current_time = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
    seven_day_start = current_time - dt.timedelta(days=7)
    last_seven_day_start = seven_day_start - dt.timedelta(days=7)
    thirty_day_start = current_time - dt.timedelta(days=30)
    last_thirty_day_start = thirty_day_start - dt.timedelta(days=30)

    # Seven day pool subsets
    sd_pool = df[(df["Date"] < current_time.date()) &
                 (df["Date"] >= seven_day_start.date())]
    last_sd_pool = df[(df["Date"] < seven_day_start.date())
                      & (df["Date"] >= last_seven_day_start.date())]
    # # Thirty day pool subsets
    td_pool = df[(df["Date"] < current_time.date()) &
                 (df["Date"] >= thirty_day_start.date())]
    last_td_pool = df[(df["Date"] < thirty_day_start.date())
                      & (df["Date"] >= last_thirty_day_start.date())]

    return sd_pool, last_sd_pool, td_pool, last_td_pool


def filter_carbon_pool(df_deposited, df_redeemed, tokenadddress):
    df_redeemed = df_redeemed[df_redeemed["Pool"]
                              == tokenadddress].reset_index()
    df_deposited = df_deposited[df_deposited["Pool"]
                                == tokenadddress].reset_index()

    return df_deposited, df_redeemed


def verra_manipulations(df_verra):
    df_verra['Vintage'] = pd.to_datetime(
            df_verra["Vintage Start"]).dt.tz_localize(None).dt.year
    df_verra['Quantity'] = df_verra['Quantity Issued']
    df_verra.loc[df_verra['Retirement Details'].str.contains(
        'TOUCAN').fillna(False), 'Toucan'] = True
    df_verra['Toucan'] = df_verra['Toucan'].fillna(False)
    df_verra_toucan = df_verra.query('Toucan')
    return df_verra, df_verra_toucan
