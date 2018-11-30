#### uuencode-py
Encode and decode uuencoded file using a mapping of your choosing (pentest,etc).

#### Usage
```
./uu2hello.py UUENCODED_FILE.UUE (creates UUENCODED_FILE.uue.hello
```

Send it somewhere...

```
./hello2uu.py UUENCODED_FILE.UUE.hello (creates UUENCODED_FILE.uue.hello.uue)
```
#### Expectations
- The original .uue file will differ from the final decoded UUENCODED_FILE.uue.hello.uue as it does not take the final name with it as that would be undesirable (if sent via an unencrypted transport)
- The final decode file will always be named test.text.tar


#### Examples
Take a .uue file, convert it and then convert back using the included 'test_uu.sh' (diffs are shown)

```
$cp /etc/passwd . 
$uuencode passwd pw > passwd.uue
./test_uu.sh passwd.uue
79ad1ac23a62220c59c4958a65ee9790cb744658d48132132f544f57b851543c  passwd.uue
fd0e713b20b8807a1df853863f2683e365262ee4bd849b695d501abced79c8da  passwd.uue.hello.uue
1c1

< begin 644 pw
---
> begin 664 test.text.tar
```
The files differ only by the inital unix file name line.
