## Why
- From time to time one needs to do maintenance on principals in the Kerberos DB.
- Here we can remove flags from users or modify their encrpytion types in bulk.
- Do it consistently :)

## Usage
```
root@box2:~# ./krb5_modify.py -h
usage: krb5_modify.py [-h] --tkt XXXXXX [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]

optional arguments:
  -h, --help          show this help message and exit
  --tkt             XXXXXX
  --project         [desdeco|disfwd]
  --blist           /tmp/blacklist.txt
  --ulist           /tmp/users.txt
  --disfwd_action   [disable|restore]
  --disfwd_mode     [remote|local]
  --desdeco_action  [strengthen|restore]
```
