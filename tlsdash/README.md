#### tlsdash
Simple TLS Dashboard Creator

#### Usage
- This script consumes Virtual IP/host data and connects to the URL to extract a date.
- Dump relevant URL data
- Schedule tlsdash periodically 

#### Expectations
- In a large org the extract portion will be bespoke, there rest can be used as-is.
- Step 1 will be sourcing your TLS certs.  Here, a config db is assumed and uses a tls-dash.conf file in the format of: app:appid.
- Step 2 is running tls-dash-tls-crawler.py to crawl and collect the TLS expire dates. (with or with a web server fronting based on load)
- Step 3 is running tls-dash-flask.py (with or with a web server fronting based on load). You'll need to install ![Flask](http://flask.pocoo.org).

#### Screen Shot 
![TLS Dashboard](tlsdash.png?raw=true "TLS Dashboard")
