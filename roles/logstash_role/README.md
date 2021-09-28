Role Name
=========

Role for Logstash installation on Ubuntu 18/20, RHEL 7/8


Role Variables
--------------

| Variable name | Default value | Description |
|---------------|---------------|-------------|
|logstash_version |7.14.0 | Logstash version |
|logstash_install_type| remote | Install type |
|elasticsearch_hosts| --- | Array of elasticsearch hosts |

Example Playbook
----------------
    - name: Install Logstash
      hosts: logstash
      roles:
        - logstash_role


License
-------

MIT

