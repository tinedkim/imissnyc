# I MISS NYC

The general domain of the application data will emulate the data required to spend a day in New York City. When a user spends a day, they would usually want to select specific locations/areas in the city. Also, when a user plans to stay at a location, they will want to embrace the visuals of the place they selected. According to the central location they select, they will choose which events that they want to attend and/or eat out at as many recommended restaurants as they’d like in the area which thereby completes an ideal day in New York City.


The website will narrow New York City into five well-represented areas — Times Square, Upper East Side, Williamsburg, Chelsea, and Lower East Side. The application also allows users to “go” to a location by clicking on a tab containing the backdrop of the location. The location tab will return relevant events and restaurants of each area. For events, the application will allow users to make a reservation ticket and update how many spots are left. Finally, the application will provide recommendations on the restaurants based on the location the user chose. 

## Submission Details
Our PostgreSQL account: ck2980 in the 4111-team-proj instance

URL of our web application: http://34.138.23.99:8111/

## Proposal Changes
We have implemented all the parts of SQL schema from our original proposal in Part 1, except the Goes_To table. The Goes_To relationship set was not needed because a user can go to any event(s) they choose to go; they are not chosen for a specific event. Additionally, the Goes_To table is not directly related to the frontend so we decided to omit the usage of this table.

We have also made changes in the attributes for some tables: 

- We deleted ‘distance’ and added ‘price estimation’ in the Near_ Restaurant entity set because many restaurants range their price levels from 1 to 4 to measure approximate cost per person for a meal in the restaurant. We thought this was a more crucial factor that a user can decide upon which restaurant they want to go to, so we added price estimation instead of distance in the entity set.
	
- We deleted ‘environment’ and added ‘borough’ in the Location entity set because borough was a more practical factor when users search for addresses of locations.
- We changed the name of the ‘User’ entity set to ‘Person’ because “user” is a reserved word in Postgresql. 
	
- To make things more specific, we changed attribute names from ‘name’ to ‘rname’ for the Near_Restaurant entity set and ‘name’ to ‘pname’ for the Person entity set. 
	
- After realizing that the Postgresql had more specific attribute types other than INTEGER, we changed the types for ‘start_time’ and ‘end_time’ to TIME and ‘date’ to DATE. 
	
- We added a key constraint towards the ‘Ticket’ entity set in the ER diagram because a person cannot buy more than one ticket with the same barcode (i.e. a ticket is owned by at most one person)
	

## Interesting Webpages
The web page ‘getarea’ groups relevant locationIDs of events and restaurants by each of the five areas: Times Square, Upper East Side, Williamsburg, Lower East Side, and Chelsea. There are four locationIDs that are appropriate to each area: two events and two restaurants (this was determined by the data that we added in part two of the project). So, the database selects events and restaurants that correspond to the area and gets their locationIDs. Thus, when the user clicks on one of the areas on the webpage, he/she will see a list of two events and two restaurants. We think this webpage has interesting database operations because the database categorizes the events' and restaurants’ locationIDs based on the name of the area. The ‘getarea’ webpage also requires a lot of querying because we are getting information on multiple entity sets (events and restaurants and tickets).

The web page ‘reserve_event’ is interesting because it is one of the more significant actions a user can take. For this action, we made use of SQL queries such as “INSERT” when a user can rightfully reserve a spot for an event and “UPDATE” when the spots_left attribute gets updated once the reservation is successful. The actual “reserving” action will take in the user’s information (in this case, the user’s uni) and the ticket information that the user is reserving for -- these two parameters are used in the “Buys” table. This action also triggers the get_itinerary method, updating the fetching from the database to show the appropriate reservation on the user’s itinerary.

## JQuery
The JQuery that we used in this project is just for aesthetic purposes. The two functions that we used are:

- Opening and closing a dropdown with a sliding feature

- We omitted a button that submits the form and instead used the dropdown to listen for any changes to submit the form automatically.

