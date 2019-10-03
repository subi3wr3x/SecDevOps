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

## Sample Log
```
root@box2:~# cat /tmp/krb5_modify_log_20191003004057.log
INFO 2019-10-03 00:40:57,468 krb5_modify 28848 Execution Starting for TKT:XXXXXXXXXXX - disfwd:disable local
INFO 2019-10-03 00:40:57,477 krb5modify 28848 PRE-EXEC-CHECK: user1@JOHNO.COM DISALLOW_ALL_TIX attribute is currently not set
INFO 2019-10-03 00:40:57,479 krb5modify 28848 QUERY: user1@JOHNO.COM DISALLOW_FORWARDABLE attribute is currently not set
INFO 2019-10-03 00:40:57,485 krb5modify 28848 ACTION: DISALLOW_FORWARDABLE was set OK for user1@JOHNO.COM
INFO 2019-10-03 00:40:57,488 krb5modify 28848 QUERY: user1@JOHNO.COM DISALLOW_FORWARDABLE attribute is currently set
INFO 2019-10-03 00:40:58,504 krb5modify 28848 PRE-EXEC-CHECK: user2@JOHNO.COM DISALLOW_ALL_TIX attribute is currently not set
INFO 2019-10-03 00:40:58,507 krb5modify 28848 QUERY: user2@JOHNO.COM DISALLOW_FORWARDABLE attribute is currently not set
INFO 2019-10-03 00:40:58,512 krb5modify 28848 ACTION: DISALLOW_FORWARDABLE was set OK for user2@JOHNO.COM
INFO 2019-10-03 00:40:58,514 krb5modify 28848 QUERY: user2@JOHNO.COM DISALLOW_FORWARDABLE attribute is currently set
INFO 2019-10-03 00:40:59,530 krb5modify 28848 PRE-EXEC-CHECK: user3@JOHNO.COM DISALLOW_ALL_TIX attribute is currently not set
INFO 2019-10-03 00:40:59,533 krb5modify 28848 QUERY: user3@JOHNO.COM DISALLOW_FORWARDABLE attribute is currently not set
```
