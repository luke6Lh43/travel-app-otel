from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
import json
import random
import datetime
import os

app = Flask(__name__)

#ENV VARIABLES

places_svc = os.environ['PLACES_SVC']
poll_svc = os.environ['POLL_SVC']
ad_svc = os.environ['AD_SVC']

#SUPPORTIVE METHODS

#This is a method to get ad URL from ad service
def get_ad_url():

    ad_url = ""

    #GETTING THE AD URL

    try:
        response = requests.get('http://' + ad_svc + ':5002/get_ad')
        response.close()
        ad_url = response.json()

    except requests.exceptions.RequestException as e:
        ad_url = "ERROR"  

    return ad_url

#This is a method to get poll results from poll service
def get_poll_results():

    #GETTING POLL RESULTS

    values = []

    try:
        response = requests.get('http://' + poll_svc + ':5003/get_poll')
        response.close()

        if response.status_code == 200:
            poll_results = response.json()
        else:
            poll_results = {}        
        
    except requests.exceptions.RequestException as e:
        poll_results = {}  

    alone_val = 17
    group_val = 31

    if poll_results:
        for key in poll_results:
            if poll_results[key] == 'alone':
                alone_val = alone_val + 1
            elif poll_results[key] == 'group':
                group_val = group_val + 1
    
    values = [alone_val, group_val]

    return values

#This is a main page route
@app.route('/')
def index():

    #generating voter_id

    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    ad_url = get_ad_url()
    values = get_poll_results()

    #getting list of places

    try:
        response = requests.get('http://' + places_svc + ':5001/read')
        response.close()
        places = response.json()
        
        if response.status_code == 200:
            resp = make_response(render_template('index.html', places=places, ad_url=ad_url, values=values))
            resp.set_cookie('voter_id', voter_id)
            return resp 

        else:
            resp = make_response(render_template('index.html', ad_url=ad_url, values=values))
            resp.set_cookie('voter_id', voter_id)
            return resp          

    except requests.exceptions.RequestException as e:
        resp = make_response(render_template('index.html', ad_url=ad_url, values=values))
        resp.set_cookie('voter_id', voter_id)
        return resp

#This is an add page route (where the form for adding new place is present)
@app.route('/add')
def add():

    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    ad_url = get_ad_url()
    values = get_poll_results()
    
    resp = make_response(render_template('add.html', ad_url=ad_url, values=values))
    resp.set_cookie('voter_id', voter_id)
    return resp

#This is an edit page route (where the form for editing a place is present)
@app.route('/edit', methods=['POST'])
def edit():

    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    ad_url = get_ad_url()
    values = get_poll_results()

    id = request.form.get('id')
    data = {"id": id}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}

    try:
        response = requests.get('http://' + places_svc + ':5001/read_one', json=payload)
        response.close()
    
        return render_template('edit.html', place=response.json(), ad_url=ad_url, values=values)

    except requests.exceptions.RequestException as e:
        return render_template('failure.html')

#This is a success page route
@app.route('/success')
def success():

    return render_template('success.html')

#This is a failure page route
@app.route('/failure')
def failure():
    return render_template('failure.html')


#This is a create method to send data to places service and create a new item
@app.route('/create', methods=['POST'])
def create():

    #getting some values from the form
    place = request.form.get("place")
    country = request.form.get('country')
    visit_date = request.form.get('visit_date')
    transport = request.form.get('transport')

    data = {"place": place, "country": country, "visit_date": visit_date, "transport": transport}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}

    try:
        response = requests.post('http://' + places_svc + ':5001/create', json=payload)
        response.close()
    
        if response.status_code == 200:
            return redirect(url_for('success')) 
        else:
            return redirect(url_for('failure')) 

    except requests.exceptions.RequestException as e:
        return redirect(url_for('failure')) 

#This is an update method to send data to places service and edit an item
@app.route('/update', methods=['POST'])
def update():

    id = request.form.get("id")
    place = request.form.get("place")
    country = request.form.get('country')
    visit_date = request.form.get('visit_date')
    transport = request.form.get('transport')

    data = {"id": id, "place": place, "country": country, "visit_date": visit_date, "transport": transport}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}

    try:
        response = requests.put('http://' + places_svc + ':5001/update', json=payload)
        response.close()
    
        if response.status_code == 200:
            return redirect(url_for('success')) 
        else:
            return redirect(url_for('failure')) 

    except requests.exceptions.RequestException as e:
        return redirect(url_for('failure')) 

#This is a delete method to send data to places service and delete an item
@app.route('/delete', methods=['POST'])
def delete():

    id = request.form.get("id")

    data = {"id": id}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}

    try:
        response = requests.delete('http://' + places_svc + ':5001/delete', json=payload)
        response.close()
    
        if response.status_code == 200:
            return redirect(url_for('success')) 
        else:
            return redirect(url_for('failure')) 

    except requests.exceptions.RequestException as e:
        return redirect(url_for('failure')) 

#This is a route to send visitor data to ad service
@app.route('/post_ad')
def post_ad():

    #getting IP address of the visitor
    ip_addr = request.remote_addr

    now = datetime.datetime.now()
    currenttime = now.strftime("%Y-%m-%d %H:%M:%S")

    payload = json.dumps({'time' : currenttime, 'ip_addr': ip_addr})

    try:
        response = requests.post('http://' + ad_svc + ':5002/post_ad', json=payload)
        response.close()    
        return redirect(url_for('index'))

    except requests.exceptions.RequestException as e:
        return redirect(url_for('failure'))

#This is a route to send poll data (choice) to poll service
@app.route('/poll', methods=['POST'])
def poll():

    choice = request.form.get("choice")
    voter_id = request.cookies.get('voter_id')

    data = {"choice": choice, "voter_id": voter_id}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}

    try:
        response = requests.post('http://' + poll_svc + ':5003/poll_update', json=payload)
        response.close()
        return redirect(url_for('index')) 

    except requests.exceptions.RequestException as e:
        return redirect(url_for('failure'))

# main driver function
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000, threaded=True)