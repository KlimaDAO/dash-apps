BCT_ADDRESS = '0x2f800db0fdb5223b3c3f354886d907a671414a7f'
NCT_ADDRESS = '0xd838290e877e0188a4a44700463419ed96c16107'
UBO_ADDRESS = '0x2b3ecb0991af0498ece9135bcd04013d7993110c'
NBO_ADDRESS = '0x6bca3b77c1909ce1a4ba1a20d1103bde8d222e48'
GRAY = '#232B2B'
DARK_GRAY = '#343a40'
FIGURE_BG_COLOR = '#202020'
MCO2_ADDRESS = '0xfC98e825A2264D890F9a1e68ed50E1526abCcacD'
MCO2_ADDRESS_MATIC = '0xaa7dbd1598251f856c12f63557a4c4397c253cea'
VERRA_FALLBACK_NOTE = "Note: Off-Chain Verra Registry data is not updated, we are temporarily using fallback data"
KLIMA_RETIRED_NOTE = "Note: This only includes Retired Tonnes coming through the KlimaDAO retirement aggregator tool"
VERRA_FALLBACK_URL = 'https://prod-klimadao-data.nyc3.digitaloceanspaces.com/verra_registry_fallback_data.csv'

rename_map = {
    'carbonOffsets_bridges_value': 'Quantity',
    'carbonOffsets_bridges_timestamp': 'Date',
    'carbonOffsets_bridge': 'Bridge',
    'carbonOffsets_region': 'Region',
    'carbonOffsets_vintage': 'Vintage',
    'carbonOffsets_projectID': 'Project ID',
    'carbonOffsets_standard': 'Standard',
    'carbonOffsets_methodology': 'Methodology',
    'carbonOffsets_country': 'Country',
    'carbonOffsets_category': 'Project Type',
    'carbonOffsets_name': 'Name',
    'carbonOffsets_tokenAddress': 'Token Address',
    'carbonOffsets_balanceBCT': 'BCT Quantity',
    'carbonOffsets_balanceNCT': 'NCT Quantity',
    'carbonOffsets_balanceUBO': 'UBO Quantity',
    'carbonOffsets_balanceNBO': 'NBO Quantity',
    'carbonOffsets_totalBridged': 'Total Quantity',
}

mco2_bridged_rename_map = {
    'batches_id': 'ID',
    'batches_serialNumber': 'Serial Number',
    'batches_timestamp': 'Date',
    'batches_tokenAddress': 'Token Address',
    'batches_vintage': 'Vintage',
    'batches_projectID': 'Project ID',
    'batches_value': 'Quantity',
    'batches_originaltx': 'Original Tx Address',
}

retires_rename_map = {
    'retires_value': 'Quantity',
    'retires_timestamp': 'Date',
    'retires_offset_bridge': 'Bridge',
    'retires_offset_region': 'Region',
    'retires_offset_vintage': 'Vintage',
    'retires_offset_projectID': 'Project ID',
    'retires_offset_standard': 'Standard',
    'retires_offset_methodology': 'Methodology',
    'retires_offset_country': 'Country',
    'retires_offset_category': 'Project Type',
    'retires_offset_name': 'Name',
    'retires_offset_tokenAddress': 'Token Address',
    'retires_offset_totalRetired': 'Total Quantity',
}

bridges_rename_map = {
    'bridges_value': 'Quantity',
    'bridges_timestamp': 'Date',
    'bridges_transaction_id': 'Tx Address',
}


redeems_rename_map = {
    'redeems_value': 'Quantity',
    'redeems_timestamp': 'Date',
    'redeems_pool': 'Pool',
    'redeems_offset_region': 'Region',
}

deposits_rename_map = {
    'deposits_value': 'Quantity',
    'deposits_timestamp': 'Date',
    'deposits_pool': 'Pool',
    'deposits_offset_region': 'Region',
}

pool_retires_rename_map = {
    'klimaRetires_amount': 'Quantity',
    'klimaRetires_timestamp': 'Date',
    'klimaRetires_pool': 'Pool',
}

verra_rename_map = {
    'issuanceDate': 'Issuance Date',
    'programObjectives': 'Sustainable Development Goals',
    'instrumentType': 'Credit Type',
    'vintageStart': 'Vintage Start',
    'vintageEnd': 'Vintage End',
    'reportingPeriodStart': 'Reporting Period Start',
    'reportingPeriodEnd': 'Reporting Period End',
    'resourceIdentifier': 'ID',
    'resourceName': 'Name',
    'region': 'Region',
    'country': 'Country',
    'protocolCategory': 'Project Type',
    'protocol': 'Methodology',
    'totalVintageQuantity': 'Total Vintage Quantity',
    'quantity': 'Quantity Issued',
    'serialNumbers': 'Serial Number',
    'additionalCertifications': 'Additional Certifications',
    'retiredCancelled': 'Is Cancelled',
    'retireOrCancelDate': 'Retirement/Cancellation Date',
    'retirementBeneficiary': 'Retirement Beneficiary',
    'retirementReason': 'Retirement Reason',
    'retirementDetails': 'Retirement Details',
    'inputTypes': 'Input Type',
    'holdingIdentifier': 'Holding ID'
}

merge_columns = ["ID", "Name", "Region", "Country",
                 "Project Type", "Methodology", "Toucan"]


verra_columns = ['Issuance Date', 'Sustainable Development Goals',
                 'Credit Type', 'Vintage Start', 'Vintage End', 'Reporting Period Start', 'Reporting Period End', 'ID',
                 'Name', 'Region', 'Country', 'Project Type', 'Methodology', 'Total Vintage Quantity',
                 'Quantity Issued', 'Serial Number', 'Additional Certifications',
                 'Is Cancelled', 'Retirement/Cancellation Date', 'Retirement Beneficiary', 'Retirement Reason',
                 'Retirement Details', 'Input Type', 'Holding ID']

mco2_verra_rename_map = {
    'Project Name': 'Name',
    'Quantity of Credits': 'Quantity',
}
