
![Kerberos](https://web.mit.edu/kerberos/images/dog-ring.jpg)


## What and Why
- From time to time one needs to do maintenance on principals in the Kerberos DB.
- Here we can remove flags from users or modify their encrpytion types in bulk.
- Bake in risk reduction by pausing if a back up is running.
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

## Sample Output
```
root@box2:~# ./krb5_modify.py  --tkt  XXXXXXXXXXX --ulist /tmp/users.txt --blist /tmp/blacklist.txt --project  disfwd --disfwd_action disable --disfwd_mode local
Execution Starting for TKT:XXXXXXXXXXX - disfwd:disable local
Processing user:user1@JOHNO.COM
Processing user:user2@JOHNO.COM
(snip for length)
Processing user:user99@JOHNO.COM
Processing user:user100@JOHNO.COM
Execution Completed for TKT: XXXXXXXXXXX
Summary ==> Success: 79, Errors: 0,Skipped-in-Error: 0,Skipped-Non-conform: 0,Skipped-Blacklist: 21,Is-Enabled: 79,Total: 100
```

## Sample Waiting for Backup
```
root@box2:~/gitrepos/SecDevOps/krb5modify# ./krb5_modify.py  --tkt  XXXXXXXXXXX --ulist /tmp/users.txt --blist /tmp/blacklist.txt --project  disfwd --disfwd_action disable --disfwd_mode local 
Execution Starting for TKT:XXXXXXXXXXX - disfwd:disable local
Processing user:user1@JOHNO.COM
user1@JOHNO.COM - backup_kdb5.sh running - sleeping for 240 seconds - count 1
user1@JOHNO.COM - backup_kdb5.sh running - sleeping for 240 seconds - count 2
user1@JOHNO.COM - backup_kdb5.sh running - sleeping for 240 seconds - count 3
user1@JOHNO.COM - backup_kdb5.sh running - sleeping for 240 seconds - count 4
Backup not running after 5 tries - user1@JOHNO.COM  to be processed next
Processing user:user1@JOHNO.COM
Processing user:user2@JOHNO.COM
```

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
