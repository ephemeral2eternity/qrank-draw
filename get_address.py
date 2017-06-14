import requests
import json

def get_address_by_coords(lat, lon):
    google_map_api_url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%.4f,%.4f" % (lat, lon)

    rsp = requests.get(google_map_api_url)
    rsts = rsp.json()["results"]

    codes_to_read = ["administrative_area_level_3", "administrative_area_level_2", "administrative_area_level_1"]
    rst_to_read = None
    for rst in rsts:
        if set(codes_to_read) & set(rst["types"]):
            rst_to_read = rst["formatted_address"]
            return rst_to_read

    return rsts[0]["formatted_address"]

if __name__ == '__main__':
    lat = 39.018
    lon = -77.539

    print(get_address_by_coords(lat,lon))
