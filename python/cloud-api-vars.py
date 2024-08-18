import requests
import json
import time

#Token for Terraform Clouds


list_ip = "1.1.1.1/32"
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
           'Content-Type': 'application/vnd.api+json'
          }
url = 'https://app.terraform.io/api/v2/vars/var-BkewCwLTxEdvNCZR'
print(payload)
print(type(payload))
update_var = requests.request("PATCH", url, headers=headers, json=payload)
if update_var.status_code == 201:
    print("retrieved the response..")
    print(update_var.content)
else:
    print(update_var.content)
    print("Did not get the required response")

print(update_var)
print(type(update_var))
