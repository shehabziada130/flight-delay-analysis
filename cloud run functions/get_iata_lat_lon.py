import pandas as pd
import json


airports=pd.read_csv("airports.csv")

MENA_AIRPORTS = {
        # Algeria
        "ALG", "ORN", "CZL",
        # Bahrain
        "BAH",
        # Egypt
        "CAI", "HBE", "HRG", "SSH", "LXR",
        # Iran
        "IKA", "THR", "MHD", "SYZ", "IFN",
        # Iraq
        "BGW", "EBL", "BSR", "ISU", "NJF",
        # Israel
        "TLV", "ETM", "HFA",
        # Jordan
        "AMM", "AQJ", "ADJ",
        # Kuwait
        "KWI",
        # Lebanon
        "BEY",
        # Oman
        "MCT", "SLL", "OHS",
        # Palestine
        "GZA",
        # Qatar
        "DOH",
        # Saudi Arabia
        "JED", "RUH", "DMM", "MED", "AHB",
        # Syria
        "DAM", "ALP", "LTK",
        # Turkey
        "IST", "SAW", "ESB", "AYT", "ADB",
        # United Arab Emirates
        "DXB", "AUH", "SHJ", "DWC", "RKT",
        # Yemen
        "SAH", "ADE", "GXF"
}

def get_longitude_latitude(MENA_AIRPORTS):
    iata_lat_lon={}
    airport_codes=list(MENA_AIRPORTS)
    for code in airport_codes:
        airport_info=airports[airports['iata_code']==code]
        if not airport_info.empty:
            lat=airport_info.iloc[0]['latitude_deg']
            lon=airport_info.iloc[0]['longitude_deg']
        else:
            lat = lon = None
        iata_lat_lon[code] = (lat, lon)
    return iata_lat_lon


json_data = get_longitude_latitude(MENA_AIRPORTS)
with open('iata_lat_lon.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)