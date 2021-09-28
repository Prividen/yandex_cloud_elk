# Ansible Collection - prividen.yandex_cloud_elk
Deploy ELK stack on Yandex Cloud instances

## Modules
`plugins/modules/`
- `create_text_file` - This module create a text file with provided content.
- `create_yc_instance` - create compute instances in Yandex Cloud

## Roles
`roles/`
- `create_text_file` - Test role for create_text_file module
- `elasticsearch_role` - install and configure Elasticsearch
- `filebeat_role` - install and configure Filebeat
- `kibana_role` - install and configure Kibana
- `logstash_role` - install and configure Logstash

## Playbooks
`playbooks/`
- `site.yml` - main playbook to deploy ELK stack
- `create_yc_instance.yml` - create YC instance and register it in dynamic inventory
- `create_text_file.yml` - test playbook for `create_text_file` role

## Vars
`playbooks/group_vars/all/vars.yml`
- `hosts_spec` - dictionary with hosts resources, group by hostgroup names

Description of other vars see in role's README