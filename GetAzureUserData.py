from graphviz import Digraph
import pandas as pd
import requests
import os


# Get ur credentials from your computer environment variables (You need to define them before running the code)
tenant_id = os.getenv('TENANT_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


######################################################################## 1.GET USER DATA ################################################################################


# Zugriffstoken abrufen
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
token_response = requests.post(token_url, data=token_data)
access_token = token_response.json()['access_token']









# Get User Data (this user stcruture with its user attributes can vary from orga to orga)
users_url = 'https://graph.microsoft.com/v1.0/users?$select=displayName,JobTitle,UserPrincipalName,Department,id'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
users_response = requests.get(users_url, headers=headers)
users_data = users_response.json()
df_basic = pd.DataFrame(users_data['value'])
df_target = pd.DataFrame(columns=["DisplayName", "JobTitle", "Manager", "Id"]) #will be the modelling df
for i, row in df_basic.iterrows():
    manager_email = row["department"]
    manager_name = ""
    for i2, row2 in df_basic.iterrows():
        if(row2["userPrincipalName"]):
            if row2["userPrincipalName"] == manager_email:
                manager_name = row2["displayName"]
    df_target.loc[len(df_target), df_target.columns] = row["displayName"], row["jobTitle"], manager_name, row['id']


######################################################### 2. GET USER Profile Photo ########################################



# Download Profile Photo
def download_user_profile_picture(access_token, user_id, save_path):
    graph_api_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/photo/$value'
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(graph_api_url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    else:
        return None
    
# Save Profile Photo
for i, row in df_target.iterrows():
    save_path = "/Users/henrikraithle/Desktop/UserImages/" + f"{row['DisplayName']}.jpg"
    profile_picture = download_user_profile_picture(access_token, row["Id"], save_path)
