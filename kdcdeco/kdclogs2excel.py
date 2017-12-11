#!/usr/bin/python3

""" Create an MS Excel Chart for Chasing stragglers            """
""" Send it to your proj mgr / client mgrs                     """
""" A la https://stackoverflow.com/questions/47722603/pandas\  """ 
""" -to-csv-not-save-index-values-repeatedly/47722671#47722671 """

import time
import xlsxwriter                                                                
import numpy as np                                                                
import pandas as pd                                                                

log_dir='/tmp/kdc-deco/'                                                                
log_file='kdc_all.txt'                                                                
timestr = time.strftime("%Y%m%d-%H%M%S")                                                                
df = pd.read_csv(log_dir + log_file,sep='|',names=['Time','KDC','IP','Host','ClntPrinc','SrvPrinc'])  
#Filter if you need to...
df = df[df['ClntPrinc'].str.contains('crazy')==False]                                                                            
df = df[df['Host'].str.contains('kdc')==False]                                                                                
df.set_index('Host',inplace=True)                                                                                        
df.groupby(['Host', 'ClntPrinc', 'SrvPrinc']).SrvPrinc.agg('count').to_excel('/tmp/kdc_no_spot_agg_' + timestr + '.xlsx','kdc-deco',engine='xlsxwriter')                                                                                            
