import boto3
import subprocess
import time
import argparse
'''
Usage:
python aws_inventory.py -u <aws_username>

Where <aws_username> is your AWS login name.
This will be used to validate the OTP that will be supplied.

Requirements:
- Python 3.7
- AWS config file populated with user credentials.
- OTP cli, an STS will be generated using the command 'otp aws'

If there a problems with the credentials for an account, a placeholder record will be returned,
eg.
123456789,cust-short-name-prod,nullResource,nullType,nullRegion,nullState

There is a pause of 15 seconds to allow a new MFA to be generated added after all resources for an account has been retrieved.
'''


def account_list():
    '''
    Generates a list of all the organization's accounts, including the parent account.
    '''
    client_accounts = []
    client = boto3.client('organizations')
    response = client.list_accounts()
    client_accounts.extend(response['Accounts'])
    if 'NextToken' in response:
        while 'NextToken' in response:
            response = client.list_accounts(NextToken=response['NextToken'])
            client_accounts.extend(response['Accounts'])
    return client_accounts


def describe_rds_instance(creds, region_list):
    '''
    Takes a set of credentials and a list of AWS regions.
    Provides a list of rds instance description by region.
    Returns a list of dictionaries which contain the resource descriptions.
    '''
    ec2_list = []
    for region in region_list:
        client = boto3.client('rds', aws_access_key_id=creds['AccessKeyId'], aws_secret_access_key=creds['SecretAccessKey'],
                              aws_session_token=creds['SessionToken'], region_name=region)
        response = client.describe_db_instances(
        )
        ec2_list.append(response)
    return ec2_list


def describe_ec2_instance(creds, region_list):
    '''
    Takes a set of credentials and list of AWS regions.
    Provides a list of ec2 instance description by region.
    Returns a list of dictionaries which contains the resource descriptions.
    '''
    db_list = []
    for region in region_list:
        client = boto3.client('ec2', aws_access_key_id=creds['AccessKeyId'], aws_secret_access_key=creds['SecretAccessKey'],
                              aws_session_token=creds['SessionToken'], region_name=region)
        response = client.describe_instances()
        db_list.append(response)
    return db_list


def sts_creds(account_number, aws_user):
    '''
    Takes an aws account number and aws username.
    Generates an STS token for a given account number.
    Returns a dictionary of STS credentials.
    '''
    client = boto3.client('sts')
    mfa_token = (subprocess.run(["otp", "aws"], capture_output=True)).stdout.decode().strip()
    response = client.assume_role(
        RoleArn='arn:aws:iam::' + account_number + ':role/DevOps',
        RoleSessionName='DevOps-Boto3',
        SerialNumber='arn:aws:iam::013209015422:mfa/' + aws_user,
        TokenCode=mfa_token
    )
    return response['Credentials']


if __name__ == '__main__':
    # Retrieves an AWS user from the supplied arguments
    parser = argparse.ArgumentParser(description='Generate a csv separated list of AWS RDS and EC2 resources for all of\
                                                 the accounts.')
    parser.add_argument('-u', '--user', type=str, help='AWS username.', nargs='?', required=True)
    args = parser.parse_args()
    aws_user_name = args.user

    # Generates a list of accounts from the parent organization.
    org_accounts = account_list()

    # Generates a list of all available AWS regions.
    regions = [region['RegionName'] for region in boto3.client('ec2').describe_regions()['Regions']]

    # Prints a header row.
    print(','.join(["AccountID", "CustomerName", "Resource", "Type", "Region", "Status"]))

    # Loops through the list of accounts to gather a list of resources.
    for account in org_accounts:
        if 'system-' in account['Name']:
            account_name = account['Name'][7:]
        else:
            account_name = account['Name']
        account_id = account['Id']
        # I've wrapped this in a try/except block in case the credentials don't work.
        try:
            # Gets STS credentials
            account_creds = sts_creds(account_id, aws_user_name)
            # Gets a description of RDS and EC2 instances
            rds_dbs = describe_rds_instance(account_creds, regions)
            ec2_instances = describe_ec2_instance(account_creds, regions)
            # Loops through the list of descriptions, generates a CSV of a few key resource characteristics.
            for db_region in rds_dbs:
                for db in db_region['DBInstances']:
                    print(','.join([account_id, account_name, "RDS", db['DBInstanceClass'], db['AvailabilityZone'][:-1], db['DBInstanceStatus']]))
            for ec2_region in ec2_instances:
                for instance in ec2_region['Reservations']:
                    for machine in instance['Instances']:
                        print(','.join([account_id, account_name, "EC2", machine['InstanceType'], machine['Placement']['AvailabilityZone'][:-1], machine['State']['Name']]))
        except:
            # If the credentials fail for one account, a placeholder record is generated and the loop continues.
            print(','.join([account_id, account_name, "nullResource", "nullType", "nullRegion", "nullState"]))
        time.sleep(15)
