## Why
Splunk was giving us dirty/broken data. I could wait no longer to deco this infra.
- kdcdeco/kdc_logs_flatten.py	- Pull out selection portions of the MIT logs 
- kdcdeco/kdclogs2excel.py    - Consolidate and aggregrate the KDC data with Pandas.
- kdcdeco/kdc_deco.png - Pretty Pic of the Result
## Usage
- Make sure you've got enough disk for the logs
- Collect up all your Infra logs into one dir 
- Make sure the logs have 'mit_kdc_log' in the name or edit 'kdc_log_file_glob' in kdc_logs_flatten.py
```
./kdc_logs_flatten.py #creates "/tmp/kdc_all.txt"
./kdclogs2excel.py    #creates "/tmp/kdc_agg_ + TIME_STAMP + .xlsx"
```
## Sample Spreadsheet
![Sample Spreadsheet](kdc_deco.png?raw=true "Sample Spreadsheet")
