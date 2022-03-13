
rename_map = {
    'carbonOffsets_bridges_value': 'Quantity',
    'carbonOffsets_bridges_timestamp': 'Date',
    'carbonOffsets_bridge': 'Bridge',
    'carbonOffsets_region': 'Region',
    'carbonOffsets_vintage': 'Vintage',
    'carbonOffsets_projectID': 'Project ID',
    'carbonOffsets_standard': 'Standard',
    'carbonOffsets_methodology': 'Methodology',
    'carbonOffsets_tokenAddress': 'Token Address',
    'carbonOffsets_balanceBCT': 'BCT Quantity',
    'carbonOffsets_balanceNCT': 'NCT Quantity',
    'carbonOffsets_totalBridged': 'Total Quantity',
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
    'retires_offset_tokenAddress': 'Token Address',
    'retires_offset_totalRetired': 'Total Quantity',
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
