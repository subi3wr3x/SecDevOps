#!/usr/bin/python3

import os
import sys
import time
import pickle
import ms.version

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

app = Flask(__name__)
app.debug = True

@app.route('/tlsdash/<app>')
def ssl_status(app):
    file = app + ".pickle"
    try:
        with open(file,'rb') as fh:
            dshdict=pickle.load(fh)
            OKOK=dshdict[  'OK'    ]
            OKOK.sort(key=lambda x : int(x[3]))
            #Don't sort numerically if all are 'NA'
            SOON=dshdict[  'SOON'  ]
            if len(set(SOON)) <=1:
                pass
            else:
                SOON.sort(key=lambda x : int(x[3]))
            DECO=dshdict[  'DECO'  ]
            if len(set(DECO)) <=1:
                pass
            else:
                DECO.sort(key=lambda x : int(x[3]))
            #Failed Certs won't will have 'NA' vs a number of days
            FAIL=dshdict[ 'FAILED' ]
            FAIL.sort(key=lambda x : x[3])
    except Exception as e:
            print("File Problem: " + str(e))
            sys.exit(6)
    return render_template('tls-dash.html', SOON=SOON,OKOK=OKOK,DECO=DECO,FAIL=FAIL)

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
