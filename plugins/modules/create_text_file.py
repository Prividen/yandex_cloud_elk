#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=45000, stdoutToServer=True, stderrToServer=True)

DOCUMENTATION = r'''
---
module: create_text_file

short_description: Create text file

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module create a text file with provided content.

options:
    path:
        description: Path to the file to be created (relative or absolute). If exist, may be replaced. 
        required: true
        type: path
    content:
        description: Content of text file
        required: true
        type: string
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - prividen.yandex_cloud_elk.create_text_file

author:
    - Michael Kangin (@Prividen)
'''

EXAMPLES = r'''
# Create a file with content
- name: Test file creation
  prividen.yandex_cloud_elk.create_text_file:
    path: /var/tmp/test-file.txt
    content: This is my content
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
path:
    description: Path of the created file
    type: str
    returned: always
    sample: '/var/tmp/test-file.txt'
checksum:
    description: SHA-1 checksum of file content
    type: str
    returned: always
    sample: 'd3142687e449788fd5f97a6b469c284f65bf8243'
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
            content=dict(type='str', no_log=True, required=True),
            path=dict(type='path', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    dest = module.params['path']
    content = module.params['content']

    if not dest:
        module.fail_json(msg="Destination file path can't be empty", **result)

    if os.path.sep not in dest:
        dest = '.{0}{1}'.format(os.path.sep, dest)

    b_dest = to_bytes(dest, errors='surrogate_or_strict')

    if os.path.isdir(b_dest):
        module.fail_json(msg=f'Destination {dest} is exist and directory', **result)

    dest_dir = os.path.dirname(b_dest)
    # if not dest_dir:
    #     dest_dir = to_bytes('.')

    if not os.path.exists(dest_dir):
        try:
            # os.path.exists() can return false in some
            # circumstances where the directory does not have
            # the execute bit for the current user set, in
            # which case the stat() call will raise an OSError
            os.stat(dest_dir)
        except OSError as e:
            if "permission denied" in to_native(e).lower():
                module.fail_json(msg="Destination directory %s is not accessible" % (to_native(dest_dir)))
        module.fail_json(msg="Destination directory %s does not exist" % (to_native(dest_dir)))

    if not os.access(dest_dir, os.W_OK):
        module.fail_json(msg="Destination directory %s is not writable" % (to_native(dest_dir)))


    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # create a temporary file
    _, b_mysrc = tempfile.mkstemp(dir=dest_dir)

    # and write our valuable content there
    with open(b_mysrc, 'wb') as fd:
        fd.write(to_bytes(content))
        fd.close()

    src_checksum = module.sha1(b_mysrc)

    # if destination file exist and it's checksum differ, we have to replace it
    if os.path.exists(b_dest):
        dst_checksum = module.sha1(b_dest)

        if src_checksum != dst_checksum:
            module.atomic_move(b_mysrc, b_dest)
            result['changed'] = True
        else:
            os.remove(b_mysrc)
    else:
        module.atomic_move(b_mysrc, b_dest)
        result['changed'] = True


    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    # result['original_message'] = module.params['name']
    result['path'] = dest
    result['checksum'] = src_checksum

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
