# HPE3PAR-Automation-Playbooks
Playbooks to automation HPE3PAR storage for Application workloads

Using these
* The username and passwords of VMware and 3PAR are written in ansible vault
  Use the option --ask-vault-pass while running playbooks

DATASTORE CREATE/RESIZE/DELETE
******************************
1. cd /workspace/ansible

2. Update the fields for storage and vcenter in the input file
   (properties/ds_create_input.yml)
   (properties/ds_resize_input.yml)
   (properties/ds_delete_input.yml)

3. Run the playbooks to perform create/resize/delete datastore
   ansible-playbook create.yml --ask-vault-pass
   ansible-playbook resize.yml --ask-vault-pass
   ansible-playbook delete.yml --ask-vault-pass
   (Enter the password when prompted for vault password
