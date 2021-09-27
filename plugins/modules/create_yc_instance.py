#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_yc_instance

short_description: Create compute instance in Yandex Cloud 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Create compute instance in Yandex Cloud. 
!!! If the instance with given name is already exist, and it's resources doesn't meet required ones,
it will be deleted and recreated, without any confirmation !!! 

options:
    name:
        description: name of the instance to be created, must be unique
        required: true
        type: str
    cores:
        description: number of instance CPU cores
        required: false
        type: int
        default: 2
    memory_g:
        description: memory size in GB
        required: false
        type: int
        default: 2
    disk_g:
        description: disk size in GB
        required: false
        type: int
        default: 10
    image:
        description: image family
        required: false
        type: str
        default: centos-8
    ssh_key:
        description: public SSH key placed on created instance
        required: false
        type: str
        default: ~/.ssh/id_rsa.pub
          
        
author:
    - Michael Kangin (@Prividen)
'''

EXAMPLES = r'''
- name: Create instance with default resources
  prividen.yandex_cloud_elk.create_yc_instance:
    name: test-instance-1

- name: Create instance with custom resources
  prividen.yandex_cloud_elk.create_yc_instance:
    name: test-instance-2
    cores: 4
    memory_g: 4
    disk_g: 16
    image: ubuntu-2004-lts
    ssh_key=/home/user/.ssh/id_rsa_yandex.pub
'''

RETURN = r'''
name:
    description: name of instance
    type: str
    returned: always
cores:
    description: number of instance cpu cores
    type: int
    returned: always
memory_g:
    description: memory size in GB
    type: int
    returned: always
disk_g:
    description: disk size in GB
    type: int
    returned: always
public_ip:
    description: public IP for access this instance (temporary NAT)
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule

import yaml
import subprocess

#import pydevd_pycharm
#    pydevd_pycharm.settrace('localhost', port=45000, stdoutToServer=True, stderrToServer=True)

DEFAULT_CORES = 2
DEFAULT_MEMORY_G = 2
DEFAULT_DISK_G = 10
DEFAULT_IMAGE = 'centos-8'
DEFAULT_SSH_KEY = '~/.ssh/id_rsa.pub'


def run_yc(yc_options):
    result = {"changed": False}

    yc_cmd = f"yc --no-user-output --format yaml {yc_options}"
    yc_result = subprocess.run(yc_cmd.split(" "), capture_output=True)
    if yc_result.returncode > 0:
        module.fail_json(
            msg=f"Error running yc: {yc_result.stderr}",
            cmd="yc " + yc_options,
            **result
        )

    try:
        parsed_content = yaml.safe_load(yc_result.stdout)
    except yaml.YAMLError as e:
        module.fail_json(msg=e, **result)

    return parsed_content


def create_instance(name, cores, memory_g, disk_g, image, ssh_key):
    inst_create_options = f"compute instance create " \
                          f"--name {name} --hostname {name} --ssh-key {ssh_key} " \
                          f"--cores {cores} --memory {memory_g} --create-boot-disk type=network-ssd," \
                          f"image-folder-id=standard-images,image-family={image},size={disk_g} " \
                          f"--public-ip --preemptible"
    instance_details = run_yc(inst_create_options)
    return instance_details

def get_disk_size(disk_id):
    disk_info = run_yc(f"compute disk get --id {disk_id}")
    return int(int(disk_info["size"]) / 1024 / 1024 / 1024)

def is_instance_meet_requirements(instance, cores, memory_g, disk_g):
    # will not check for image and ssh-key in this release

    # Check for cores, memory and disk size
    return True if (
            int(instance['resources']['cores']) == cores and
            int(int(instance["resources"]["memory"]) / 1024 / 1024 / 1024) == memory_g and
            get_disk_size(instance['boot_disk']['disk_id']) == disk_g
    ) else False

def delete_instance(name):
    run_yc(f"compute instance delete --name {name}")

def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        cores=dict(type='int', required=False, default=DEFAULT_CORES),
        memory_g=dict(type='int', required=False, default=DEFAULT_MEMORY_G),
        disk_g=dict(type='int', required=False, default=DEFAULT_DISK_G),
        image=dict(type='str', required=False, default=DEFAULT_IMAGE),
        ssh_key=dict(type='str', required=False, default=DEFAULT_SSH_KEY),
    )

    result = dict(
        changed=False,
    )

    global module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    need_to_delete = False
    need_to_create = True

    all_instances = run_yc('compute instances list')

    # select info for instance with given name
    instances_by_name = [ item for item in all_instances if item.get('name') == module.params['name']]
    instance_of_interest = instances_by_name[0] if instances_by_name else False

    if instance_of_interest:
        if is_instance_meet_requirements(
                instance_of_interest,
                cores=module.params['cores'],
                memory_g=module.params['memory_g'],
                disk_g=module.params['disk_g'],
        ):
            need_to_delete = False
            need_to_create = False
        else:
            need_to_delete = True
            need_to_create = True

    if module.check_mode:
        result['changed'] = need_to_create
        module.exit_json(**result)

    if need_to_delete:
        delete_instance(module.params['name'])
        result['changed'] = True

    if need_to_create:
        instance = create_instance(
            name=module.params['name'],
            cores=module.params['cores'],
            memory_g=module.params['memory_g'],
            disk_g=module.params['disk_g'],
            image=module.params['image'],
            ssh_key=module.params['ssh_key'],
        )
        result['changed'] = True
    else:
        instance = instance_of_interest

    result["name"] = instance["name"]
    result["cores"] = int(instance["resources"]["cores"])
    result["memory_g"] = int(int(instance["resources"]["memory"]) / 1024 / 1024 / 1024)
    result["disk_g"] = get_disk_size(instance['boot_disk']['disk_id'])
    result["public_ip"] = instance["network_interfaces"][0]["primary_v4_address"]["one_to_one_nat"]["address"]

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
