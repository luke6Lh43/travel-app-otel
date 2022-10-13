from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json

#KUBERNETES 

#Environment Variables
mysql_host = os.environ['MYSQL_HOST']
mysql_username = os.environ['MYSQL_USERNAME']
mysql_password = os.environ['MYSQL_PASSWORD']

engine = create_engine("mysql+pymysql://" + mysql_username + ":" + mysql_password + "@" + mysql_host + ":3306/places", poolclass=NullPool)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

app = Flask(__name__)

Base = declarative_base()
Base.query = db_session.query_property()

#GENERAL CALLS

@app.route('/create', methods=['POST'])
def create():

    content = request.get_json()
    content_dict = json.loads(content['json_payload'])

    #inserting data into mysql
    try:
        from models import Places
        place = Places(place=content_dict['place'], country=content_dict['country'], visit_date=content_dict['visit_date'], transport=content_dict['transport'])
        db_session.add(place)
        db_session.commit()
        db_session.remove()

        return Response(status=200)
    except exc.SQLAlchemyError:
        return Response(status=500)

@app.route('/read', methods=['GET'])
def read():
    
    try:
        from models import Places
        list_of_places = Places.query.all()
        data = []
        
        for i in list_of_places:
            data.append(i.toDict())

        db_session.commit()
        db_session.remove()
        return json.dumps(data)

    except exc.SQLAlchemyError:
        return Response(status=500) 

@app.route('/read_one', methods=['GET'])
def read_one():
    
    content = request.get_json()
    content_dict = json.loads(content['json_payload'])
    id = content_dict['id']

    try:
        from models import Places
        place = Places.query.get(id)

        db_session.commit()
        db_session.remove()
        
        return json.dumps(place.toDict())
    except exc.SQLAlchemyError:
        return Response(status=500) 

@app.route('/update', methods=['PUT'])
def update():

    content = request.get_json()
    content_dict = json.loads(content['json_payload'])
    print(content_dict)
    #inserting data into mysql
    try:
        from models import Places
        place_to_update = db_session.query(Places).get(content_dict['id'])

        place_to_update.place = content_dict['place']
        place_to_update.country = content_dict['country']
        place_to_update.visit_date = content_dict['visit_date']
        place_to_update.transport = content_dict['transport']

        db_session.commit()
        db_session.remove()

        return Response(status=200)
    except exc.SQLAlchemyError:
        return Response(status=500)

@app.route('/delete', methods=['DELETE'])
def delete():
    content = request.get_json()
    content_dict = json.loads(content['json_payload'])

    #deleting the object
    try:
        from models import Places
        db_session.query(Places).filter(Places.id==content_dict['id']).delete()
        db_session.commit()
        db_session.remove()
        return Response(status=200)
    except exc.SQLAlchemyError:
        return Response(status=500)

# main driver function!
if __name__ == '__main__':
#   app.run(host="0.0.0.0", debug=True, use_reloader=False, port=5001, threaded=True)
    app.run(host="0.0.0.0", debug=False, port=5001, threaded=True)