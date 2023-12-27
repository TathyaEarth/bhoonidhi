import json
import logging
import os
import requests
import time
import urllib

from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

cartosat_list = """CartoSat-2_PAN(SPOT)
CartoSat-2A_PAN(SPOT)
CartoSat-2B_PAN(SPOT)
CartoSat-2C_PAN(SPOT)
CartoSat-2D_PAN(SPOT)
CartoSat-2E_PAN(SPOT)
CartoSat-2F_PAN(SPOT)
CartoSat-3_PAN(SPOT)
CartoSat-1_PAN(MONO)
CartoSat-2C_MX(SPOT)
CartoSat-2D_MX(SPOT)
CartoSat-2E_MX(SPOT)
CartoSat-2F_MX(SPOT)
CartoSat-3_MX(SPOT)
KompSat-3_MS
KompSat-3A_MS"""
resourcesat_list = """ResourceSat-1_LISS4(MONO)
ResourceSat-2_LISS3
ResourceSat-2_LISS4(MONO)
ResourceSat-2_LISS4(MX23)
ResourceSat-2_LISS4(MX70)
ResourceSat-2A_LISS3
ResourceSat-2A_LISS4(MONO)
ResourceSat-2A_LISS4(MX23)
ResourceSat-2A_LISS4(MX70)
LandSat-8_OLI+TIRS_Standard
Sentinel-2A_MSI_Level-1C
Sentinel-2A_MSI_Level-2A
Sentinel-2B_MSI_Level-1C
Sentinel-2B_MSI_Level-2A
ResourceSat-2_AWIFS
ResourceSat-2A_AWIFS"""

othersat_list = """Novasar-1_SAR(All)
Aqua_MODIS
OceanSat-2_OCM
OceanSat-2_OCM_L1B
Terra_MODIS
Sentinel-1A_SAR(IW)_GRD
Sentinel-1B_SAR(IW)_GRD"""

microsat_list = """RISAT-2B_SAR(MOSAIC-3)
RISAT-2B_SAR(STRIP-MAP)
RISAT-2B_SAR(SUPER-STRIP)
RISAT-2B1_SAR(MOSAIC-3)
RISAT-2B1_SAR(STRIP-MAP)
RISAT-2B1_SAR(SUPER-STRIP)
RISAT-2B2_SAR(MOSAIC-3)
RISAT-2B2_SAR(STRIP-MAP)
RISAT-2B2_SAR(SUPER-STRIP)
RISAT-2B_SAR(FINE-SPOT)
RISAT-2B_SAR(MOSAIC-1)
RISAT-2B_SAR(SLIDING-FINE-SPOT10)
RISAT-2B_SAR(SLIDING-FINE-SPOT20)
RISAT-2B_SAR(SLIDING-SPOT-LIGHT10)
RISAT-2B_SAR(SLIDING-SPOT-LIGHT20)
RISAT-2B_SAR(SPOT-LIGHT)
RISAT-2B1_SAR(FINE-SPOT)
RISAT-2B1_SAR(MOSAIC-1)
RISAT-2B1_SAR(SLIDING-FINE-SPOT10)
RISAT-2B1_SAR(SLIDING-FINE-SPOT20)
RISAT-2B1_SAR(SLIDING-SPOT-LIGHT10)
RISAT-2B1_SAR(SLIDING-SPOT-LIGHT20)
RISAT-2B1_SAR(SPOT-LIGHT)
RISAT-2B2_SAR(FINE-SPOT)
RISAT-2B2_SAR(MOSAIC-1)
RISAT-2B2_SAR(SLIDING-FINE-SPOT10)
RISAT-2B2_SAR(SLIDING-FINE-SPOT20)
RISAT-2B2_SAR(SLIDING-SPOT-LIGHT10)
RISAT-2B2_SAR(SLIDING-SPOT-LIGHT20)
RISAT-2B2_SAR(SPOT-LIGHT)
"""


def bhoo_sat(sat_list):
    res = ""
    sat_list = sat_list.split("\n")
    for sat in sat_list:
        res = res + "%2C" + sat
    return res[3:]


def bhoo_date(in_date):
    con_date = (
        datetime.strptime(in_date, "%Y-%m-%d") if isinstance(in_date, str) else in_date
    )
    month = con_date.strftime("%B")
    year = con_date.strftime("%Y")
    date = con_date.strftime("%d")
    return f"{month[:3].upper()}%2F{date}%2F{year}"


class Bhoonidhi:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.get_token()

    def get_token(self):
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/LoginServlet"
        payload = {
            "userId":  os.environ.get('bhoo_username'),
            "password": urllib.parse.quote(os.environ.get('bhoo_password')),
            "oldDB": "false",
            "action": "VALIDATE_LOGIN",
        }
        res = self.session.post(url, json=payload)
        if res.ok:
            result = res.json()
            self.token = result["Results"][0]["JWT"]
            self.user_id = result["Results"][0]["USERID"]
        return res.json()
    
    def download_cart_product(self, product, cart_date):
        """product: Cart Product"""
        server_url = "https://bhoonidhi.nrsc.gov.in/"
        sat = product["SATELLITE"]
        sen = product["SENSOR"] 
        path = product["DIRPATH"].upper()
        prdId = product["ID"]
        sid = product["srt"]
        mon = ""
        if ("NOEDA" in path):
            path = path.replace("//IMGARCHIVE/NOEDAJPG//", "bhoonidhi/data/")
            mon = prdId.split("_")[2][2:4] # Extracting the month from ots id
        else:
            path = path[:-3] #Clipping the date, taking only till month
            path = path.replace("/IMGARCHIVE/PRODUCTJPGS/", "bhoonidhi/data/")
        if (sen == "OLI"):
            path = path.replace("L8/OLI", "L8/O")
            path = path.replace("L9/OLI", "L9/O")
        if (sat == "NVS"):
            path = path.replace("NVS/", "NV/")
        if (sat == "NPP"):
            path = path.replace("NPP/VIR/", "NPP/V/")
        if (sat == "JP1"):
            path = path.replace("JP1/VIR/", "JP1/V/")
        if (sat == "RS2"):
            path = path.replace("RS2/LIS3/", "RS2/3/")
            path = path.replace("RS2/AWIF/", "RS2/W/")
            path = path.replace("RS2/LIS4/", "RS2/F/")
            path = path.replace("RS2/L4FMX/", "RS2/F/")
        if (sat == "R2A"):
            path = path.replace("R2A/LIS3/", "R2A/3/")
            path = path.replace("R2A/AWIF/", "R2A/W/")
            path = path.replace("R2A/LIS4/", "R2A/F/")
            path = path.replace("R2A/L4FMX/", "R2A/F/")
        if (mon != ""):
            path = path + "/" + mon + "/"

        downURL = f"{server_url}{path}{prdId}.zip?token={self.token}&product_id={prdId}"
        if (sat != "NVS" or sen != "A"):
            downURL += f"&cartDate={cart_date.strftime('%d %B %Y')}&sid={sid}"
        start = time.perf_counter()
        res = self.session.get(downURL, stream=True)
        total_length = res.headers.get('content-length')
        dl = 0
        bar_char_length = 50
        with open(f'{prdId}.zip', 'wb') as f:
            if total_length is None: # no content length header
                f.write(res.content)
            else:
                past_done = -1
                for chunk in res.iter_content(1024):
                    dl += len(chunk)
                    f.write(chunk)
                    done = int( bar_char_length * dl / int(total_length))
                    if past_done != done:
                        past_done = done
                        logging.info("\r[%s%s] %s bps" % ('=' * done, ' ' * (bar_char_length-done), dl//(time.perf_counter() - start)))
            logging.info(f"File written successfully at {prdId}.zip in {time.perf_counter() - start} seconds")

    def view_cart(self, date):
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/CartServlet"
        payload = {
            "userId": self.user_id,
            "cartDate": urllib.parse.quote(date.strftime("%d %B %Y")),
            "action": "VIEWCART",
        }
        res = self.session.post(url, json=payload, headers={"Token": self.token})
        if res.ok:
            result = res.json()
            if "Results" in result:
                return result["Results"]
        return []

    def confirm_cart(self):
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/CartServlet"
        payload = {"action": "CONFIRM", "userId": self.user_id, "cartDate": urllib.parse.quote(datetime.now().strftime("%d-%b-%Y").upper())}
        res = self.session.post(url, json=payload, headers={"Token": self.token})
        return res.json()

    @staticmethod
    def get_interface(product):
        subscene_list = ["A", "B", "C", "D", "F", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]
        product_id = product.get("ID", "")
        split_product = product_id.split("_")
        if not product.get("IMAGING_MODE"):
            product["IMAGING_MODE"] = "-"
        if "_" in product_id and product["SATELLITE"] != "O2":
            product["IMAGING_MODE"] = split_product[2] if len(split_product) > 2 else ''
        else:
            product["IMAGING_MODE"] = "-"

        product["SUBSCENE_ID"] = "F"
        temp_sub = split_product[6] if len(split_product) > 6 else ''
        if product["TABLETYPE"] == "PMETA" and len(product_id) == 41:
            temp_sub = product["ID"][40:]
        if temp_sub in subscene_list:  # Assuming `subscene_list` is defined elsewhere
            product["SUBSCENE_ID"] = temp_sub

        sub = "F"
        if "F" not in product["SUBSCENE_ID"] and product["SENSOR"] != 'LIS4':
            sub = "S"
        if (
            (product["SATELLITE"] in ["1C", "1D"])
            and product["SENSOR"] == "PAN"
            and product["SUBSCENE_ID"] in ["A", "B", "C", "D"]
        ):
            sub = "F"

        sat_spec_scheme = "Satellite_Sensor_ImagingMode_Subscene"
        product["SAT_SPEC"] = f"{product['SATELLITE']}_{product['SENSOR']}_{product['IMAGING_MODE']}_{sub}"
        if product["TABLETYPE"] == "PMETA" and product["PRODTYPE"] != "Others":
            product["SAT_SPEC"] += f"_{product['PRODTYPE']}"
            sat_spec_scheme += "_Product"
            if product.get("SATELLITE","").startswith("E06") and product.get("SENSOR").startswith("SCT"):
                product["SAT_SPEC"] += f"_{split_product[len(split_product)-2]}"  # Assuming `sub` is defined elsewhere
                sat_spec_scheme += "_Resolution"
        if product["TABLETYPE"] == "PMETA" and product["SATELLITE"] == "E04":
            product["SAT_SPEC"] += f"_{split_product[9] if len(split_product) > 9 else ''}"
            sat_spec_scheme += "_TxPol"

        scene_spec1 = product["SAT_SPEC"]
        if product["SATELLITE"] in ("NPP", "JP1"):
            scene_spec1 += f"_{product.ID.split('_')[-1]}"
            product["SAT_SPEC"] = scene_spec1

        scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product.get('STRIP_NO')}_{product.get('SCENE_NO')}"
        scene_spec_scheme = "GroundOrbit_Strip_Scene"
        this_sat = product["SATELLITE"]
        if this_sat.startswith("SEN"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['TILE_ID']}"
            scene_spec_scheme = "GroundOrbit_TileID"
        elif this_sat.startswith("GI1"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product.get('STRIP_NO')}"
            scene_spec_scheme = "Orbit_Strip"
        elif this_sat.startswith("E04"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['IMAGING_ORBIT_NO']}_{product.get('STRIP_ID')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_ImagingOrbit_Strip_Scene"
        elif this_sat.startswith("E04"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['IMAGING_ORBIT_NO']}_{product.get('STRIP_ID')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_ImagingOrbit_Strip_Scene"
        elif this_sat.startswith("SC1") and product.get("SENSOR", "").startswith("SCAT"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_Scene"
        elif this_sat.startswith("E06") and product.get("SENSOR", "").startswith("SCT"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_Scene"
        elif this_sat.startswith("G29"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_Scene"
        elif this_sat == "C2":
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['IMAGING_ORBIT_NO']}_{split_product[12] if len(split_product) > 12 else ''}_{product.get('STRIP_NO')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_ImagingOrbit_Segment_Strip_Scene"
        elif this_sat in ("C2A", "C2B", "C2C", "C2D"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['IMAGING_ORBIT_NO']}_{split_product[11] if len(split_product) > 11 else ''}_{product.get('STRIP_NO')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_ImagingOrbit_Session_Strip_Scene"
        elif this_sat in ("C2E", "C2F", "C03"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{split_product[11] if len(split_product) > 11 else ''}_{product.get('STRIP_NO')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_Session_Strip_Scene"
        elif this_sat in ("C2A", "C2B", "C2C", "C2D"):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['IMAGING_ORBIT_NO']}_{split_product[11] if len(split_product) > 11 else ''}_{product.get('STRIP_NO')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_ImagingOrbit_Session_Strip_Scene"
        elif this_sat.startswith("O2") and product.get("SENSOR", "").startswith("SCAT"):
            scene_spec2 = product['GROUND_ORBIT_NO']
            scene_spec_scheme = "GroundOrbit"
        elif this_sat.startswith("O2") and product.get("SENSOR", "").startswith("OCM"):
            scene_spec2 = f"{product.get('PATHNO', '')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "Path_Row"
        elif this_sat.startswith("RS2") and "4x4deg-tiles" in product.get("PRODTYPE", ""):
            scene_spec2 = f"{split_product[6] if len(split_product) > 6 else ''}_{split_product[5] if len(split_product) > 5 else ''}day"
            scene_spec_scheme = "TileID_BinningPeriod"
        elif (this_sat.startswith("O2") or  this_sat.startswith("P6")) and "tiles" in product.get("PRODTYPE", ""):
            scene_spec2 = f"{product_id.split('_')[3]}_{product.get('PATHNO', '')}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "TileID_Path_Row"
        elif any(list(map(lambda x: this_sat.startswith(x), ["RS2", "R2A", "L8", "L9", "P4", "P5", "P6"]))) or (
            this_sat.startswith("O2" and product["SENSOR"].startswith("OCM")) or (
            this_sat.startswith("E06" and product["SENSOR"].startswith("OCM"))) or (
            this_sat.startswith("E06" and product["SENSOR"].startswith("SST")))):
            scene_spec2 = f"{product['GROUND_ORBIT_NO']}_{product['PATHNO']}_{product.get('SCENE_NO')}"
            scene_spec_scheme = "GroundOrbit_Path_Row"
            if product["SENSOR"] == "AWIF" or product["IMAGING_MODE"] in ["FMX", "MN"]:
                scene_spec2 += "_" + product["SUBSCENE_ID"]
                scene_spec_scheme += "_Subscene"
            elif this_sat.startswith("P6") and product["IMAGING_MODE"] in ["SMX"]:
                scene_spec2 += "_" + split_product[13] if len(split_product) > 13 else ''
                scene_spec_scheme += "_StripNo"
            elif (this_sat.startswith("RS2") or this_sat.startswith("R2A")) and product["IMAGING_MODE"] in ["SMX"]:
                scene_spec2 += "_" + split_product[23] if len(split_product) > 23 else ''
                scene_spec_scheme += "_StripNo"
            elif this_sat.startswith("P5") and product["PRODTYPE"] == "CartoDEM-10m":
                scene_spec2 = product_id
                scene_spec_scheme = "TileID"
        elif any(list(map(lambda x: this_sat.startswith(x), ["1A", "1B", "1C", "1D", "L5", "AQ", "TE", "N1"]))):
            scene_spec2 = f'{product["PATHNO"]}_{product["SCENE_NO"]}'
            scene_spec_scheme = "Path_Row"
            if product("SENSOR") in ["AWIF", "LIS4", "LIS2", "PAN"]:
                scene_spec2 += f'_{product["SUBSCENE_ID"]}'
                scene_spec_scheme += "_Subscene"
        if this_sat.startswith("E06") and product.get("SENSOR", "").startswith("OCM"):
            product["SSTM_avail"] = "Y" if product.get("Other_Scene", "") and len(product["Other_Scene"]) > 2 else "N"

        product["SAT_SPEC_SCHEME"] = sat_spec_scheme
        product["SCENE_SPEC"] = scene_spec2
        product["SCENE_SPEC_SCHEME"] = scene_spec_scheme
        product["SCENE_ID"] = product["ID"]

        img_loc = f"{product['DIRPATH']}/{product['FILENAME']}"
        img_loc += ".jpeg" if product["TABLETYPE"] == "SMETA" else ".jpg"
        product["IMG_PATH"] = img_loc
        return product

    
    def add_order(self, product):
        """
        product is json of the product result
        """
        product = self.get_interface(product)
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/OpenOrderCart"
        if "DirectDownload" in product["PRICED"] or "Open_Data" in product["PRICED"]:
            if 'Other_Scene' in product:
                product.pop("Other_Scene")
            payload = {
                "dop": product["DOP"],
                "PROD_ID": product["ID"],
                "PROD_AV": "Y" if product["CURR_SCENE_NO"] == "Y" else "N",
                "srt": product["srt"],
                "action": "ADDTOCART",
                "selProds": json.dumps(product, separators=(',', ':')),
                "userId": self.user_id,
            }
        else:  # "OnOrder" in product["PRICED"]
            if 'Other_Scene' in product:
                product.pop("Other_Scene")
            payload = {
                "sceneID": product["ID"],
                "srt": product["srt"],
                "queryType": product["TABLETYPE"],
                "action": "ADDTOORDERCART",
                "userId": self.user_id,
                "selProds": json.dumps(product, separators=(',', ':')),
                "selOtherProds": "NA",
                "selSats": product["SAT_SPEC"],
                "prod": "Standard"
            }
        for k, v in payload.items():
            payload[k] = urllib.parse.quote(v, safe='')
        print(payload)
        res = self.session.post(url, json=payload, headers={"Token": self.token, 'Origin': 'https://bhoonidhi.nrsc.gov.in',
                                                        'Host': 'bhoonidhi.nrsc.gov.in'})
        return res.json()

    def delete_order(self, product):
        payload = {
            "sceneID": product["ID"],
            "srt": product["srt"],
            "action": "DELETE",
            "userId": self.user_id,    
        }
        for k, v in payload.items():
            payload[k] = urllib.parse.quote(v)
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/OpenOrderCart"
        res = self.session.post(url, json=payload, headers={"Token": self.token})
        return res.json()
        
    def search_bhoo(
        self, lat_lon, start_date=None, end_date=None, sats=resourcesat_list
    ):
        # sat_lists = [resourcesat_list, cartosat_list, othersat_list, microsat_list]
        d1 = bhoo_date(start_date)
        d2 = bhoo_date(end_date)
        sats = sats if isinstance(sats, list) else bhoo_sat(sats)
        thresh = 0.01
        json_to_be_sent = {
            "edate": d2,
            "filters": "%7B%7D",
            "isMX": "No",
            "offset": "0",  # implementing expecting < 500 results on area
            "query": "area",
            "queryType": "polygon",
            "tllat": lat_lon[0] + thresh,
            "tllon": lat_lon[1] - thresh,
            "brlat": lat_lon[0] - thresh,
            "brlon": lat_lon[1] + thresh,
            "prod": "Standard",
            "sdate": d1,
            "selSats": '%2C'.join(sats),
            "userId": self.user_id,
        }
        print(json_to_be_sent)
        logging.info("Searching the products")
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/ProductSearch"
        res = self.session.post(url, json=json_to_be_sent)

        """
        Sample response
        {
            'PRODTYPE': 'Others',
            'CURR_SCENE_NO': 'NA',
            'GROUND_ORBIT_NO': '23473',
            'TABLETYPE': 'SMETA',
            'SEGMENT_NO': '0',
            'CrnSWLon': '77.155',
            'CrnSELat': '15.818',
            'PRICED': 'Priced',
            'PATHNO': '102',
            'CrnSWLat': '16.54',
            'SCENE_NO': '59',
            'ID': 'R2A_AWIF_-_16-JUN-2021_102_59_C_SAN_23473_16-JUN-2021_PLD_23473_1_000_432_SAN_PLD _1_23473_SAN_PLD _1_23473_1',
            'CrnNELat': '19.119',
            'QUALITY_SCORE': '1',
            'FILENAME': 'cbp1020590101003_SAN_awxr2a.16jun2021',
            'CrnNELon': '81.376',
            'SCENE_CENTER_LAT': '17.818',
            'O2_MODE': '-',
            'SCENE_CENTER_LONG': '79.346',
            'SATELLITE': 'R2A',
            'DOP': '16-Jun-2021',
            'CrnSELon': '80.584',
            'CrnNWLat': '19.841',
            'SENSOR': 'AWIF',
            'DIRPATH': '/imgarchive//IRSR2A/AWIF/2021/JUN/16/',
            'srt': '20210617_000006669',
            'IMAGING_ORBIT_NO': '23473',
            'CrnNWLon': '77.881'
            }
        """
        if res.ok:
            results = res.json()["Results"]
            return results
        else:
            print(res.content)
            return []
        
    def dowload_cart(self, cart_date):
        logging.info(f"Checking the cart for {cart_date}")
        cart_items = instance.view_cart(cart_date)
        logging.info(f"Found {len(cart_items)} items")
        # Confirm the Data
        for cart_item in cart_items:
            file_path = cart_item['ID']+'.zip'
            if not os.path.exists(file_path):
                instance.download_cart_product(cart_item, cart_date)
            else:
                logging.info(f"File {file_path} already downloaded")


if __name__ == "__main__":
    instance = Bhoonidhi()
    sats = [
        # "ResourceSat-1_LISS4(MONO)",
        # "ResourceSat-2_LISS3",
        "ResourceSat-2_LISS3_L2",
        # "ResourceSat-2_LISS4(MONO)",
        # "ResourceSat-2_LISS4(MX23)",
        # "ResourceSat-2_LISS4(MX70)",
        # "ResourceSat-2A_LISS3",
        "ResourceSat-2A_LISS3_L2",
        # "ResourceSat-2A_LISS4(MONO)",
        # "ResourceSat-2A_LISS4(MX23)",
        # "ResourceSat-2A_LISS4(MX70)",
        # "ResourceSat-2_AWIFS",
        # "ResourceSat-2_AWIFS_L2",
        # "ResourceSat-2A_AWIFS",
        # "ResourceSat-2A_AWIFS_L2",
    ]
    # 1. Search time data
    results = instance.search_bhoo(
        [18.677323, 73.027479],
        start_date="2021-12-01",
        end_date="2022-01-01",
        sats=sats
    )
    logging.info(f"Found {len(results)} results")
    
    # TODO: Order the Data
    # for i in results[:2]:
    #     result = instance.add_order(i)
    #     print(result)
    #     message = {}
    #     if result and result.get("Results", []):
    #         message = result.get("Results", [])[0]

    # 3 Specify date for which dowload to happen
    cart_date = datetime.now() # - timedelta(days=1)
    instance.dowload_cart(cart_date)
    