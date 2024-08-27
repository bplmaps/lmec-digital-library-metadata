import requests
import json
import pandas as pd
from datetime import date

# prepare requests & load as JSON

gis = requests.get("https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services?f=pjson") # select datasets from this - just a few
plans = requests.get("https://gis.bostonplans.org/hosting/rest/services?f=pjson") # most datasets
portal = requests.get("https://gisportal.boston.gov/arcgis/rest/services?f=pjson") # second most datasets

gis_data = gis.json()
plans_data = plans.json()
portal_data = portal.json()

# load the data structure for parsing

data={
    "servers": [
        {
          "url": "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services",
          "data": gis_data,
          "name": "bostongis"
        },
        {
          "url": "https://gis.bostonplans.org/hosting/rest/services",
          "data": plans_data,
          "name": "bostonplans"
        },
        {
          "url": "https://gisportal.boston.gov/arcgis/rest/services",
          "data": portal_data,
          "name": "gisportal"
        }
    ]
  }

# define the giant queries we'll be using over and over

query1="query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&relationParam=&returnGeodetic=false&outFields=*&returnGeometry=true&returnCentroid=false&returnEnvelope=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=4326&defaultSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnTrueCurves=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
query2="/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=*&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=4326&havingClause=&gdbVersion=&historicMoment=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&multipatchOption=xyFootprint&resultOffset=&resultRecordCount=&returnTrueCurves=false&returnExceededLimitFeatures=false&quantizationParameters=&returnCentroid=false&timeReferenceUnknownClient=false&sqlFormat=none&resultType=&featureEncoding=esriDefault&datumTransformation=&f=pjson"

# open the target JSON file to filter for only those datasets listed in target

with open('../inputs/target.json') as f:
    target=json.load(f)

# open the snapshot json file where we'll write our data

with open('../inputs/snapshot.json') as f:
    snapshot=json.load(f)

snapshot['servers']=[ ]
serverCount=0

# this is the big looping loop

for server in data['servers']:   # SERVER LOOP

    serviceCount=0
    new={ "url": server['url'], "name": server['name'], "services": [ { "featureServers": [], "mapServers": [] } ], "folders": [ ] }
    snapshot['servers'].append(new)

    layerCount=0

    for service in server['data']['services']:    # SITE ROOT SERVICES LOOP

        if service['name'] in target and service['type'] == 'FeatureServer':
            url=f"{server['url']}/{service['name']}/{service['type']}"
            url_req=requests.get(f"{url}?f=pjson")
            url_json=url_req.json()
            new={ "url": url, "name": service['name'], "layers": [] }
            snapshot['servers'][serverCount]['services'][serviceCount]['featureServers'].append(new)

            for layer in url_json['layers']:    # SITE ROOT SERVICE LAYERS LOOP

                layerUrl=f"{url}/{layer['id']}/{query1}"
                new={ "name": layer['name'], "layerUrl": layerUrl}
                snapshot['servers'][serverCount]['services'][serviceCount]['featureServers'][layerCount]['layers'].append(new)
            
            layerCount+=1

    if "folders" in server['data']:
        folderCount=0
        folder2Count=0
        fsCount=0 
        msCount=0
        for folder_name in server['data']['folders']:   # FOLDER LOOP
            
            folder_url=f"{server['url']}/{folder_name}"
            folder_req=requests.get(f"{folder_url}?f=pjson")
            folder_data=folder_req.json()           

            if "error" in folder_data:
                pass
            else:
                new={ "url": folder_url, "name": folder_name, "services": [ { "featureServers": [], "mapServers": [] } ] }
                snapshot['servers'][serverCount]['folders'].append(new)
                
                fs=[]
                ms=[]
                errors=[]

                for service in folder_data['services']: # GET F/S and M/S
                    if service['type']=='FeatureServer':
                        fs.append(f"{service['name']}/{service['type']}")
                    elif service['type']=='MapServer':
                        ms.append(f"{service['name']}/{service['type']}")
                
                fslCount=0
                mslCount=0

                for feature in fs:  # FEATURE SERVER LOOP
                    url=f"{server['url']}/{feature}"
                    feature_req=requests.get(f"{url}/?f=pjson")
                    feature_data=(feature_req.json())
                    
                    if "error" in feature_data:
                        new={ "url": url, "name": feature, "layers": "Restricted" }
                        snapshot['servers'][serverCount]['folders'][folderCount]['services'][fsCount]['featureServers'].append(new)
                    else:
                        new={ "url": url, "name": feature, "layers": [] }
                        snapshot['servers'][serverCount]['folders'][folderCount]['services'][fsCount]['featureServers'].append(new)
                        for layer in feature_data['layers']:
                            new={ "url": f"{url}/{layer['id']}{query2}", "name": layer['name'] }
                            snapshot['servers'][serverCount]['folders'][folderCount]['services'][fsCount]['featureServers'][fslCount]['layers'].append(new)
                        fslCount+=1
                folderCount+=1

                for feature in ms:  # MAP SERVER LOOP
                    url=f"{server['url']}/{feature}"
                    feature_req=requests.get(f"{url}/?f=pjson")
                    feature_data=(feature_req.json())
                    if "error" in feature_data:
                        new={ "url": url, "name": feature, "layers": "Restricted" }
                        snapshot['servers'][serverCount]['folders'][folder2Count]['services'][msCount]['mapServers'].append(new)
                    else:
                        new={ "url": url, "name": feature, "layers": [] }
                        snapshot['servers'][serverCount]['folders'][folder2Count]['services'][msCount]['mapServers'].append(new)
                        for layer in feature_data['layers']:
                            new={ "url": f"{url}/{layer['id']}{query2}", "name": layer['name'] }
                            snapshot['servers'][serverCount]['folders'][folder2Count]['services'][msCount]['mapServers'][mslCount]['layers'].append(new)
                        mslCount+=1
                folder2Count+=1
    serverCount+=1    

##############
##############
##          ##
##   DONE   ##
##          ##
##############
##############

print(json.dumps(snapshot, indent=2))
with open(f'../snapshots/snapshot-{date.today()}.json', 'w') as f:
    json.dump(snapshot,f,indent=2)
    