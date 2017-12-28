"""
DESCRIPTION:
    This script populates the database "max-size" that stores the maximum cabin-approved baggage size
    for the most popular airlines.
    It is entirely based on the example materials from the Bluemix documentation, available here:
    https://console.bluemix.net/docs/services/Cloudant/tutorials/create_database.html

RAW DATA:
    The raw data is available in the file "max-baggage-size-db.txt", but it's already embedded in this
    script.

DATA SOURCE:
    Skyscanner:
    https://www.skyscanner.net/news/cabin-luggage-guide-hand-baggage-sizes-and-weight-restrictions

AUTHOR:
    Jaime Gonzalez-Arintero
    <a.lie.called.called@gmail.com>
"""

# Required Python libraries.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

import time

# Credentials.
# serviceUsername = "<YOUR_USER_NAME>-bluemix"
# servicePassword = "<YOUR_PASSWORD>"
# serviceURL = "https://<YOUR_USER_NAME>-bluemix.cloudant.com"

serviceUsername = "389c0932-8ba8-406b-8730-ff8b76623111-bluemix"
servicePassword = "a87f3c5c22bed16fd4c8cb6aa1cc00c87a12a2e8d0fd6fa0588f91084bb28529"
serviceURL = "https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com"

# Name of the database we are working with.
databaseName = "maxsize"

# Simple collection of data, as an example to store within the database:
# Data format: [airline_id, h, w, d, kg]
# "h" is for height (cm) | "w" is for width (cm) | "d" is for depth (cm) | "kg" is for the weight (kg)
# The airlines with "NA" in the last field have no weight restrictions
sampleData = [
    ["AerLingus", 55, 40, 24, 10],
    ["AirFrance", 55, 35, 25, 12],
    ["British", 56, 45, 25, 23],
    ["Delta", 56, 35, 23, "NA"],
    ["easyJet", 56, 45, 25, "NA"],
    ["Emirates", 55, 38, 20, 7],
    ["Etihad", 40, 50, 25, 7],
    ["Flybe", 55, 35, 23, 10],
    ["Jet2", 56, 45, 25, 10],
    ["KLM", 55, 25, 35, 12],
    ["Lufthansa", 55, 40, 23, 8],
    ["Monarch", 56, 40, 25, 10],
    ["Norwegian", 55, 40, 23, 10],
    ["Qatar", 50, 37, 25, 7],
    ["Ryanair", 55, 40, 20, 10],
    ["ThomasCook", 55, 40, 20, 6],
    ["Thomson", 55, 40, 20, 5],
    ["Turkish", 55, 40, 23, 8],
    ["Virgin", 56, 36, 23, 10],
    ["Vueling", 55, 40, 20, 10]
]

# Launch the script.
print "===\n"

# Use the Cloudant library to create a Cloudant client.
client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

# Connect to the server.
client.connect()

# The database has to exist already to continue!
# Otherwise, see the commented out code below.
myDatabaseDemo = client[databaseName]   
# ----------------------------------------------

# Create an instance of the database (in case it does not exist).
# myDatabaseDemo = client.create_database(databaseName)

# Check that the database has been successfully created.
# if myDatabaseDemo.exists():
#     print "'{0}' successfully created.\n".format(databaseName)

# Otherwise, if it already exists, open it.
# except:
#     myDatabaseDemo = client[databaseName]

#     # Check that it truly exists.
#     if myDatabaseDemo.exists():
#         print "'{0}' already exists, no need to create it again.\n".format(databaseName)

# Space out the results.
print "----\n"

# Create the entries using the sample data.
# Go through each row in the array.
for document in sampleData:

    # Retrieve the fields in each row.
    airline_id = document[0]
    height = document[1]
    width = document[2]
    depth = document[3]
    weight = document[4]

    # Create a JSON document that represents all the data in the row.
    jsonDocument = {
        '_id': str(airline_id),
        'baggageHeight': height,
        'baggageWidth': width,
        'baggageDepth': depth,
        'baggageWeight': weight,
        }

# data = {
#     '_id': 'julia30', # Setting _id is optional
#     'name': 'Julia',
#     'age': 30,
#     'pets': ['cat', 'dog', 'frog']
#     }

    # Create a document/entry using the Database API.
    newDocument = myDatabaseDemo.create_document(jsonDocument)

    # Check that the document/entry exists in the database.
    if newDocument.exists():
        print "Document '{0}' successfully created.".format(airline_id)
        # Wait between insertions (since the free tier of Cloudant is limited).
        time.sleep(0.5)

# Space out the results.
print "----\n"

# Simple and minimal retrieval of the first document in the database.
result_collection = Result(myDatabaseDemo.all_docs)
print "Retrieved minimal document:\n{0}\n".format(result_collection[0])

# Simple and full retrieval of the first document in the database.
result_collection = Result(myDatabaseDemo.all_docs, include_docs=True)
print "Retrieved full document:\n{0}\n".format(result_collection[0])

# Space out the results.
print "----\n"

# Use a Cloudant API endpoint to retrieve
# all the documents in the database,
# including their content.

# Define the end point and parameters
end_point = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
params = {'include_docs': 'true'}

# Issue the request
response = client.r_session.get(end_point, params=params)

# Display the response content
print "{0}\n".format(response.json())

# Space out the results.
print "----\n"

# Check one of the airlines.
my_document = myDatabaseDemo['AirFrance']

# Display its name (airline_id)
print my_document['_id']

# Display a sample height
print my_document['baggageHeight']


# # All done.
# # Time to tidy up.

# # 5.  Deleting the database.

# # Delete the test database.
# try :
#     client.delete_database(databaseName)
# except CloudantException:
#     print "There was a problem deleting '{0}'.\n".format(databaseName)
# else:
#     print "'{0}' successfully deleted.\n".format(databaseName)

# # 6.  Closing the connection to the service instance.

# # Disconnect from the server
# client.disconnect()

# # Finish the demo.
# print "===\n"

# Say good-bye.
exit()