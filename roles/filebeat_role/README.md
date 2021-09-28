Role Name
=========

Role for Filebeat installation on Ubuntu 18/20, RHEL 7/8


Role Variables
--------------

| Variable name | Default value | Description |
|---------------|---------------|-------------|
|filebeat_version |7.14.0 | Filebeat version |
|filebeat_install_type| remote | Install type |
|elasticsearch_hosts| --- | Array of elasticsearch hosts |
|logstash_hosts| --- | Array of logstash hosts |
|kibana_host| --- | Kibana host |

Example Playbook
----------------
    - name: Install Filebeat
      hosts: filebeat
      roles:
        - filebeat_role


License
-------

MIT

