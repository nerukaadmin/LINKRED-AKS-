import datetime
import os
import sys
import re
import traceback
import subprocess
import pandas as pd
import numpy as np
from pandas import ExcelWriter

stamp=datetime.datetime.now()
date=stamp.strftime("%Y-%m-%d")
time=stamp.strftime("%X")

arg=sys.argv[1]
df=pd.read_csv(arg,header=0)
df_list=df.values.tolist()
BP=[]
UP=[]
for i in df_list:
	pattern = re.compile(r"-BP")
	if pattern.search(str(i[0])):
	   i.append("Build-Place")
	   pattern_region_US= re.compile(r"US")
	   pattern_region_Canada= re.compile(r"Canada")
	   pattern_Eu=re.compile(r"Europe")
	   if pattern_region_US.search(str(i[5])) or pattern_region_Canada.search(str(i[5])):
	   	i.append("US")
	   	BP.append(i)
	   elif pattern_Eu.search(str(i[5])):
	   	i.append("Europe")
	   	BP.append(i)
	   else:
	   	i.append("APMJ")
	   	BP.append(i)
	else:
	   i.append("Use-Place")
	   pattern_region_US= re.compile(r"US")
	   pattern_region_Canada= re.compile(r"Canada")
	   pattern_Eu=re.compile(r"Europe")
	   if pattern_region_US.search(str(i[5])) or pattern_region_Canada.search(str(i[5])):
	   	i.append("US")
	   	UP.append(i)
	   elif pattern_Eu.search(str(i[5])):
	   	i.append("Europe")
	   	UP.append(i)
	   else:
	   	i.append("APMJ")
	   	UP.append(i)
bp_df=pd.DataFrame(BP)
up_df=pd.DataFrame(UP)
bp_df.sort_values(by=[5],inplace=True)
up_df.sort_values(by=[5],inplace=True)
bp_dfh=bp_df.rename(columns=bp_df.iloc[0]).drop(bp_df.index[0])
fdf_bp=pd.DataFrame(np.row_stack([bp_dfh.columns, bp_dfh.values]),columns=['Subscription_name', 'Sub_ID','AKS_Name','AKS_RG','AKS_Version','Location','linkerd-identity-issuer-valid-date','linkerd-proxy-injector-k8s-tls-valid-date','Cert_Status',"ENV-Type",'Region'])
up_dfh=up_df.rename(columns=up_df.iloc[0]).drop(up_df.index[0])
fdf_up=pd.DataFrame(np.row_stack([up_dfh.columns, up_dfh.values]),columns=['Subscription_name', 'Sub_ID','AKS_Name','AKS_RG','AKS_Version','Location','linkerd-identity-issuer-valid-date','linkerd-proxy-injector-k8s-tls-valid-date','Cert_Status','ENV-Type','Region'])
frames={'ALL':df,'Build-Place':fdf_bp,'Use-Place':fdf_up}
with pd.ExcelWriter('./final_list/Linkerd_final_sorted_'+str(date)+'.xlsx',mode="w",engine='xlsxwriter') as writer:
	for sheet, frame in  frames.items():
		frame.to_excel(writer, sheet_name = sheet,index=False)
print("Excel File created: "+'./final_list/Linkerd_final_sorted_'+str(date)+'.xlsx')