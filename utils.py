import os
import json
import requests
import dialogflow_v2 as dialogflow
from pymongo import MongoClient

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"

dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "moviesbot-ouhijv"

mclient = MongoClient("mongodb+srv://mukul:mukulvashishtha@cluster0-2akl0.mongodb.net/test?retryWrites=true&w=majority")
db = mclient.get_database('preference')
records = db.preference


# from gnewsclient import gnewsclient

# client = gnewsclient.NewsClient(max_results=3)

# def get_news(parameters):
# 	client.topic = parameters.get('news_type')
# 	client.language = parameters.get('language')
# 	client.location = parameters.get('geo-country')
# 	return client.get_news()

mykey = '7d20c210'

def apicall(query):
    url = f'http://www.omdbapi.com/?apikey={mykey}&t={query}&plot=full'
    print(url)
    res = requests.get(url)
    data = json.loads(res.text)
    return data

def getquery(parameters):
    # print(parameters)
    client = parameters.get('movies')   
    # print('movie name is ', client)
    # data = apicall(client)
    return client

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg, session_id):
    response = detect_intent_from_text(msg, session_id)
    movie = getquery(dict(response.parameters))

    if response.intent.display_name == 'getactor':
        resp = apicall(movie)
        temp = f'Actors are {resp["Actors"]}'
        return temp
    elif response.intent.display_name == 'getgenre':
        resp = apicall(movie)
        temp = f'Genre is {resp["Genre"]}'
        return temp
    elif response.intent.display_name == 'getposter':
        resp = apicall(movie)
        temp = resp["Poster"]
        ls = []
        ls.append(temp)
        return ls
    elif response.intent.display_name == 'getplot':
        resp = apicall(movie)
        dic = {"session_id" : session_id, "movies" : movie}
        if records.find_one({"movies" : movie}):
            records.delete_one({"movies" : movie})
        records.insert(dic) 
        temp = f'{resp["Plot"]}'
        return temp
    elif response.intent.display_name == 'showrating':
        resp = apicall(movie)
        rating = resp["Ratings"]
        print(rating)
        temp = ''
        for i in rating:
            temp += f'{i["Source"]} : {i["Value"]} \n'
        return temp
    elif response.intent.display_name == 'getpreference':
        # records.delete_one({"movies" : "null"})
        ls = list(records.find())
        print(ls)
        temp = ''
        if len(ls) != 0:
            temp = 'Your preference are '
            for var in ls:
                temp += var["movies"] + ', '
        else:
            temp = 'Your preference are empty. '        
        return temp        
    else:
        return response.fulfillment_text