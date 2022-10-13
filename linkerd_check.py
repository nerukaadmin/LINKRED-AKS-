import datetime
import os
import sys
import csv
import subprocess
import base64
import json
import ssl
import time
import OpenSSL
from kubernetes import client, config
from x5092json import x509parser
from collections import OrderedDict

stamp=datetime.datetime.now()
date=stamp.strftime("%Y-%m-%d")
time=stamp.strftime("%X")
nstamp=int(datetime.datetime.utcnow().timestamp())


with open('linkerd_cus_list.csv', newline='', encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    data = list(reader)   
print(data)
#subprocess.run(["az", "login"])
fie_name=str(nstamp)
header=["Subscription_name","Sub_ID","AKS_name","AKS_RG","AKS_version","Location","linkerd-identity-issuer-vailid-date","linkerd-proxy-injector-k8s-tls-valid-date","Cert_Status"]
with open('./final_list/Linkerd_final_check_'+fie_name+'.csv','w') as fd:
	writer = csv.writer(fd)
	writer.writerow(header)
fd.close()	

for i in data:
	print(i)
	#subprocess.run(["az", "account", "set", "--subscription", i[2]])
	#subprocess.run(["az",  "aks", "get-credentials", "--resource-group", i[3], "--name", i[0]])
	#subprocess.run(["kubectl", "config", "use-context", i[0]])
	k8sinit_sub=subprocess.Popen(["./initk8s.sh", i[0], i[2], i[3]],stdout=subprocess.PIPE)
	init_out, err=k8sinit_sub.communicate()
	config.load_kube_config()
	v1 = client.CoreV1Api()
	node_sub=subprocess.Popen(["kubectl", "get", "no", "-o=jsonpath='{.items[0].status.nodeInfo.kubeletVersion}'"],stdout=subprocess.PIPE)
	out, err=node_sub.communicate()
	k8s_version=str(out.decode())
	sec1 = v1.read_namespaced_secret("linkerd-identity-issuer", "ifs-ingress").data
	cert1 = base64.b64decode(sec1["crt.pem"])
	cert1_x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert1)
	exp1=cert1_x509.get_notAfter()
	hdt1=datetime.datetime.strptime(exp1.decode('utf-8'), '%Y%m%d%H%M%SZ').date()
	dt1=datetime.datetime.strptime(exp1.decode('utf-8'), '%Y%m%d%H%M%SZ').timestamp()
	linkerd_identity_issuer_exp=int(dt1)

	sec2 = v1.read_namespaced_secret("linkerd-proxy-injector-k8s-tls", "ifs-ingress").data
	cert2 = base64.b64decode(sec2["tls.crt"])
	cert2_x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert2)
	exp2=cert2_x509.get_notAfter()
	hdt2=datetime.datetime.strptime(exp2.decode('utf-8'), '%Y%m%d%H%M%SZ').date()
	dt2=datetime.datetime.strptime(exp2.decode('utf-8'), '%Y%m%d%H%M%SZ').timestamp()
	linkerd_proxy_injector_k8s_tls=int(dt2)

	#print("linkerd_identity_issuer_exp :"+ str(hdt1))
	#print("linkerd_proxy_injector_k8s_tls:"+ str(hdt2))
	#print (linkerd_identity_issuer_exp)
	#print(linkerd_proxy_injector_k8s_tls)
	#print(nstamp)

	if nstamp > linkerd_identity_issuer_exp or nstamp > linkerd_proxy_injector_k8s_tls:
		print("Cert has been Expired")
		print("linkerd_identity_issuer_exp :"+ str(hdt1))
		print("linkerd_proxy_injector_k8s_tls:"+ str(hdt2))
		sub_name=str(i[6])
		AKS_name=str(i[0])
		Location=str(i[5])
		AKS_version=str(i[4])
		AKS_RG=str(i[3])
		sub_id=str(i[2])
		print("Sub name: "+str(i[6]))
		print("AKS Name: "+str(i[0]))
		print("Location: "+str(i[5]))
		print("AKS version: "+str(i[4]))
		print("AKS RG: "+str(i[3]))
		row=[sub_name,sub_id,AKS_name,AKS_RG,k8s_version,Location,str(hdt1),str(hdt2),"Expired"]
		with open('./final_list/Linkerd_final_check_'+fie_name+'.csv','a') as fd:
			writer = csv.writer(fd)
			writer.writerow(row)
		row.clear()	
	else:
		print("Cert is upto date..!")
		print("linkerd_identity_issuer_exp :"+ str(hdt1))
		print("linkerd_proxy_injector_k8s_tls:"+ str(hdt2))
		sub_name=str(i[6])
		AKS_name=str(i[0])
		Location=str(i[5])
		AKS_version=str(i[4])
		AKS_RG=str(i[3])
		sub_id=str(i[2])
		print("Sub name: "+str(i[6]))
		print("AKS Name: "+str(i[0]))
		print("Location: "+str(i[5]))
		print("AKS version: "+str(i[4]))
		print("AKS RG: "+str(i[3]))
		row=[sub_name,sub_id,AKS_name,AKS_RG,k8s_version,Location,str(hdt1),str(hdt2),"Up to Date"]
		with open('./final_list/Linkerd_final_check_'+fie_name+'.csv','a') as fd:
			writer = csv.writer(fd)
			writer.writerow(row)
		row.clear	
	
print("--- %s seconds ---" % (datetime.datetime.now() - stamp))