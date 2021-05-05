# 30 mins cpcb data fetch range

import pandas as pd
import re
import base64
import json
import time
import traceback
import requests
from datetime import datetime
from datetime import timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fetch_cpcb_data(state, city, site, fromDate, endDate):
  objFromDate = datetime.strptime(fromDate, "%d-%m-%Y" )
  objEndDate = datetime.strptime(endDate, "%d-%m-%Y" )

  how_many_days = 1 #Increment by days for the loop
  toDate = ""

  time_part = " T00:00:00Z"
  time_part_end = " T00:00:59Z"

  df = pd.DataFrame(columns=['From Date','PM2.5 (ug/m3)','PM10 (ug/m3)'])

  headers = {}
  headers['Origin'] = 'https://app.cpcbccr.com'
  headers['Accept-Encoding'] ="gzip, deflate, br"
  headers['Accept-Language'] ="en-GB,en-US;q=0.9,en;q=0.8"
  headers['User-Agent'] ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.51 Safari/537.36"
  headers['Content-Type'] ="application/x-www-form-urlencoded"
  headers['Accept'] ="application/json, text/plain, */*"
  headers['Referer'] ="https://app.cpcbccr.com/ccr/"
  headers['Connection'] ="keep-alive"
  headers['Host'] ="app.cpcbccr.com"

  while (objFromDate < objEndDate):

    print("Started for " + objFromDate.strftime("%d-%m-%Y"))
    objNextDate = objFromDate +timedelta(days=how_many_days)

    fromDate=objFromDate.strftime("%d-%m-%Y")+time_part
    toDate=objNextDate.strftime("%d-%m-%Y")+time_part_end

    data_to_encode='{"draw":1,"columns":[{"data":0,"name":"","searchable":true,"orderable":false,"search":{"value":"","regex":false}}],"order":[],"start":0,"length":50000,"search":{"value":"","regex":false},"filtersToApply":{"parameter_list":[{"id":0,"itemName":"PM2.5","itemValue":"parameter_193"},{"id":1,"itemName":"PM10","itemValue":"parameter_215"}],"criteria":"30 Minute","reportFormat":"Tabular","fromDate":"'+fromDate+'","toDate":"'+toDate+'","state":"'+state+'","city":"'+city+'","station":"'+site+'","parameter":["parameter_193","parameter_215"],"parameterNames":["PM2.5","PM10"]},"pagination":1}'

    encoded_data = base64.b64encode(data_to_encode.encode())

    r = requests.post("https://app.cpcbccr.com/caaqms/fetch_table_data", headers=headers, data=encoded_data, verify=False, timeout=None)

    if r.status_code == 200:
      print("Yayy! Received some response")
      json_data = json.dumps(r.json())

      #print(json_data)

      try:
        json_data = json.loads(json_data)
          
        data = json_data["data"]
        tabularData = data["tabularData"]
        bodyContent = tabularData["bodyContent"]

        for row in bodyContent:
          dict={}
          #dateformat : 14-Oct-2017 - 08:00"
          if "from date" in row.keys():
            from_date = row["from date"]
            dict["From Date"] = from_date

          if "PM2.5" in row.keys():
            pm25 = row["PM2.5"]
            if pm25 and pm25 !="":
              dict["PM2.5 (ug/m3)"] = pm25

          if "PM10" in row.keys():
            pm10 = row["PM10"]
            if pm10 and pm10 !="":
              dict["PM10 (ug/m3)"]= pm10

          #print(dict)
          df = df.append(dict, ignore_index = True)

      except Exception:
        traceback.print_exc() #error in parsing

    else:
      print("Bad luck! Received no response")

    print("Done for " + objFromDate.strftime("%d-%m-%Y"))

    objFromDate = objNextDate
    #end while

  df["From Date"] = pd.to_datetime(df["From Date"])
  df.sort_values(by="From Date", inplace=True)
  return df



state = "Delhi"
city = "Delhi"
site = "site_122"        # site_122:mandir_marg, site_124:rkpuram
fromDate = "04-05-2021"  # starting date format in %d-%m-%Y
endDate = "06-05-2021"   # final ending date format in %d-%m-%Y

df = fetch_cpcb_data(state, city, site, fromDate, endDate)

df.head()
