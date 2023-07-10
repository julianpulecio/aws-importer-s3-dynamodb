import pytest
import boto3
import os
import json
import csv
import re
from ast import literal_eval
from dotenv import load_dotenv
from moto import mock_s3, mock_dynamodb
from process_csv_file import process_s3_file

load_dotenv()

class TestFileProcessing:

    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    TEST_FILE_PATH = 'tests/grades.csv'
    TEST_FILE_NAME = 'grades.csv'
    TEST_SQS_EVENT_FILE_PATH = 'tests/event_sqs_test.json'
    
    @pytest.fixture
    def s3(self):
        with mock_s3():
            s3 = boto3.client(service_name='s3', region_name='us-east-1')
            s3.create_bucket(Bucket=self.S3_BUCKET_NAME)
            s3.upload_file(Filename=self.TEST_FILE_PATH, Bucket=self.S3_BUCKET_NAME, Key=self.TEST_FILE_NAME)
            yield s3
    
    @pytest.fixture
    def dynamodb(self):
        with mock_dynamodb():
            dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
            yield dynamodb_client

    @pytest.fixture
    def sqs_event(self):
        sqs_event = open(self.TEST_SQS_EVENT_FILE_PATH).read()
        return sqs_event
    
    @pytest.fixture
    def csv_file(self):
        csv_file = open(self.TEST_FILE_PATH, 'r')
        return csv_file

    def test_that_the_number_of_items_in_csv_and_dyanmodb_are_equal(self, s3, dynamodb, sqs_event, csv_file):
        process_s3_file(event=json.loads(sqs_event), context={})
        dynamo_items = dynamodb.scan(TableName=self.TEST_FILE_NAME).get('Items')
        csv_items = csv.reader(csv_file)

        assert len(dynamo_items) + 1 == len([item for item in csv_items])
        
        
        



