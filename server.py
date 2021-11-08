
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


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://ck2980:7876@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

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
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None
@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/event
#
# Notice that the function name is event() rather than index()
# The functions for each app.route need to have different names
#

@app.route("/getareas" , methods=['POST'])
def getarea():
  select = request.form.get('areas')
  cursor = g.conn.execute("SELECT L.locationID FROM location L WHERE L.area = '{0}'".format(str(select)))
  locationIds= []
  for result in cursor:
    locationIds.append(result[0])
  
  events = getEvents(locationIds)
  restaurants = getRestaurants(locationIds)
  
  #event_context = dict(events = events)
  #restaurant_context = dict(restaurants = restaurants)
  return render_template("index.html", events = events, restaurants = restaurants)

def getEvents(locationIds):
  eventInfo = {}
  for id in locationIds:
    occurs = g.conn.execute("SELECT O.eventID, O.locationID FROM Occurs_In O WHERE O.locationID = {0}".format(id))
    for result in occurs:
      if id == result[0]:
        eventInfo[result[0]] = {
          'loc_id': result[1]
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
      #print(id)
      #print(result)
      if id == result[1]:
        restaurantInfo[result[0]] = {
          'loc_id': result[1]
        }
  #print(restaurantInfo)

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
  print(restaurantInfo)
  return restaurantInfo

# Example of adding new data to the database
@app.route('/login', methods=['POST'])
def add():
  name = request.form['name']
  uni = request.form['uni']
  # account for when user already exists -- switch to logged in state
  g.conn.execute('INSERT INTO Person(uni, pname) VALUES (%s, %s)', uni, name)
  return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
