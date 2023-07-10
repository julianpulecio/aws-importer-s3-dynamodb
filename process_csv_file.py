import os
import json
from src.helpers.process_dict_to_object import dict_to_object
from src.models.s3_model import S3_model
from src.models.dynamodb_model import Dynamodb_model

def process_s3_file(event, context):
    for record in event.get('Records'):
        try:
            record = json.loads(record.get('body'))
            s3_model = dict_to_object(S3_model,record)
            dynamo_db_model = Dynamodb_model(
                s3_model.key_name,
                s3_model.file_headers,
                s3_model.file_content
            )
            dynamo_db_model.populate_table()       
        except Exception as e:
            raise Exception('file could not be processed') from e
    return {"statusCode": 200}
