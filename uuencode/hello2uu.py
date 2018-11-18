#!/usr/bin/python3

""" Given a  file encoded with uu2hello.py, reverse it """

import sys
if len(sys.argv) < 2:
    print(sys.argv[0],"file")
    sys.exit
else:
    myfile=sys.argv[1]
    myfileout=sys.argv[1] + ".uue"

def main():
    try:
        with open(myfile) as fh:
            with open(myfileout,'w') as fh2:
                all_lines=fh.readlines()
                all_lines.insert(0,'begin 664 test.text.tar\n')  #Add back a unix line
                for line in all_lines:
                    line=line\
                    .replace('HELLO000','`').replace('HELLO001','~').replace('HELLO002','!')\
                    .replace('HELLO003','@').replace('HELLO04','#').replace('HELLO05','$')\
                    .replace('HELLO06','%').replace('HELLO07','^').replace('HELLO08','&')\
                    .replace('HELLO09','*').replace('HELLO010','(').replace('HELLO011',')')\
                    .replace('HELLO012','_').replace('HELLO013','-').replace('HELLO014','+')\
                    .replace('HELLO015','=').replace('HELLO016','{').replace('HELLO017','}')\
                    .replace('HELLO018','[').replace('HELLO019',']').replace('HELLO020','|')\
                    .replace('HELLO021','\\').replace('HELLO022',':').replace('HELLO023',';')\
                    .replace("HELLO024","'").replace('HELLO025','<').replace('HELLO026',',')\
                    .replace('HELLO027','>').replace('HELLO028','.').replace('HELLO029','?')\
                    .replace('HELLO030','/').replace('HELLO31','"').replace('HELLOKITTY','M')
                    fh2.write(line)
        with open(myfileout,'a') as fh3:
                fh3.write('`\n')    #Add back '`'
                fh3.write('end\n')   #Add back the 'end' line
    except Exception as e:
        print("Error:",e)

if __name__ == "__main__":
    main()
