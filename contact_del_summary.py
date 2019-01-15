#
# Python sample
# Call Contact Delete Status Summary REST API and import timeseries data into Datorama
#
# Marketing Cloud Demo Day
# sanagama | 11-Dec-2018
#
import os, sys, requests, json, datorama

# Read ClientId and ClientSecret from ENV variables
client_id = str(os.environ['MCAPI_CLIENTID'])
client_secret = str(os.environ['MCAPI_CLIENTSECRET'])

# Read REST endpoimnts from ENV variables
# See: https://developer.salesforce.com/docs/atlas.en-us.noversion.mc-getting-started.meta/mc-getting-started/get-access-token.htm
auth_url = str(os.environ['MCAPI_AUTH_URL'])

# See: https://developer.salesforce.com/docs/atlas.en-us.mc-apis.meta/mc-apis/ContactsDeleteStatus.htm
contact_summary_url = str(os.environ['MCAPI_CONTACT_DELETE_ANALYTICS_URL'])

def main():
    print ('>>> Contact Delete Status Summary REST API Demo <<<\n')

    try:
        # 1. Call REST API to get OAuth token with ClientId and ClientSecret
        oauth_token = get_oauth_token(client_id, client_secret)

        # 2. Call REST API to get Contact Delete Status Summary
        delete_status_summary = get_contact_delete_summary(oauth_token)

        # 3. Add JSON data to Datorama model
        add_to_Datorama(delete_status_summary)

    except Exception as e:
        print('Caught exception:' )
        print str(e)

    print ('\nAll done!\n')

#
# 1. Call REST API to get OAuth token with ClientId and ClientSecret
#
def get_oauth_token(client_id, client_secret):
    print ('>>> Getting OAuth Access Token')

    url = auth_url
    oauth_token = None
    headers = { 'Content-type': 'application/json;charset=UTF-8' }
    post_body = { 'clientId': client_id, 'clientSecret': client_secret }

    print ('>>> URL:' + auth_url)
    print ('>>> POST Body: ' + str(post_body))

    response = requests.post(url = url, headers = headers, json = post_body)
    if(response.ok):
        json_data = json.loads(response.content)
        oauth_token = str(json_data['accessToken'])
        token_expiry = str(json_data['expiresIn'])
        print("OAuth token = " + oauth_token + ", expires = " + token_expiry)
    else:
        response.raise_for_status()

    return oauth_token

#
# 2. Call REST API to get Contact Delete Status Summary
#
def get_contact_delete_summary(oauth_token):
    print ('>>> Getting Contact Delete Status Summary')

    delete_status_summary = None
    url = contact_summary_url
    headers = { 
        'Content-type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + oauth_token
    }
    params = { "startdateUtc": "2018-11-11", "enddateUtc": "2018-12-11" }

    print ('>>> URL:' + url)
    response = requests.get(url, headers = headers, params = params)
    if(response.ok):
        delete_status_summary = json.loads(response.content)
    else:
        response.raise_for_status()

    return delete_status_summary

#
# 3. Add JSON data to Datorama model
#
def add_to_Datorama(delete_status_summary):
    print ('>>> Adding Contact Delete Status Summary into Datorama')
    print ('>>> JSON payload')
    print(json.dumps(delete_status_summary, indent=2, sort_keys=True))

    csvData = ""
    csvHeaders = "DateTime, Count, Status"

    # Get timeseries data from JSON
    timeSeriesReceived = delete_status_summary["timeSeries"][0]
    for timeSeriesItem in timeSeriesReceived["items"]:
        csvData += "\n"
        csvData += str(timeSeriesItem["time"]) + ','
        csvData += str(timeSeriesItem["value"]) + ','
        csvData += "Received"

    timeSeriesCompleted = delete_status_summary["timeSeries"][1]
    for timeSeriesItem in timeSeriesCompleted["items"]:
        csvData += "\n"
        csvData += str(timeSeriesItem["time"]) + ','
        csvData += str(timeSeriesItem["value"]) + ','
        csvData += "Completed"

    timeSeriesInvalid = delete_status_summary['timeSeries'][2]
    for timeSeriesItem in timeSeriesInvalid["items"]:
        csvData += "\n"
        csvData += str(timeSeriesItem["time"]) + ','
        csvData += str(timeSeriesItem["value"]) + ','
        csvData += "Invalid"

    timeSeriesProcessing = delete_status_summary["timeSeries"][3]
    for timeSeriesItem in timeSeriesProcessing["items"]:
        csvData += "\n"
        csvData += str(timeSeriesItem["time"]) + ','
        csvData += str(timeSeriesItem["value"]) + ','
        csvData += "Processing"

    # Save CSV into Datorama
    csv = csvHeaders + "\n" + csvData + "\n"
    datorama.save_csv(csv)

#
# main entry point
#
if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("Usage: contact_del_summary.py")
    else:
        main()
