import pandas as pd
import datetime as dt
import os
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
    if not(df.empty):
        if "Vintage" in df.columns:
            df["Vintage"] = pd.to_datetime(
                df["Vintage"], unit='s').dt.tz_localize(None).dt.year
        df["Date"] = pd.to_datetime(df["Date"], unit='s').dt.tz_localize(
            None).dt.floor('D').dt.date
        datelist = pd.date_range(start=df["Date"].min()+pd.DateOffset(-1),
                                 end=pd.to_datetime('today'), freq='d')
        df_date = pd.DataFrame()
        df_date["Date_continous"] = datelist
        df_date["Date_continous"] = pd.to_datetime(df_date["Date_continous"],  unit='s').dt.tz_localize(
            None).dt.floor('D').dt.date
        df = df.merge(df_date, how='right', left_on='Date',
                      right_on='Date_continous').reset_index(drop=True)
        df["Date"] = df["Date_continous"]
        for i in df.columns:
            if "Quantity" in i:
                df[i] = df[i].fillna(0)
            else:
                df[i] = df[i].fillna("missing")
                df[i] = df[i].replace("", "missing")
    return df


def date_manipulations_verra(df):
    if not(df.empty):
        df["Date"] = pd.to_datetime(df["Date"], unit='s').dt.tz_localize(
            None).dt.floor('D').dt.date
        datelist = pd.date_range(start=df["Date"].min()+pd.DateOffset(-1),
                                 end=pd.to_datetime('today'), freq='d')
        df_date = pd.DataFrame()
        df_date["Date_continous"] = datelist
        df_date["Date_continous"] = pd.to_datetime(df_date["Date_continous"],  unit='s').dt.tz_localize(
            None).dt.floor('D').dt.date
        df = df.merge(df_date, how='right', left_on='Date',
                      right_on='Date_continous').reset_index(drop=True)
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
    df_verra = df_verra.drop_duplicates(
        subset=['ID']).reset_index(drop=True)
    for i in drop_columns:
        if i in df.columns:
            df = df.drop(columns=i)
    df = df.merge(df_verra, how='left', left_on="Project ID Key",
                  right_on='ID', suffixes=('', '_Verra'))

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
    sd_pool = df[(df["Date"] <= current_time.date()) &
                 (df["Date"] > seven_day_start.date())]
    last_sd_pool = df[(df["Date"] <= seven_day_start.date())
                      & (df["Date"] > last_seven_day_start.date())]
    # # Thirty day pool subsets
    td_pool = df[(df["Date"] <= current_time.date()) &
                 (df["Date"] > thirty_day_start.date())]
    last_td_pool = df[(df["Date"] <= thirty_day_start.date())
                      & (df["Date"] > last_thirty_day_start.date())]

    return sd_pool, last_sd_pool, td_pool, last_td_pool


def filter_df_by_pool(df, pool_address):
    df["Pool"] = df["Pool"].str.lower()
    df = df[(df["Pool"] == pool_address)].reset_index()
    return df


def verra_manipulations(df_verra):
    df_verra['Vintage'] = df_verra['Vintage Start']
    df_verra['Vintage'] = pd.to_datetime(
        df_verra["Vintage Start"]).dt.tz_localize(None).dt.year
    df_verra['Quantity'] = df_verra['Quantity Issued']
    df_verra['Retirement/Cancellation Date'] = pd.to_datetime(
        df_verra['Retirement/Cancellation Date'])
    df_verra['Date'] = df_verra['Retirement/Cancellation Date']
    df_verra.loc[df_verra['Retirement Details'].str.contains(
        'TOUCAN').fillna(False), 'Toucan'] = True
    df_verra['Toucan'] = df_verra['Toucan'].fillna(False)
    df_verra.loc[df_verra['Retirement Details'].str.contains(
        'C3T').fillna(False), 'C3'] = True
    df_verra['C3'] = df_verra['C3'].fillna(False)
    df_verra_c3 = df_verra.query('C3')
    df_verra_toucan = df_verra.query('Toucan')
    return df_verra, df_verra_toucan, df_verra_c3


def verra_retired(df_verra, df_bridged_mco2):
    df_verra['Issuance Date'] = pd.to_datetime(df_verra['Issuance Date'])
    df_verra['Retirement/Cancellation Date'] = pd.to_datetime(
        df_verra['Retirement/Cancellation Date'])
    df_verra['Days to Retirement'] = (
        df_verra['Retirement/Cancellation Date'] - df_verra['Issuance Date']).dt.days
    df_verra.loc[df_verra['Days to Retirement'] > 0, 'Status'] = 'Retired'
    df_verra['Status'] = df_verra['Status'].fillna('Available')
    lst_sn = list(df_bridged_mco2['Serial Number'])
    df_verra.loc[df_verra['Serial Number'].isin(lst_sn), 'Moss'] = True
    df_verra['Moss'] = df_verra['Moss'].fillna(False)
    df_verra_retired = df_verra.query('~Toucan & ~C3 & ~Moss')
    df_verra_retired = df_verra_retired[df_verra_retired['Status'] == 'Retired']
    df_verra_retired = df_verra_retired.reset_index(drop=True)
    return df_verra_retired


def mco2_verra_manipulations(df_mco2_bridged):
    df_mco2_bridged = df_mco2_bridged[df_mco2_bridged['Project ID'] != 'missing']
    df_mco2_bridged["Quantity"] = df_mco2_bridged["Quantity"].astype(int)
    pat = r'VCS-(?P<id>\d+)'
    repl = (
        lambda m: '[VCS-' + m.group(
            'id') + '](https://registry.verra.org/app/projectDetail/VCS/' + m.group('id') + ')')
    df_mco2_bridged['Project ID'] = df_mco2_bridged['Project ID'].astype(str).str.replace(
        pat, repl, regex=True)
    return df_mco2_bridged


def filter_carbon_pool(pool_address, *dfs):
    filtered = []
    for df in dfs:
        filtered.append(filter_df_by_pool(df, pool_address))

    return filtered


def filter_pool_quantity(df, quantity_column):
    filtered = df[df[quantity_column] > 0]
    filtered["Quantity"] = filtered[quantity_column]
    filtered = filtered[[
        'Project ID', 'Vintage', 'Quantity', 'Country', 'Name', 'Project Type',
        'Methodology', 'Token Address'
    ]]
    pat = r'VCS-(?P<id>\d+)'
    repl = (
        lambda m: '[VCS-' + m.group(
            'id') + '](https://registry.verra.org/app/projectDetail/VCS/' + m.group('id') + ')'
    )
    filtered['Project ID'] = filtered['Project ID'].str.replace(
        pat, repl, regex=True)

    filtered['Token Address'] = filtered['Token Address'].str.replace(
        '(.*)',
        lambda m: '[' + m.group(0) +
        '](https://polygonscan.com/address/' + m.group(0) + ')'
    )

    return filtered


def read_csv(filename):
    '''READ a csv file from the 'data' folder'''
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, 'data')
    df = pd.read_csv(os.path.join(file_dir, filename), thousands=',')

    return df


def to_csv(df, filename):
    '''Write a dataframe to a csv file in 'data' folder'''
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, 'data')
    df.to_csv(os.path.join(file_dir, filename), escapechar='\\')


def dump_to_json(data, filename):
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, 'data')
    with open(os.path.join(file_dir, filename), 'w') as outfile:
        json_string = json.dumps(data)
        json.dump(json_string, outfile)


def read_from_json(filename):
    script_dir = os.path.dirname(__file__)
    file_dir = os.path.join(script_dir, 'data')
    with open(os.path.join(file_dir, filename)) as json_file:
        data = json.load(json_file)
        data = json.loads(data)
    return data


def adjust_mco2_bridges(df, df_tx):
    df_tx = df_tx[['Date', 'Tx Address']]
    df = df.merge(df_tx, how='left', left_on='Original Tx Address',
                  right_on='Tx Address', suffixes=('', '_new')).reset_index(drop=True)
    df.loc[df["Original Tx Address"] != '0x0000000000000000000000000000000000000000000000000000000000000000', 'Date'] \
        = df.loc[df["Original Tx Address"] !=
                 '0x0000000000000000000000000000000000000000000000000000000000000000', 'Date_new']
    df = df.drop(columns=['Tx Address', 'Date_new'])
    return df
