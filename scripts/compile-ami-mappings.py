#!/usr/bin/env python
#
# Connect to each EC2 region and query for the AMI ID that matches a given name,
# returning the result as a JSON output suitable for saving into a template.

import argparse
import json
import sys
import os

parser = argparse.ArgumentParser(
    description='Create a cross-region mapping stanza from an AMI name')
parser.add_argument('--owner', help='owner of ami (optional)')
parser.add_argument('name', help='name of ami')
args = parser.parse_args()

try:
    from boto import ec2
except ImportError:
    print 'The `boto\' module does not seem to be available, exiting.'
    sys.exit(1)

# Collect a list of regions, excluding GovCloud
regions = []
for region in ec2.regions():
    if not '-gov-' in region.name:
        regions.append(region.name)

mapping = {}
ami_filter = dict([('state', 'available'), ('name', args.name)])
for region in regions:
    sys.stdout.write('%-20s' % region)
    ec2_conn = ec2.connect_to_region(region)
    if args.owner is not None:
        ret = ec2_conn.get_all_images(owners = args.owner, filters = ami_filter)
    else:
        ret = ec2_conn.get_all_images(filters = ami_filter)

    try:
        ami = str(ret[0].id)
        real_name = str(ret[0].name)
    except IndexError:
        ami = 'NOTSUPPORTED'
    print ami
    mapping[region] = {'AMI': ami}

os.system('clear')
print json.dumps({real_name: mapping}, sort_keys=True, indent=4, separators=(',', ': '))
