## Contributing guide

### Setup

    virtualenv venv -p python3.6
    pip install aws-sam-cli
    pip install lambda/requirements.txt


### Deploy

    sam build
    sam package --s3-bucket <SAM_S3_BUCKET> --output-template-file packaged.yml
    sam deploy --template-file packaged.yml --stack-name stop-start-on-tag --capabilities CAPABILITY_IAM

### Publish

    sam build
    sam package --s3-bucket <SAM_S3_BUCKET> --output-template-file packaged.yml
    sam publish --template packaged.yml --region <AWS_REGION>