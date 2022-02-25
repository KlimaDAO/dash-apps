from subgrounds.subgrounds import Subgrounds


def get_data():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(
        'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.carbonOffsets(
        orderBy=carbon_data.CarbonOffset.lastUpdate,
        orderDirection='desc',
        first=999
    )

    df_bridged = sg.query_df([
        carbon_offsets.tokenAddress,
        carbon_offsets.region,
        carbon_offsets.vintage,
        carbon_offsets.projectID,
        carbon_offsets.standard,
        carbon_offsets.methodology,
        carbon_offsets.balanceBCT,
        carbon_offsets.balanceNCT,
        carbon_offsets.totalBridged,
        carbon_offsets.bridges.value,
        carbon_offsets.bridges.timestamp
    ])

    carbon_offsets = carbon_data.Query.retires(
        first=999
    )

    df_retired = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.offset.tokenAddress,
        carbon_offsets.offset.region,
        carbon_offsets.offset.vintage,
        carbon_offsets.offset.projectID,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.methodology,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.totalRetired,
    ])

    return df_bridged, df_retired


def get_data_pool():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(
        'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.deposits(
        first=999
    )

    df_deposited = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region,
    ])

    carbon_offsets = carbon_data.Query.redeems(
        first=999
    )

    df_redeemed = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region
    ])

    return df_deposited, df_redeemed
