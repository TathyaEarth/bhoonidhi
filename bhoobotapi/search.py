import requests
from datetime import date,timedelta

cartosat_list='''CartoSat-2_PAN(SPOT)
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
KompSat-3A_MS'''
resourcesat_list='''ResourceSat-1_LISS4(MONO)
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
ResourceSat-2A_AWIFS'''
othersat_list='''Novasar-1_SAR(All)
Aqua_MODIS
OceanSat-2_OCM
OceanSat-2_OCM_L1B
Terra_MODIS
Sentinel-1A_SAR(IW)_GRD
Sentinel-1B_SAR(IW)_GRD'''
microsat_list='''RISAT-2B_SAR(MOSAIC-3)
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
'''

telegram_token='1834545677:AAH4PIA2FACtgPJap5g2cYUe07o0CFcke9U'
#https://api.telegram.org/bot1834545677:AAH4PIA2FACtgPJap5g2cYUe07o0CFcke9U/setWebhook?url=https://27aef22b2bad.ngrok.io/locationbot/
api_url=f'https://api.telegram.org/bot{telegram_token}'

def bhoo_sat(sat_list):
    res=''
    sat_list = sat_list.split('\n')
    for sat in sat_list:
        res=res+'%2C'+sat
    return res[3:]

def msg_telegram(text,chat_id):
    message_url=f'{api_url}/sendMessage'
    data={}
    data['text']=text
    data['chat_id']=chat_id
    res=requests.post(message_url,json=data)
    resjson=res.json()
    print("SENT MSG TO TELEGRAM ---------------")
    print(resjson)
    print("------------------------------------")

def send_telegram(send_dict,chat_id):
    
    #=-------------------------------------------------------
    photo_url=f'{api_url}/sendPhoto'
    message_url=f'{api_url}/sendMessage'
    reply_id=None
    data={}
    text=''
    if('img_path' in send_dict.keys()):    
        send_url=photo_url
        data['photo']=send_dict['img_path']
        del send_dict['img_path']
    else:
        send_url=message_url
    for key in send_dict.keys():
        text=text+f'{key} : {send_dict[key]} \n'
    if('photo' in data.keys()):
        data['caption']=text+'_______________\n'
    else:
        data['text']=text+'________________\n'
    data['chat_id']=chat_id
    res=requests.post(send_url,json=data)
    resjson=res.json()
    print(resjson)
    
    #----------------------------------------------------------

def bhoo_date(today):
    month=today.strftime("%B")
    date=today.strftime("%d")
    year=today.strftime("%Y")
    return f"{month[:3].upper()}%2F{date}%2F{year}"



def search_bhoo(lat_lon,chat_id,days_diff=5):
    today = date.today()
    d2 = bhoo_date(today)
    diff= timedelta(days = days_diff) 
    d1=bhoo_date(today-diff)
    sat_lists=[cartosat_list,resourcesat_list,othersat_list,microsat_list]
    send_array=[]
    for l in sat_lists:
        sats=bhoo_sat(l)
        thresh=0.01
        json_to_be_sent={
            'edate': d2,
            'filters': "%7B%7D",
            'offset': "0", # implementing expecting < 500 results on area
            'query': "area",
            'queryType': "polygon",
            'tllat':lat_lon[0]+thresh,
            'tllon':lat_lon[1]-thresh,
            'brlat':lat_lon[0]-thresh,
            'brlon':lat_lon[1]+thresh,
            'sdate': d1,
            'selSats': sats,
            'userId': "T",
            'filters': "%7B%7D",
        }

        #print(json_to_be_sent)

        url='https://bhoonidhi.nrsc.gov.in/bhoonidhi/ProductSearch'

        res=requests.post(url,json=json_to_be_sent)
        
        '''
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
        '''

        results=res.json()['Results']
        
        for result in results:
            print('-----------------------------')
            #print(result)
            send_dict={}
            if('$' not in result['FILENAME'] and 'SEN2A' not in result['FILENAME']):
                img_path=f"https://bhoonidhi.nrsc.gov.in/{result['DIRPATH']}/{result['FILENAME']}.jpeg"
                send_dict['img_path']=img_path
                print(img_path)
            elif('SEN2A' in result['FILENAME']):
                img_path=f"https://bhoonidhi.nrsc.gov.in/{result['DIRPATH']}/{result['FILENAME']}.jpg"
                send_dict['img_path']=img_path
                print(img_path)
            send_dict['sensor']=result['SENSOR']
            send_dict['satellite']=result['SATELLITE']
            send_dict['dateofpass']=result['DOP']
            try:
                send_dict['path']=result['PATHNO']
                send_dict['scene']=result['SCENE_NO']
                send_dict['imagingorbit']=result['IMAGING_ORBIT_NO']
            except:
                pass
            send_telegram(send_dict,chat_id)
            send_array.append(send_dict)
        
    #print(send_array)    
if(__name__=='__main__'):
    search_bhoo([20,78],chat_id)
