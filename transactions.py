import requests

url = "https://oba-auth.revolut.com/accounts/{AccountId}/transactions"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer <yourSecretApiKey>'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)