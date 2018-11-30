## Why
Splunk was giving us dirty/broken data. I could wait no longer to deco this infra.
- kdcdeco/kdc_logs_flatten.py	- Pull out selection portions of the MIT logs 
- kdcdeco/kdclogs2excel.py    - Consolidate and aggregrate the KDC data with Pandas.
- kdcdeco/kdc_deco.png - Pretty Pic of the Result
## Usage
- Collect up all your Infra logs into one dir 
- Make sure the logs have 'mit_kdc_log' in the name 
```

./kdc_logs_flatten.py
./kdclogs2excel.py

```

