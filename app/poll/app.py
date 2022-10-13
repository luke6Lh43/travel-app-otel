from flask import Flask, Response, request
import json
import redis
import datetime
import os

#Environment Variables
redis_host = os.environ['REDIS_HOST']
redis_password = os.environ['REDIS_PASSWORD']

app = Flask(__name__)

@app.route('/poll_update', methods=['POST'])
def update_poll():

    content = request.get_json()
    content_dict = json.loads(content['json_payload'])

    now = datetime.datetime.now()
    currenttime = now.strftime("%Y-%m-%d %H:%M:%S")

    data = json.dumps({'time' : currenttime, 'voter_id': content_dict['voter_id'], 'choice': content_dict['choice']})

    try:
        r = redis.Redis(host=redis_host, password=redis_password, port='6379')
        r.rpush('key', data)
        return Response(status=200)
    except redis.RedisError as e:
        return Response(status=500)

@app.route('/get_poll', methods=['GET'])
def get_poll():

    try:
        r = redis.Redis(host=redis_host, password=redis_password, port='6379')
        data = r.lrange('key', 0, -1)

        temp_dict = {}
        final_dict = {}

        #saving redis db content to dictionary
        for index, item in enumerate(data):
            res = json.loads(item)
            temp_dict[index]=res

        #reverting the order in dictionary and saving unique values voter_id->choice to new dict
        for key in sorted(temp_dict, reverse=True):
            if temp_dict[key]['voter_id'] not in final_dict.keys():
                final_dict[temp_dict[key]['voter_id']] = temp_dict[key]['choice']

        return json.dumps(final_dict)

    except redis.RedisError as e:
        return Response(status=500)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5003, threaded=True)


    