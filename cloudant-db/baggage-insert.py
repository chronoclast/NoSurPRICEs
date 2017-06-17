# 1.  Connecting to the service instance.

# Enable the required Python libraries.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

# Useful variables
serviceUsername = "<YOUR_USER_NAME>-bluemix"
servicePassword = "<YOUR_PASSWORD>"
serviceURL = "https://<YOUR_USER_NAME>-bluemix.cloudant.com"

# This is the name of the database we are working with.
databaseName = "baggage"

# Simple collection of data, as an example to store within the database:
# Data format: [baggage_id, h, w, d]
# "h" is for height | "w" is for width | "d" is for depth
sampleData = [
    [1, 65, 45, 25],
    [2, 66, 46, 26],
    [3, 67, 47, 27],
    [4, 68, 48, 28],
    [5, 69, 49, 39]
]

# Start the demo.
print "===\n"

# Use the Cloudant library to create a Cloudant client.
client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

# Connect to the server
client.connect()

# 2.  Creating a database within the service instance.

# Create an instance of the database.
try:
    myDatabaseDemo = client.create_database(databaseName)

    # Check that the database has been successfully created.
    if myDatabaseDemo.exists():
        print "'{0}' successfully created.\n".format(databaseName)

# Otherwise, if it already exists, open it.
except:
    myDatabaseDemo = client[databaseName]

    # Check that it truly exists.
    if myDatabaseDemo.exists():
        print "'{0}' already exists, no need to create it again.\n".format(databaseName)

# Space out the results.
print "----\n"

# 3.  Storing a small collection of data as documents within the database.

# Create documents using the sample data.
# Go through each row in the array
for document in sampleData:
    # Retrieve the fields in each row.
    baggage_id = document[0]
    height = document[1]
    width = document[2]
    depth = document[3]

    # Create a JSON document that represents
    # all the data in the row.
    jsonDocument = {
        '_id': str(baggage_id),
        'baggageHeight': height,
        'baggageWidth': width,
        'baggageDepth': depth
    }

# data = {
#     '_id': 'julia30', # Setting _id is optional
#     'name': 'Julia',
#     'age': 30,
#     'pets': ['cat', 'dog', 'frog']
#     }

    # Create a document using the Database API.
    newDocument = myDatabaseDemo.create_document(jsonDocument)

    # Check that the document exists in the database.
    if newDocument.exists():
        print "Document '{0}' successfully created.".format(baggage_id)

# Space out the results.
print "----\n"

# 4.  Retrieving a complete list of the documents.

# Simple and minimal retrieval of the first
# document in the database.
result_collection = Result(myDatabaseDemo.all_docs)
print "Retrieved minimal document:\n{0}\n".format(result_collection[0])

# Simple and full retrieval of the first
# document in the database.
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

my_document = myDatabaseDemo['2']


# Display the document
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