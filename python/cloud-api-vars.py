import requests
import json
import time
import sys
import pytz
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
# This token is for XC 
token = "hP568bgJiiJi/+ZxyKedZ0nMkZE="
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Authorization"] = "APIToken " + token
tenant_api = "https://treino.console.ves.volterra.io/api"
ns_name = "kvm-on-prem"

#Token for Terraform Clouds
TOKEN = sys.argv[1]

def fetch_sec_event(tenant_api, ns_name):
     
    gmt = pytz.timezone('GMT')
    current = datetime.now(gmt)
    one_hour = current - timedelta(hours=1)

    end = current.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.000Z')
    start = one_hour.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.000Z')

    url = "{0}/data/namespaces/{1}/app_security/events".format(tenant_api, ns_name)
    data = {"namespace":"ns","query":"{vh_name=\"ves-io-http-loadbalancer-re-multi-op-test\",sec_event_type=~\"waf_sec_event|bot_defense_sec_event|api_sec_event|svc_policy_sec_event\"}","aggs":{},"start_time":"start","end_time":"end"}
    data["start_time"] = start
    data["end_time"] = end
    data["namespace"] = ns_name

    event = requests.post(url, headers=headers, json=data)
    return event.json()


def sec_timeline():
    """ The function will print security events """
    output = fetch_sec_event(tenant_api, ns_name)
    print("\n======= IP to get blocked =======\n")

    for i in range(len(output['events'])):
        d = json.loads(output['events'][i])    
        if d['rsp_code'] == "429" or "403":
            return d['src_ip']

    
    # Need to add if no ip address is found, then need to send Null

def update_deny_ip_in_terraform_cloud(result_dict):   
    """ This function send Deny IP to the terraform Cloud """     
    print("This function send Deny IP to the terraform Cloud")

    get_ip = list(result_dict.keys())
    list_ip = get_ip[0]
    #list_ip = sec_timeline() + '/32'
    payload = {
      "data": {
      "id":"var-BkewCwLTxEdvNCZR",
      "attributes": {
      "key":"IP_list",
      "value": list_ip,
      "description": "new description",
      "category":"terraform",
      "hcl": 'false',
      "sensitive": 'false'
      },
      "type":"vars"
    }
    }
    headers = {'Authorization': 'Bearer '+TOKEN,
           'Content-Type': 'application/vnd.api+json'}
    url = 'https://app.terraform.io/api/v2/vars/var-BkewCwLTxEdvNCZR'
    print(payload)
    update_var = requests.request("PATCH", url, headers=headers, json=payload)
    if update_var.status_code == 200:
      print("Variable updated successfully to Terraform Cloud..")
      print(update_var.content)
    else:
      print(update_var.content)
      print("Did not get the required response")
    print("retuning the data")
    return list_ip


#Get the data from updated variables

    url_get = 'https://app.terraform.io/api/v2/vars?filter%5Borganization%5D%5Bname%5D=ideathon-2024&filter%5Bworkspace%5D%5Bname%5D=xc-ratelimit'
    update_var_get = requests.request("GET", url_get, headers=headers )
    print("data received is: ")
    print(update_var_get.content)
    a_json = json.loads(update_var_get.content)
    print(a_json)
#print(type(a_json))
#print("The value of IP is: ")
#print(a_json['data']['attributes']['value'])

#Updating a variable in dictionary format

def update_ip_historic_events():
    """ This function appends the historic events on the IP """
    print("This function appends the historic events on the IP")
    ### Get the IP from Terraform Cloud
    headers = {'Authorization': 'Bearer '+TOKEN,
           'Content-Type': 'application/vnd.api+json'}

    if sec_timeline() == None:
       got_ip = '1.1.1.1/32'
    else:
       got_ip = sec_timeline() + '/32'

    print(got_ip)
    url_get = 'https://app.terraform.io/api/v2/vars?filter%5Borganization%5D%5Bname%5D=ideathon-2024&filter%5Bworkspace%5D%5Bname%5D=xc-ratelimit'
    update_var_get = requests.request("GET", url_get, headers=headers)
    print("data received is: ")
    #print(update_var_get.content)
    ip_available = json.loads(update_var_get.content)
    #print(ip_available)
    if ip_available['data'][1]['id'] == "var-4hSY5DBLpeS2QMQ8":
        existing_ip = ip_available['data'][1]['attributes']['value']    

    # Converting to list
    existing_ip_json = json.loads(existing_ip)
    # Getting the list 1st value i.e IP address
    available_ip_list = list(existing_ip_json.keys())
    available_ip = available_ip_list[0]
    print(existing_ip_json)
    print(available_ip)
    dict_ip = {}
    
    if got_ip == available_ip:
        # Getting value of IP and incrementing it
        print("User is blocked, still he tries to access")
        new_value = existing_ip_json[available_ip] + 1
        dict_ip[available_ip] = new_value
    else:
        # If the IP is found as Malicious for 1st time
        if got_ip != "1.1.1.1/32" and available_ip == '1.1.1.1/32':
           # IP address found for the first time
           print("IP is found Malicious for first time, proceeding accordingly")
           dict_ip[got_ip] = 1
        else:
        # When user is blocked for more hours and he is quite afterwards, hence decrementing the counter
           print("decrementing the counter since, malicious user is not accessing again")
           new_value = existing_ip_json[available_ip] - 1
           dict_ip[available_ip] = new_value
           if new_value == 0:
              dict_ip = {'1.1.1.1/32': 1}          

    dict_ip_str = json.dumps(dict_ip)
    payload_historic_events = {
      "data": {
      "id":"var-4hSY5DBLpeS2QMQ8",
      "attributes": {
      "key":"IP_historical_events",
      "value": dict_ip_str,
      "description": "new description",
      "category":"terraform",
      "hcl": 'false',
      "sensitive": 'false'
      },
      "type":"vars"
      }
      }
    
    headers = {'Authorization': 'Bearer '+TOKEN,
          'Content-Type': 'application/vnd.api+json'}
    
    url_dict = 'https://app.terraform.io/api/v2/vars/var-4hSY5DBLpeS2QMQ8'

    update_historic_event = requests.request("PATCH", url_dict, headers=headers, json=payload_historic_events)
    if update_historic_event.status_code == 200:
      print("Dictionary updated successfully to Terraform Cloud..")
      print(update_historic_event.content)
    else:
      print(update_historic_event.content)
      print("Did not get the Dictionary response")
    return dict_ip

if __name__ == "__main__":
    result_dict = update_ip_historic_events()
    update_deny_ip_in_terraform_cloud(result_dict)
