import datetime
import os
import sys
import csv


stamp=datetime.datetime.now()
date=stamp.strftime("%Y-%m-%d")
time=stamp.strftime("%X")



with open('linkerd_cus_list.csv', newline='', encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    data = list(reader)   
print(data)

for i in data:
	print(i)
	with open('aks_list.txt','a') as file:
		file.write(i[0]+"\n")

	with open('reg_list.txt','a') as file:
		file.write(i[1]+"\n")

	with open('subid_list.txt','a') as file:
		file.write(i[2]+"\n")

print("completed..!")		
