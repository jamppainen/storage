from uuid import uuid4
from boto3.dynamodb.conditions import Key

DEFAULT_USERNAME = 'default'


class FSTestDB(object):
    def list_items(self):
        pass

    def add_item(self, token, data=None):
        pass

    def get_item(self, uid):
        pass

    def delete_item(self, uid):
        pass

    def update_item(self, uid, data=None):
        pass

class DynamoDBFSTest(FSTestDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, username=DEFAULT_USERNAME):
        response = self._table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']

    def add_item(self, data=None, username=DEFAULT_USERNAME):
        uid = self.generate_id()
        self._table.put_item(
            Item={
                'username': username,
                'uid': uid,
                'data': data
            }
        )
        return uid


    def generate_id(self):
        response = self._table.scan()
        max = 0
        for item in response['Items']:
            id=item['uid']
            if int(id) > max:
                max = int(id)
        return str(max+1)

    def get_item(self, uid, username=DEFAULT_USERNAME):
        response = self._table.get_item(
            Key={
                'username': username,
                'uid': uid,
            }
        )
        #print(response)
        return response.get('Item',None)

    def delete_item(self, uid, username=DEFAULT_USERNAME):
        self._table.delete_item(
            Key={
                'username': username,
                'uid': uid,
            },
            Expected={'uid':{'Value':uid}}
        )

    def update_item(self, uid, data=None, username=DEFAULT_USERNAME):
        self._table.update_item(
            Key={
                'username': username,
                'uid': uid,
            },
            UpdateExpression='SET #data = :data',
            ExpressionAttributeValues={
                ':data': data,
            },
            # data is a reserved keyword in DynamoDb so use expression attribute
            ExpressionAttributeNames={
                '#data': 'data'
            })
