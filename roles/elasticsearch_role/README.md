Elascticsearch role
=========

Роль для установки elasticsearch на хостах с ОС: Debian, Ubuntu, CentOS, RHEL.

Requirements
------------

Поддерживаются только ОС семейств debian и EL.

Role Variables
--------------

| Variable name | Default | Description |
|-----------------------|----------|-------------------------|
| elasticsearch_version | "7.14.0" | Параметр, который определяет какой версии elasticsearch будет установлен |
| es_java_memory_gb     | 1        | Elasticsearch Java heap memory limit |

Example Playbook
----------------

    - hosts: all
      roles:
         - { role: mnt-homeworks-ansible }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
