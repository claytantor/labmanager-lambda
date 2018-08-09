#!/usr/bin/env python
# coding: utf-8

import datetime
import logging
import boto3
import json

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

class Dynamic(dict):
  """Dynamic objects are just bags of properties, some of which may happen to be functions"""
  def __init__(self, **kwargs):
    self.__dict__ = self
    self.update(kwargs)

  def __setattr__(self, name, value):
    import types
    if isinstance(value, types.FunctionType):
      self[name] = types.MethodType(value, self)
    else:
      super(Dynamic, self).__setattr__(name, value)

def main():
    event = Dynamic()
    context = Dynamic(function_name="cli")
    run(event, context)


def get_untagged_buckets(s3):

    # Call S3 to list current buckets
    response = s3.list_buckets()

    # Get a list of all bucket names from the response
    buckets_remove = []
    for bucket in response['Buckets']:
        try:
            tags_response = s3.get_bucket_tagging(Bucket=bucket['Name'])
            tags = [tag['Key'] for tag in tags_response['TagSet']]

            # required tags - must have either
            # TODO should be data driven
            if "owner" not in tags and "aws:cloudformation:stack-name" not in tags:
                buckets_remove.append(bucket['Name'])
        except:
            buckets_remove.append(bucket['Name'])

    return buckets_remove

def delete_buckets(s3, buckets_remove):
    for bucket_name in buckets_remove:
        response = delete_recursive(bucket_name, "")
        response = s3.delete_bucket(Bucket=bucket_name)
        logger.info("deleted bucket:{0}".format(bucket_name))


def delete_recursive(bucketname, keyprefix):
    '''
    Recusively delete all keys with given prefix from the named bucket
    '''
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucketname)
    bucket.objects.filter(Prefix=keyprefix).delete()

def run(event, context):

    # Create an S3 client
    s3 = boto3.client('s3')
    buckets_remove = get_untagged_buckets(s3)
    logger.info("buckets to delete:{0}".format(buckets_remove))
    delete_buckets(s3, buckets_remove)

    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time))


if __name__ == '__main__':
    main()
