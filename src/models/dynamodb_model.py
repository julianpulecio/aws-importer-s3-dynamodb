import boto3
import uuid
import time
import json
from cerberus import Validator
from ast import literal_eval

class Dynamodb_model():
    def __init__(self, table_name, headers, contents):
        self.table_name = table_name
        self.headers = headers
        self.contents = contents
        self.dynamodb_client = boto3.client(service_name='dynamodb', region_name='us-east-1')

    def _map_content_type(self, content_value):
        value = literal_eval(content_value)
        content_type = type(value)
        if content_type is int or content_type is float:
            return {'N' : str(value)} 
        if content_type is str:
            return {'S' : str(value)}
        if content_type is bool:
            return {'B' : bool(value)}
        if content_type is None:
            return None

    def _create_items(self):
        items = []
        for row in self.contents:
            item = self._create_item(row)
            items.append(item)
        return items

    def _create_item(self, row):
        item = {}
        for element_key, element in enumerate(row):
            header = self.headers[element_key].strip()
            try:
                attribute = literal_eval(header.strip())
            except ValueError as e:
                attribute = header.strip()
            value = self._map_content_type(element.strip())
            item['key'] = {'S': str(uuid.uuid4().int)}
            if value is None:
                raise ValueError(
                    f'the file could not be processed in row {element_key} for attribute {header}'
                )
            item[attribute] = value
        return item
    
    def _create_table(self):
        table_name = self.table_name
        table_schema = [{
            'AttributeName': 'key',
            'AttributeType': 'S'
        }]
        key_schema = [{
            'AttributeName': 'key',
            'KeyType': 'HASH'
        }]
        provisioned_throughput = {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
        self.dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=table_schema,
            KeySchema=key_schema,
            ProvisionedThroughput=provisioned_throughput
        )
        self._is_table_ready()

    def _table_exist_(self, table_name):
        table_list = self.dynamodb_client.list_tables(Limit=10).get('TableNames')
        return self.table_name in table_list

    def _is_table_ready(self):
        time.sleep(2)
        if not self._table_exist_(self.table_name):
            self._is_table_ready()
        table_info = self.dynamodb_client.describe_table(TableName=self.table_name)
        if table_info['Table']['TableStatus'] != 'ACTIVE':
            self._is_table_ready()
        return True
    
    def populate_table(self):
        if not self._table_exist_(self.table_name):
            self._create_table()
        items = self._create_items()
        for item in items:
            self.dynamodb_client.put_item(
                TableName = self.table_name,
                Item = item 
            )