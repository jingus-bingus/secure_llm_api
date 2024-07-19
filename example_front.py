import requests
import webbrowser
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Disable HTTPS verification warnings for development

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
            return user_id
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
            user_id = response.json()['user_id']
            token = input("Enter the token from Google Authenticator: ")

            verify_url = "https://127.0.0.1:5000/verify-token"
            verify_data = {"user_id": user_id, "token": token}
            verify_response = session.post(verify_url, json=verify_data, timeout=30, verify=cert_path)
            if verify_response.status_code == 200 and verify_response.json()['verified']:
                print("Login successful!")
                return user_id
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
        user_id = signup()
    elif choice.lower() == 'login':
        user_id = login()
    
    if user_id is None:
        print("Exiting program...")
        return

    print("---------conversation start---------")

    message = input("USER: ")
    print("------------------------------------")
    data = {"prompt": message, "user_id": user_id}

    session = requests.Session()
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

        data = {"prompt": message, "conversation_id": conversation_id, "user_id": user_id}
        response = session.put(url, json=data, timeout=30, verify=cert_path).json()

        print("BOT: ", response['output'])
        print("------------------------------------")

main()
