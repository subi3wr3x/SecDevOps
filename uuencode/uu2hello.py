#!/usr/bin/python3

import sys
if len(sys.argv) < 2:
    print(sys.argv[0],"file")
    sys.exit
else:
    myfile=sys.argv[1]
    myfileout=sys.argv[1] + ".hello"

#TBD: Change always changing the first char from M to HK to subbing M to HK
#there could be a '%' somewhere...

try:
    with open(myfile) as fh:
            all_lines=fh.readlines()
            all_lines = all_lines[:-1] # Remove Final 'end' line
            all_lines = all_lines[:-1] # Remove second to last  '`' line
            all_lines = all_lines[1:]  # Remove Inital Unix line
            with open(myfileout,'w') as fh2:
                for line in all_lines:
                    if line.startswith('M'):
                        line = "HELLOKITTY" + line[1:] #Change to suit your needs
                    line=line\
                    .replace('`','HELLO000').replace('~','HELLO001').replace('!','HELLO002')\
                    .replace('@','HELLO003').replace('#','HELLO04').replace('$','HELLO05')\
                    .replace('%','HELLO06').replace('^','HELLO07').replace('&','HELLO08')\
                    .replace('*','HELLO09').replace('(','HELLO010').replace(')','HELLO011')\
                    .replace('_','HELLO012').replace('-','HELLO013').replace('+','HELLO014')\
                    .replace('=','HELLO015').replace('{','HELLO016').replace('}','HELLO017')\
                    .replace('[','HELLO018').replace(']','HELLO019').replace('|','HELLO020')\
                    .replace('\\','HELLO021').replace(':','HELLO022').replace(';','HELLO023')\
                    .replace("'","HELLO024").replace('<','HELLO025').replace(',','HELLO026')\
                    .replace('>','HELLO027').replace('.','HELLO028').replace('?','HELLO029')\
                    .replace('/','HELLO030').replace('"','HELLO31')
                    fh2.write(line)
except Exception as e:
    print("Error:",e)
