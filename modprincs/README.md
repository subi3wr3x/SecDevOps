## Why
- From time to time one needs to do maintenance on principals in the Kerberos DB.
- Here we can remove flags from users or modify their encrpytion types in bulk.
- Do it consistently :)

## Usage
```
./y -h 
usage: modprincs.py [-h] [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]

Your Text Here

optional arguments:
  -h, --help  show this help message and exit
  --ulist   /tmp/users.txt
  --blist   /tmp/blacklist.txt
```
