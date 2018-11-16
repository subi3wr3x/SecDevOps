In [146]: cat myfile
?email=test2@fake.some1.com
?email=test1@fake.some2.org
?email=test1@fake.some3.info
?email=test1@some4.net


In [147]: import re
     ...: infile="myfile"
     ...: outfile="myfile.redacted"
     ...: #Basic Pattern, can be more complex 
     ...: pattern=re.compile("\?email=(\w+)@(\w+\.\w+(\.\w+)?)")
     ...: with open(infile) as fh:
     ...:     with open(outfile,'w') as fh2:
     ...:         contents=fh.readlines()
     ...:         for line in contents:
     ...:             match = pattern.search(line)
     ...:             user=match.group(1)
     ...:             domain=match.group(2)
     ...:             fh2.write("X"*5 + "@" + domain +"\n") #hardcode vs len() of user
     ...:             
     ...:             
     ...:             


In [148]: cat myfile.redacted
XXXXX@fake.some1.com
XXXXX@fake.some2.org
XXXXX@fake.some3.info
XXXXX@some4.net
