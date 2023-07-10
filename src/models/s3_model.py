import boto3
from cerberus import Validator


class S3_model():
    validation_schema = {
        'bucket_name': {'type': 'string', 'required': True},
        'key_name': {'type': 'string', 'required': True},
    }

    def __init__(self, name, key):
        self.bucket_name = name
        self.key_name = key
        self.s3_client = boto3.client(service_name='s3', region_name='us-east-1')
        self.validator = Validator(self.validation_schema)
    
    def _read_content(self):
        s3_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.key_name)
        s3_content = s3_object['Body'].read().decode('utf-8')
        return s3_content
    
    def _get_list_of_file_content(self):
        s3_content = self._read_content()
        rows = s3_content.split('\n')
        rows = [row.strip() for row in rows]
        return [row.split(',') for row in rows]
    
    @property
    def file_content(self):
        return self._get_list_of_file_content()[1:] 
    
    @property
    def file_headers(self):
        return self._get_list_of_file_content()[0]
    
    def validated_file_content(self):
        is_valid = self.validator.validate(self.data)
        if not is_valid:
            raise ValueError(f"Invalid data: {self.validator.errors}")
        return self.data