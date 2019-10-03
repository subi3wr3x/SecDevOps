![Ansible](ans.png)
## Why
- Push extra config to RSA delivered boxes.
- Flip from password auth to pubkey and then shut the door after validating no ssh config errors.
- Do it consistently :)

## Usage
```

ansible-playbook -i inventory vendor.yaml

```
