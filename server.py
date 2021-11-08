
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://ck2980:7876@34.74.246.148/proj1part2"

engine = create_engine(DATABASEURI)
user = None

'''
# how do we save uni on the page

def reserve_restaurant():
  # get uni from the page?? they have to be logged in
  rname
  location 
  g.conn.execute('INSERT INTO EatsAt(rname, locationID, uni) VALUES (%s, %d, %s)', rname, location, uni)
  return redirect('/')

def buy_ticket():
  # get uni from the page?? they have to be logged in
  barcode
  g.conn.execute('INSERT INTO Buys(ticket_barcode, uni) VALUES (%s, %s)', barcode, uni)
  return redirect('/')

'''

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None
@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  print(request.args)

  return render_template("index.html")

@app.route("/getareas" , methods=['POST'])
def getarea():
  select = request.form.get('areas')
  cursor = g.conn.execute("SELECT L.locationID FROM location L WHERE L.area = '{0}'".format(str(select)))
  locationIds= []
  for result in cursor:
    locationIds.append(result[0])
  
  events = getEvents(locationIds)
  
  context = dict(events = events)
  return render_template("index.html", **context)

def getEvents(locationIds):
  eventInfo = {}
  for id in locationIds:
    occurs = g.conn.execute("SELECT O.eventID, O.locationID FROM Occurs_In O WHERE O.locationID = {0}".format(id))
    for result in occurs:
      if id == result[1]:
        eventInfo[result[1]] = {
          'loc_id': result[0]
        }

  for eventId in eventInfo.keys():
    events = g.conn.execute("SELECT * FROM Event E WHERE E.eventID = {0}".format(eventId))
    for event in events:
      eventInfo[eventId].update({
        'e_name': event[1],
        'e_type': event[2],
        'date': event[3].strftime("%m/%d/%Y"),
        'start_time': event[4].strftime("%H:%M"),
        'end_time': event[5].strftime("%H:%M"),
        'spots_left': event[6]
      })
    loc_id = eventInfo[eventId]['loc_id']
    locations = g.conn.execute("SELECT * FROM Location L WHERE L.locationID = {0}".format(loc_id))
    for location in locations:
      address = '{0}, {1}, {2}'.format(location[2], location[4], str(location[3]))
      eventInfo[eventId].update({
        'address': address,
        'image': location[5]
      })
  return eventInfo

def getRestaurants(locationIds):
  restaurantInfo = {}
  for id in locationIds:
    eats = g.conn.execute("SELECT EA.rname, EA.locationID FROM Eats_At EA WHERE EA.locationID = {0}".format(id))
    for result in eats:
      if id == result[0]:
        restaurantInfo[result[0]] = {
          'loc_id': result[1]
        }
  for rname, locationId in restaurantInfo.keys():
    restaurants = g.conn.execute("SELECT * FROM Near_Restaurant N WHERE N.locationID = {0}".format(locationId))
    for restaurant in restaurants:
      restaurantInfo[rname, locationId].update({
        'cuisine': restaurant[1],
        'rating': restaurant[2],
        'review_number': restaurant[3],
        'price_estimation': restaurant[4]
      })
    loc_id = restaurantInfo[rname, locationId]['loc_id']
    locations = g.conn.execute("SELECT * FROM Location L WHERE L.locationID = {0}".format(loc_id))
    for location in locations:
      address = '{0}, {1}, {2}'.format(location[2], location[4], str(location[3]))
      restaurantInfo[rname, locationId].update({
        'address': address,
        'image': location[5]
      })
  return restaurantInfo

# Example of adding new data to the database
@app.route('/login', methods=['POST'])
def add():
  global user
  uni = request.form['uni']
  name = request.form['name']
  # account for when user already exists -- switch to logged in state
  persons = g.conn.execute('SELECT * FROM Person P')
  returning_user = False
  for person in persons:
    if uni == person[0] and name == person[1]:
      returning_user = True
  if not returning_user:
    g.conn.execute('INSERT INTO Person(uni, pname) VALUES (%s, %s)', uni, name)
  user = (uni, name)
  return redirect('/')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
