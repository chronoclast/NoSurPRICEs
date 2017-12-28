# Required Python libraries.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

# Starting the engines.
longstring = """\
###################################
### LET'S GET THE PARTY STARTED ###
###################################
"""
print longstring

# Credentials
# serviceUsername = "<YOUR_USER_NAME>-bluemix"
# servicePassword = "<YOUR_PASSWORD>"
# serviceURL = "https://<YOUR_USER_NAME>-bluemix.cloudant.com"
serviceUsername = "389c0932-8ba8-406b-8730-ff8b76623111-bluemix"
servicePassword = "a87f3c5c22bed16fd4c8cb6aa1cc00c87a12a2e8d0fd6fa0588f91084bb28529"
serviceURL = "https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com"

# Use the Cloudant library to create a Cloudant client.
client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

# Connect to the server.
client.connect()

# This is the name of the database we are working with.
databaseName = "baggage"

# Connect to the database.
myDatabaseDemo = client[databaseName]



###################
# Baggage details #
###################
baggage_id = 0
height = 63.4
width = 40.5
depth = 21.9
approved = False
###################



# Create a JSON document that stores all the data
jsonDocument = {
    '_id': str(baggage_id),
    'height': height,
    'width': width,
    'depth': depth,
    'approved': approved
    }

# Create a new entry on the database using the API.
newDocument = myDatabaseDemo.create_document(jsonDocument)

# Space out the results.
print "Success!"

# Disconnect from the server
client.disconnect()

# Bye, bye!
exit()
