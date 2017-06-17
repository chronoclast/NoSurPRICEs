--- WORK IN PROGRESS ---

# Cloudant NoSQL Database

## Deployment In Bluemix

--- WORK IN PROGRESS ---

## Retrieving Values from the Databases

Currently there are two databases that reside in the Cloudant service:

* **Baggage:** It stores the size of the baggages, and if they're cabin-approved or not.
* **Maximum baggage size per airline:** It contains the sizes of the cabin-approved (i.e. hand luggage) per airline.

### Authentication / Permission

Reader permissions have been granted to unauthenticated connections, meaning that these databases can also be used for external projects, without a login.

### Baggage Database

Values can be easily retrieved using a GET request. Here's an example for the "Baggage" database (`baggage`) in cURL:

    $ curl -X GET https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com/baggage/_id

**Note:** The `_id` at the end of the URL is the "identificator" of the baggage, for example, `4` corresponds to the 4th baggage introduced in the system.

### Maximum Size per Airline Database

The following example retrieves the maximum size of the cabin baggage for KLM:

    $ curl -X GET https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com/maxsize/KLM

Airline names/identifiers are available in the [raw data file](./max-baggage-size-db.txt).

The response from the Cloudant instance should look like:

```shell
{
	"_id":"KLM",
	"_rev":"1-0058dfe2597cb77b2b52d072d1674b91",
	"baggageWeight":12,
	"baggageDepth":35,
	"baggageWidth":25,
	"baggageHeight":55
}
```
