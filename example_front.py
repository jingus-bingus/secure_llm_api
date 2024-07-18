import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #disables https verify, this is fine for development but not for production

cert_path = False

def signup():
    print("---------Sign Up---------")
    user_name = input("Enter username: ")
    password = input("Enter password: ")
    data = {"user_name": user_name, "password": password}
    url = "https://127.0.0.1:5000/signup"
    try:
        response = requests.post(url, json=data, verify=cert_path)
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)  # Print the raw response body

        if response.status_code == 201:
            return response.json()
        else:
            print("Error with request:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def login():
    print("---------Login---------")
    user_name = input("Enter username: ")
    password = input("Enter password: ")
    data = {"user_name": user_name, "password": password}
    url = "https://127.0.0.1:5000/login"
    try:
        response = requests.post(url, json=data, verify=cert_path)
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)  # Print the raw response body

        if response.status_code == 200:
            return response.json()
        else:
            print("Error with request:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    choice = input("Do you want to [login] or [signup]? ")
    user_id = None

    if choice.lower() == 'signup':
        user_id = signup()["user_id"]
    elif choice.lower() == 'login':
        user_id = login()["user_id"]
    
    if user_id is None:
        print("Exiting program...")
        return

    print("---------conversation start---------")

    message = input("USER: ")
    print("------------------------------------")
    data = {"prompt": message, "user_id": user_id}

    session = requests.Session()
    url = "https://127.0.0.1:5000/conversation"
    response = session.post(url, json=data, verify=cert_path).json()
    conversation_id = response["conversation_id"]
    print("BOT: ", response['output'])
    print("------------------------------------")

    while True:
        message = input("USER: ")
        print("------------------------------------")
        if message == "QUIT":
            break

        data = {"prompt": message, "conversation_id": conversation_id, "user_id": user_id}
        response = session.put(url, json=data, verify=cert_path).json()

        print("BOT: ", response['output'])
        print("------------------------------------")

main()