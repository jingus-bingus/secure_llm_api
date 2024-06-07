import requests

def main():
    user_id = input("Enter user id: ")
    print("---------conversation start---------")

    message = input("USER: ")
    print("------------------------------------")
    data = {"prompt": message, "user_id": user_id}

    session = requests.Session()
    url = "http://127.0.0.1:5000/conversation"
    response = session.post(url, json=data).json()
    conversation_id = response["conversation_id"]
    print("BOT: ", response['output'])
    print("------------------------------------")

    while True:
        message = input("USER: ")
        print("------------------------------------")
        if message == "QUIT":
            break

        data = {"prompt": message, "conversation_id": conversation_id, "user_id": user_id}
        response = session.put(url, json=data).json()

        print("BOT: ", response['output'])
        print("------------------------------------")

main()