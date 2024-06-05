import requests

def main():
    print("---------conversation start---------")

    message = input("USER: ")
    print("------------------------------------")
    data = {"prompt": message}

    session = requests.Session()
    url = "http://127.0.0.1:5000/conversation"
    response = session.post(url, json=data).json()
    
    print("BOT: ", response['output'])
    print("------------------------------------")

    while True:
        message = input("USER: ")
        print("------------------------------------")
        if message == "QUIT":
            break

        data = {"prompt": message}
        response = session.put(url, json=data).json()
        print("BOT: ", response['output'])
        print("------------------------------------")

main()