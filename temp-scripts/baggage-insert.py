
# Enable the required Python libraries.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

import time

# Useful variables
serviceUsername = "389c0932-8ba8-406b-8730-ff8b76623111-bluemix"
servicePassword = "a87f3c5c22bed16fd4c8cb6aa1cc00c87a12a2e8d0fd6fa0588f91084bb28529"
serviceURL = "https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com"

# This is the name of the database we are working with.
databaseName = "baggage"

# Simple collection of data, as an example to store within the database:
# Data format: [baggage_id, h, w, d]
# "h" is for height | "w" is for width | "d" is for depth
sampleData = [
    [17, 49.6, 44.1, 22.2, False],
    [18, 62.2, 35.3, 20, True],
    [19, 58.13, 47.2, 27, False],
    [20, 70.13, 53, 42, False]
]

# sampleData = [
#     [17, 64.6, 40.1, 22.2, False],
#     [18, 62.2, 33.3, 20, True],
#     [19, 50.13, 47.2, 27, False],
#     [20, 46.13, 53, 28, True],
#     [16, 69.1, 32.11, 39.13, False],
# ]

# Start the demo.
print "===\n"

# Use the Cloudant library to create a Cloudant client.
client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

# Connect to the server
client.connect()

myDatabaseDemo = client[databaseName]

# Space out the results.
print "----------\n"

# Create documents using the sample data.
# Go through each row in the array
for document in sampleData:
    # Retrieve the fields in each row.
    baggage_id = document[0]
    height = document[1]
    width = document[2]
    depth = document[3]
    approved = document[4]

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
    # Wait between entries so Cloudant does not freak out (we're using the free tier).
    print "-- New entry inserted!\n"

    time.sleep(0.5)

# Space out the results.
print "----------\n"

# Say good-bye.
exit()