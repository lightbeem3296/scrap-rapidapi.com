import requests

# Replace with your actual RapidAPI key
API_KEY = "ef908b5eeamsh50984dd5b890d6ep1ab791jsn2fb248ebf19a"
url = "https://api.rapidapi.com/rest/api/apis"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api.rapidapi.com"
}

# Make the request to fetch the list of APIs
response = requests.get(url, headers=headers)

# Check if the response is successful
if response.status_code == 200:
    # Parse and print the JSON data
    apis_list = response.json()
    print(apis_list)
else:
    print(f"Failed to fetch APIs: {response.status_code}")
