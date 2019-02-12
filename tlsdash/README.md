#### tlsdash
Simple TLS Dashboard Creator

#### Usage
- This script consumes Virtual IP/host data and connects to the URL to extract a date.
- Dump relevant URL data
- Schedule tlsdash periodically 

#### Expectations
- In a large org the extract portion will be bespoke, there rest can be used as-is.
- Step 1 will be sourcing your TLS certs. Here, a config db is assumed.
- Step 2 is running tls-dash-flask.py (with or with a web server fronting based on load)

#### Screen Shot 
![TLS Dashboard](tlsdash.png?raw=true "TLS Dashboard")
