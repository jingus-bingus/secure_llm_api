import requests
import webbrowser
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #disables https verify, this is fine for development but not for production
import os

cert_path = False  # Bypass SSL certificate verification

def signup():
    session = requests.Session()
    print("---------Sign Up---------")
    user_name = input("Enter username: ")
    password = input("Enter password: ")
    data = {"user_name": user_name, "password": password}
    url = "https://127.0.0.1:5000/signup"

    try:
        response = session.post(url, json=data, timeout=30, verify=cert_path)
        print("Status Code:", response.status_code)

        if response.status_code == 201:
            response_data = response.json()
            print("User created successfully!")
            user_id = response_data['user_id']
            totp_secret = response_data['totp_secret']
            # Open the QR code URL in the web browser
            qr_code_url = f"https://127.0.0.1:5000/qrcode/{user_id}/{totp_secret}"
            webbrowser.open(qr_code_url)
            return session
        else:
            print("Error with request:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def login():
    session = requests.Session()
    print("---------Login---------")
    user_name = input("Enter username: ")
    password = input("Enter password: ")
    data = {"user_name": user_name, "password": password}
    url = "https://127.0.0.1:5000/login"

    try:
        response = session.post(url, json=data, timeout=30, verify=cert_path)
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)  # Print the raw response body

        if response.status_code == 200:
            data_json = response.json()
            user_id = data_json['user_id']

            token = input("Enter the token from Google Authenticator: ")

            verify_url = "https://127.0.0.1:5000/verify-token"
            verify_data = {"user_id": user_id, "token": token}
            verify_response = session.post(verify_url, json=verify_data, timeout=30, verify=cert_path)
            if verify_response.status_code == 200 and verify_response.json()['verified']:
                print("Login successful!")
                return session
            else:
                print("Invalid token.")
                return None
        else:
            print("Error with request:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def main():
    choice = input("Do you want to [login] or [signup]? ")
    user_id = None
    if choice.lower() == 'signup':
        session = signup()
    elif choice.lower() == 'login':
        session = login()
    
    if session is None:
        print("Exiting program...")
        return
    
    choice = 0
    file_choice = None
    while choice != 'n':
        files = os.listdir('./app/files')
        for i, file in enumerate(files):
            print(str(i) + ': ' + file)
        print("Follow link to upload a new file: https://127.0.0.1:5000/upload")
        choice = input("Do you want to include a file as context? (<file number>, n to skip, or press enter to reload files)")
        if choice.isdigit():
            file_choice = files[int(choice)]
            break

    print("---------conversation start---------")

    message = input("USER: ")
    print("------------------------------------")
    if file_choice:
        data = {"prompt": message, "file": file_choice}
    else:
        data = {"prompt": message}

    url = "https://127.0.0.1:5000/conversation"
    response = session.post(url, json=data, timeout=30, verify=cert_path).json()
    conversation_id = response["conversation_id"]
    print("BOT: ", response['output'])
    print("------------------------------------")

    while True:
        message = input("USER: ")
        print("------------------------------------")
        if message == "QUIT":
            break
        
        if file_choice:
            data = {"prompt": message, "conversation_id": conversation_id, "file": file_choice}
        else:
            data = {"prompt": message, "conversation_id": conversation_id}

        response = session.put(url, json=data, verify=cert_path).json()

        print("BOT: ", response['output'])
        print("------------------------------------")

main()
