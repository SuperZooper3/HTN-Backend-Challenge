import requests
import random
import time

server_url = "http://127.0.0.1:8000/"

boba_flavors = ["Taro", "Honeydew", "Thai Tea", "Mango", "Strawberry", "Lychee", "Passionfruit", "Peach", "Coconut", "Pineapple"]
boba_sweetness = ["0% Sweet", "25% Sweet", "50% Sweet", "75% Sweet", "100% Sweet"]
boba_ice = ["No Ice", "Light Ice", "Regular Ice", "Extra Ice"]

# Give 20 pariticpants 10 tokens each
for i in range(20):
    participant_id = i+1
    response = requests.put(f"{server_url}bbt_token_admin_give", json={"tokens":10, "participant_id":participant_id})
    print("Token give response:")
    time.sleep(0.1)
    print(response.status_code)

# Send in 10 random boba orders
for i in range(10):
    participant_id = random.randint(1, 20)
    order = {
        "participant_id": participant_id,
        "flavour": random.choice(boba_flavors),
        "sweetness": random.choice(boba_sweetness),
        "ice": random.choice(boba_ice)
    }
    response = requests.post(f"{server_url}boba", json=order)
    print("Boba order response:")
    time.sleep(0.1)
    print(response.status_code)
    if response.json():
        print(response.json())

# Check in 5 random participants
for i in range(5):
    participant_id = random.randint(1, 20)
    response = requests.post(f"{server_url}checkin", json={"participant_id":participant_id, "volunteer_id":1})
    time.sleep(0.1)
    print("Check in response:")
    print(response.status_code)
    if response.json():
        print(response.json())

# Advance 10 random orders to "Ready"
for i in range(10):
    order_id = random.randint(1, 10)
    response = requests.put(f"{server_url}boba", json={"status":"Delivered", "order_id":order_id})
    time.sleep(0.1)
    print("Boba order update response:")
    print(response.status_code)
    if response.json():
        print(response.json())
