# 1.  Connecting to the service instance.

# Enable the required Python libraries.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

import time

# # Useful variables
# serviceUsername = "<YOUR_USER_NAME>-bluemix"
# servicePassword = "<YOUR_PASSWORD>"
# serviceURL = "https://<YOUR_USER_NAME>-bluemix.cloudant.com"
serviceUsername = "389c0932-8ba8-406b-8730-ff8b76623111-bluemix"
servicePassword = "a87f3c5c22bed16fd4c8cb6aa1cc00c87a12a2e8d0fd6fa0588f91084bb28529"
serviceURL = "https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com"

# This is the name of the database we are working with.
databaseName = "baggage"

# Simple collection of data, as an example to store within the database:
# Data format: [baggage_id, h, w, d]
# "h" is for height | "w" is for width | "d" is for depth
sampleData = [
    [50, 45.4, 24.6, True],
    [52.98, 46, 26.22, False],
    [63.33, 47.23, 27, False],
    [48.43, 42.11, 28.79, True],
    [43.12, 38.6, 39.27, False],
    [43,45, 45.34, 24.36, True],
    [52.98, 46, 26.14, True],
    [49.78, 47.23, 27, False],
    [68.78, 42.4, 28.5, False],
    [52.78, 42.23, 22.1, True]
]

# Start the demo.
print "===\n"

# Use the Cloudant library to create a Cloudant client.
client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

# Connect to the server
client.connect()

# Connect to the database
myDatabaseDemo = client[databaseName]

# Display the current index
my_document = myDatabaseDemo['0']
baggageIndex = my_document['count']
print "Initial index: " + str(baggageIndex)

baggageIndex = int(baggageIndex)

# Create documents using the sample data.
# Go through each row in the array
for document in sampleData:

    baggageIndex = baggageIndex + 1
    print "Updated index: " + str(baggageIndex)

    # replace the zero index with the latest input
    zero = myDatabaseDemo['0']
    zero['count'] = str(baggageIndex)
    zero.save()

    # Retrieve the fields in each row.
    baggage_id = baggageIndex
    height = document[0]
    width = document[1]
    depth = document[2]
    approved = document[3]

    # Create a JSON document that represents
    # all the data in the row.
    jsonDocument = {
        '_id': str(baggage_id),
        'height': height,
        'width': width,
        'depth': depth,
        'approved': approved
    }

    # Create a document using the Database API.
    newDocument = myDatabaseDemo.create_document(jsonDocument)

    print "Success!"

    time.sleep(4)

# Disconnect from the server
client.disconnect()

# Say good-bye.
exit()