Role Name
=========

Role for Kibana installation on Ubuntu 18/20, RHEL 7/8


Role Variables
--------------

| Variable name | Default value | Description |
|---------------|---------------|-------------|
|kibana_version |7.14.0 | Kibana version |
|kibana_install_type| remote | Install type |
|elasticsearch_hosts| --- | Array of elasticsearch hosts |

Example Playbook
----------------
    - name: Install Kibana
      hosts: kibana
      roles:
        - kibana_role


License
-------

MIT

