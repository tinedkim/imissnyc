
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
user = ()
eventInfo = {}

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
  print(user)
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
  global eventInfo
  eventInfo = {}
  events = getEvents(locationIds)
  restaurants = getRestaurants(locationIds)
  
  return render_template("index.html", events = events, restaurants = restaurants, user = user)

def getEvents(locationIds):
  global eventInfo
  for id in locationIds:
    occurs = g.conn.execute("SELECT O.eventID, O.locationID FROM Occurs_In O WHERE O.locationID = {0}".format(id))
    for result in occurs:
      if id == result[1]:
        eventInfo[result[1]] = {
          'loc_id': result[0]
        }
  update_eventInfo()
  return eventInfo

def update_eventInfo():
  global eventInfo
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
    
    tickets = get_tickets(eventId)
    eventInfo[eventId].update({
      'tickets': tickets
     })

def get_tickets(event_id):
  ticketsInfo = {}
  tickets = g.conn.execute('SELECT * FROM Ticket_Allowed_Entry T WHERE T.eventID = {0}'.format(event_id))
  for ticket in tickets:
    ticketsInfo[ticket[0]] = {
        'price': ticket[1],
        'owner': 'none'
      }
    ticket_owners = g.conn.execute('SELECT * FROM Buys B')
    reserved = False, None
    for owner in ticket_owners:
      if owner[0] == ticket[0]:
        reserved = True, owner[1]
    if reserved[0]:
      ticketsInfo[ticket[0]]['owner'] = reserved[1]
  return ticketsInfo

@app.route('/reserve', methods=['POST'])
def reserve_event():
  ticket_barcode = request.form.get('reserve')
  global user
  uni = user[0]
  events = g.conn.execute("SELECT T.eventID FROM Ticket_Allowed_Entry T WHERE T.ticket_barcode = '{0}'".format(ticket_barcode))
  
  for event in events:
    ticket_eventID = event[0]
  
  spots = g.conn.execute('SELECT E.spots_left FROM Event E WHERE E.eventID = {0}'.format(ticket_eventID))
  for spot_no in spots:
    spots_left = spot_no[0]
  if (spots_left > 0):
    g.conn.execute('UPDATE Event SET spots_left = spots_left - 1 WHERE eventID = {0}'.format(ticket_eventID))
    g.conn.execute('INSERT INTO Buys(ticket_barcode, uni) VALUES (%s, %s)', ticket_barcode, uni)
    update_eventInfo()
  global eventInfo
  return render_template("index.html", events = eventInfo, user = user)
  

def getRestaurants(locationIds):
  restaurantInfo = {}
  for id in locationIds:
    eats = g.conn.execute("SELECT EA.rname, EA.locationID FROM Eats_At EA WHERE EA.locationID = {0}".format(id))
    for result in eats:
      if id == result[1]:
        restaurantInfo[result[0]] = {
          'loc_id': result[1]
        }

  for rname in restaurantInfo.keys():
    restaurants = g.conn.execute("SELECT * FROM Near_Restaurant N WHERE N.rname = '{0}'".format(rname))
    for restaurant in restaurants:
      restaurantInfo[rname].update({
        'cuisine': restaurant[1],
        'rating': restaurant[2],
        'review_number': restaurant[3],
        'price_estimation': restaurant[4]
      })
      
    loc_id = restaurantInfo[rname]['loc_id']
    locations = g.conn.execute("SELECT * FROM Location L WHERE L.locationID = {0}".format(loc_id))
    for location in locations:
      address = '{0}, {1}, {2}'.format(location[2], location[4], str(location[3]))
      restaurantInfo[rname].update({
        'address': address,
        'image': location[5]
      })
  return restaurantInfo

@app.route('/login', methods=['POST'])
def add():
  global user
  uni = request.form['uni']
  name = request.form['name']
  persons = g.conn.execute('SELECT * FROM Person P')
  returning_user = False
  for person in persons:
    if uni == person[0] and name == person[1]:
      returning_user = True
  if not returning_user:
    g.conn.execute('INSERT INTO Person(uni, pname) VALUES (%s, %s)', uni, name)
  user = (uni, name)
  return render_template("index.html", user = user)

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
