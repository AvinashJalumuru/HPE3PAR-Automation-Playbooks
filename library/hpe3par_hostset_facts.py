#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
# HPE Deployment Automation
#
# (C) Copyright 2020-2021 Hewlett Packard Enterprise Development LP
#
# Author :  Avinash Jalumuru <avinash.jalumuru@hpe.com>
# Commit :  618e6fe
# Date   :  2022-07-19
#
##############################################################################

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hpe3par_hostset_facts
short_description: Gather facts of the HPE3PAR host facts
description:
    - This module gather facts about volume(s) of the 3PAR storage array.
version_added: 0.1
author:
    - Avinash Jalumuru
notes:
    - Tested on HPE 3PAR 7200 (3.2.2)
requirements:
  - "3PAR OS - 3.2.2 MU6, 3.3.1 MU1"
  - "Ansible - 2.4"
  - "hpe3par_sdk 1.0.0"
  - "WSAPI service should be enabled on the 3PAR storage array."
options:
   name:
     description:
     - Name of the matching volume
     - If set, facts of specific volumes are returned.
     required: False
'''

EXAMPLES = """
    - name: Gather facts of 3PAR volume with name 'existing-volume'
      hpe3par_hostset_facts:
        api_url: rest_api_url
        username: 3par_username
        password: 3par_password
        name: existing-volume
        register: facts

    - name: Gather facts of the available 3PAR volume
      hpe3par_hostset_facts:
        api_url: rest_api_url
        username: 3par_username
        password: 3par_password
        register: facts
"""

RETURN = """
volumes:
    description: returns the metadata of the 3PAR volume(s)
    type:
        list: If no input name, returns the list of volumes
        dict: If input name is specified, returns dict of volume object
        None: Returned in case of volume not found
    sample: [
        {
            "name": "BL460_Bay6",
            "wwn": "60002AC0000000000000088C00008194",
            "userCPG": "FC_r1"
            "size": "10240"
            "snapCPG": "FC_r1"
            "provisionType": "full"
        ]
    ]

count:
    description: Size of the volume response
    returned: always
    type: int
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from hpe3parclient.client import HPE3ParClient
    from hpe3parclient.exceptions import HTTPNotFound
except ImportError:
    HPE3ParClient = None

try:
    from hpe3par_sdk import client
except ImportError:
    client = None

def getHostSetInfo(hostset):
    if not hostset:
        return None

    hostList = dict()
    hostList['id'] = hostset.id
    hostList['name'] = hostset.name
    hostList['uuid'] = hostset.uuid
    hostList['comment'] = hostset.comment
    hostList['domain'] =  hostset.domain
    hostList['setmembers'] =  hostset.setmembers

    return hostList

def main():

    argument_spec = {
        "storage_system_ip":       { "required": True, "type": "str"},
        "storage_system_username": { "required": True, "type": "str", "no_log": True},
        "storage_system_password": { "required": True, "type": "str", "no_log": True},
        "name": { "required": False, "type": "str"}
    }

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    if client is None:
        module.fail_json(msg='the python hpe3par_sdk module is required')
    if HPE3ParClient is None:
        module.fail_json(msg='the python python-3parclient module is required')

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]

    name = module.params.get('name')

    port_number = client.HPE3ParClient.getPortNumber(
        storage_system_ip, storage_system_username, storage_system_password)
    wsapi_url = 'https://%s:%s/api/v1' % (storage_system_ip, port_number)
    client_obj = client.HPE3ParClient(wsapi_url)
    client_obj.login(storage_system_username, storage_system_password)

    try:

        result = dict()
        result['changed'] = False

        count = 0
        hostsets = list()

        if name:
            dbHostSet = client_obj.getHostSet(name=name)
            hostset = getHostSetInfo(dbHostSet)
            hostsets.append(hostset)
        else:
            dbHostSets = client_obj.getHostSets()
            for dbHostSet in dbHostSets:
                hostset = getHostSetInfo(dbHostSet)
                hostsets.append(hostset)

        result['hostsets'] = hostsets
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e))
    finally:
        client_obj.logout()

if __name__ == '__main__':
    main()
