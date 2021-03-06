import os
import sys
import json
from github import Github
import base64
import requests
from flask import Flask, request

app = Flask(__name__)




def push(msg):
    g = Github("8a05ca4e24f5f756bc63d652ab672798327b44ad")
    repo = g.get_user().get_repo("FbBot")
    value = repo.get_file_contents('/test.txt')
    user1 = value.content
    str1 = base64.b64decode(user1).decode("utf-8")
    update_msg=str1+"\n"+msg
    repo.update_file("/test.txt", "init commit", update_msg,value.sha)
    
def pull():
    g = Github("8a05ca4e24f5f756bc63d652ab672798327b44ad")
    repo = g.get_user().get_repo("FbBot")
    value = repo.get_file_contents('/test.txt')
    user1 = value.content
    str1 = base64.b64decode(user1).decode("utf-8")
    repo.update_file("/test.txt", "init commit", "",value.sha)
    return str1;





def splitData(data):
    return data[:data.index('_')],data[data.index('_')+1:]
    
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/data/<data>', methods=['GET'])
def msgToUser(data):
    user,msg = splitData(data)
    send_message(user, msg)
    
@app.route('/check', methods=['GET'])
def check():
    return pull()
    #check for txt file data and return

    
@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    ##################################################
                    newMsg(sender_id,message_text)
                    #send_message(sender_id, message_text)
                    ##################################################
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def newMsg(recipient_id, message_text):
    #add to txt file
    send_message(recipient_id, message_text)
    push(recipient_id+"_"+message_text)
    #file = open("test.txt", "a")
    #file.write(message_text)
    #file.close()
    #with open("test.txt", "a") as myfile:
    #   myfile.write(recipient_id + ":" +message_text + "\n")

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
