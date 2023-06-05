BCT_ADDRESS = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"
NCT_ADDRESS = "0xd838290e877e0188a4a44700463419ed96c16107"
UBO_ADDRESS = "0x2b3ecb0991af0498ece9135bcd04013d7993110c"
NBO_ADDRESS = "0x6bca3b77c1909ce1a4ba1a20d1103bde8d222e48"
GRAY = "#232B2B"
DARK_GRAY = "#343a40"
WHITE = '#FFFFFF'
FIGURE_BG_COLOR = "#202020"
MCO2_ADDRESS = "0xfC98e825A2264D890F9a1e68ed50E1526abCcacD"
MCO2_ADDRESS_MATIC = "0xaa7dbd1598251f856c12f63557a4c4397c253cea"
VERRA_FALLBACK_NOTE = "Note: Off-Chain Verra Registry data is not updated, we are temporarily using fallback data"
KLIMA_RETIRED_NOTE = "Note: This only includes Retired Tonnes coming through the KlimaDAO retirement aggregator tool"
VERRA_FALLBACK_URL = "https://prod-klimadao-data.nyc3.digitaloceanspaces.com/verra_registry_fallback_data.csv"
KLIMA_UBO_ADDRESS = "0x5400a05b8b45eaf9105315b4f2e31f806ab706de"
KLIMA_NBO_ADDRESS = "0x251ca6a70cbd93ccd7039b6b708d4cb9683c266c"
KLIMA_MCO2_ADDRESS = "0x64a3b8ca5a7e406a78e660ae10c7563d9153a739"
KLIMA_BCT_ADDRESS = "0x9803c7ae526049210a1725f7487af26fe2c24614"
BCT_USDC_ADDRESS = "0x1e67124681b402064cd0abe8ed1b5c79d2e02f64"
NCT_USDC_ADDRESS = "0xdb995f975f1bfc3b2157495c47e4efb31196b2ca"
KLIMA_USDC_ADDRESS = "0x5786b267d35F9D011c4750e0B0bA584E1fDbeAD1"

BCT_DECIMALS = 18
C3_DECIMALS = 18
FRAX_DECIMALS = 18
KLIMA_DECIMALS = 9
MCO2_DECIMALS = 18
MOSS_DECIMALS = 18
NBO_DECIMALS = 18
UBO_DECIMALS = 18
NCT_DECIMALS = 18
USDC_DECIMALS = 12

BETWEEN_SECTION_STYLE = {"padding-top": "20px"}

merge_columns = [
    "ID",
    "Name",
    "Region",
    "Country",
    "Project Type",
    "Methodology",
    "Toucan",
]


verra_columns = [
    "Issuance Date",
    "Sustainable Development Goals",
    "Credit Type",
    "Vintage Start",
    "Vintage End",
    "Reporting Period Start",
    "Reporting Period End",
    "ID",
    "Name",
    "Region",
    "Country",
    "Project Type",
    "Methodology",
    "Total Vintage Quantity",
    "Quantity Issued",
    "Serial Number",
    "Additional Certifications",
    "Is Cancelled",
    "Retirement/Cancellation Date",
    "Retirement Beneficiary",
    "Retirement Reason",
    "Retirement Details",
    "Input Type",
    "Holding ID",
]

mco2_verra_rename_map = {
    "Project Name": "Name",
    "Quantity of Credits": "Quantity",
}


GRAPH_FONT = dict(size=8, color="white", family="Inter, sans-serif")
PIE_CHART_FONT = dict(size=12, color="white", family="Inter, sans-serif")
TREEMAP_FONT = dict(size=12, color="white", family="Inter, sans-serif")

MISPRICED_NCT_SWAP_ID = "0xdb995f975f1bfc3b2157495c47e4efb31196b2ca1679432400"
