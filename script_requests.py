import requests 
import json


file_name=input("Enter the file name which you want to upload : ")
complete_file_path=input("Enter the complete file path : ")

api_base_url="{}"
api_url="{}?file_name={}".format(api_base_url,file_name)

print(api_url)

response = requests.post(api_url)
response_result=json.loads(response.text)

files = { 'file': open(complete_file_path, 'rb')}
r = requests.post(response_result['url'], data=response_result['fields'], files=files)

print(r.status_code)