# storage
Simple rest API to store user data. Built with chalice. Uses AWS Lambda, API Gateway and DynamoDb.
## Reading:
https://aws.amazon.com/blogs/developer/build-and-deploy-a-serverless-rest-api-in-minutes-using-chalice/
https://chalice.readthedocs.io/en/latest/quickstart.html
https://chalice.readthedocs.io/en/latest/api.html
http://chalice-workshop.readthedocs.io/en/latest/
https://joarleymoraes.com/hassle-free-python-lambda-deployment/

## Deployment:
chalice local
chalice deploy
chalice delete --stage dev

## DynamoDb tables:
See .chalice/config.json for table names

### Scan tables
aws dynamodb scan --table-name storage-app-<uuid>
aws dynamodb scan --table-name users-app-<uuid>

### Delete item
aws dynamodb delete-item --table-name storage-app-<uuid> --key "{\"username\":{\"S\":\"tester\"},\"uid\":{\"S\":\"1\"}}"

### Delete user
aws dynamodb delete-item --table-name users-app-<uuid> --key "{\"username\":{\"S\":\"tester\"}}"

### Drop table:
aws dynamodb delete-table storage-app-<uuid>

## API specs:
Server base address:
Username:
Password:
APIs with PUT and POST methods expect content type application/json
APIs - except login- require authentication by using header Authorization: <token>

Login:
POST /v1/login
Request body: {"username": "<username>", "password":"<password>"}
Response: {"token": "<token>"}

Create storage with optional data:
POST /v1/storage
request body (optional): { "data": <data>}
response: {"id": "<id>", "data": "<data>"}

Update data in storage
PUT /v1/storage/{id} request body: {"data": <data element>}
response: {"id": <id>, "data": <data element>}

Get data from storage
GET /v1/storage/{id}
response: {"id": <id>, "data": <data element>}

Delete storage:
DELETE /v1/storage/{id}
response: OK

## ARNs
Lambda: arn:aws:lambda:eu-central-1:419277593273:function:storage-dev

