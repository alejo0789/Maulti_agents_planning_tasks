
#data dummy
import requests
project="website"
milestone="define the needs"
task= "Requirements Gathering" 

trello_api_key="b1ad50176e2d251ac38678a476473f79"
trello_token="ATTA2200071ae723832ef517ce2d1a81bb939a99f07947eb5dd127d55f0589f782ca01EDDBE7"


def create_board(board_name):
    url = "https://api.trello.com/1/boards/"
    querystring = {"name": board_name, "key": trello_api_key, "token": trello_token}
    response = requests.post(url, params=querystring)
    if response.status_code == 200:
        board_id = response.json()["shortUrl"].split("/")[-1].strip()
        return board_id
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None





#create a list

def create_list(board_id, list_name):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    querystring = {"name": list_name, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    list_id = response.json()["id"]
    return list_id

#create a card

def create_card(list_id, card_name):
    url = f"https://api.trello.com/1/cards"
    querystring = {"name": card_name, "idList": list_id, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    card_id = response.json()["id"]
    return card_id


# create a card with id list and the name of the card "the task"

def create_card(list_id, card_name):
    url = f"https://api.trello.com/1/cards"
    querystring = {"name": card_name, "idList": list_id, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    card_id = response.json()["id"]
    return card_id

#call the function to create the board and return the id
name="test"+ project
id_board = create_board(name)

#call the function to create the list with id board and the name of the list and return the list_id
#list_id=create_list(id_board, milestone)

#create_card(list_id, task)