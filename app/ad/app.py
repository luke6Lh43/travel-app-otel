from flask import Flask, Response, request
import json
import os
import random

#Environment Variables
ad1_url = os.environ['AD1_URL']
ad2_url = os.environ['AD2_URL']
ad3_url = os.environ['AD3_URL']

app = Flask(__name__)

@app.route('/get_ad', methods=['GET'])
def get_ad():

    ads = [ad1_url, ad2_url, ad3_url]
    data = random.choice(ads)

    if(data):
        return json.dumps(data)
    else:
        return Response(status=500)

@app.route('/post_ad', methods=['POST'])
def post_ad():

    #here will be some logic to upload visitor data to external db (e.g. Mongo) for additional analytics

    content = request.get_json()
    content_dict = json.loads(content)

    return Response(status=200)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5002, threaded=True)