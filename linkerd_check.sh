[#!/bin/sh
 today=$(date +%m-%d-%Y)
 touch aks_list.txt
 touch subid_list.txt
 touch reg_list.txt
 python3 lst_gen.py
 sed -i '/^[[:space:]]*$/d' aks_list.txt
 sed -i '/^[[:space:]]*$/d' subid_list.txt
 sed -i '/^[[:space:]]*$/d' reg_list.txt
 sed -i -e 's/\r$//' linkerd_check.sh
 sed -i -e 's/\r$//' aks_list.txt
 sed -i -e 's/\r$//' subid_list.txt
 sed -i -e 's/\r$//' reg_list.txt
 #aks_lst=$(cat aks_list.txt |tr "\n" " ")
 #aks_arr=($aks_lst)
 mapfile -t aks < aks_list.txt
 aks_arr=("${aks[@]}")
 #subid_lst=$(cat subid_list.txt |tr "\n" " ")
 #subid_arr=($subid_lst)
 mapfile -t subid < subid_list.txt
 subid_arr=("${subid[@]}")
 #reg_lst=$(cat reg_list.txt |tr "\n" " ")
 #reg_arr=($reg_lst)
 mapfile -t reg < reg_list.txt
 reg_arr=("${reg[@]}")
 log_path="./final_list"
 printf "%s\n" "${aks_arr[@]}"
 printf "%s\n" "${subid_arr[@]}"
 printf "%s\n" "${reg_arr[@]}"
 
 i=0
 while [ $i -lt ${#aks_arr[*]} ]; do
     echo $i
     k8s_context=${aks_arr[$i]}
     sub=${subid_arr[$i]}
     rg=${reg_arr[$i]}
     echo $k8s_context
     echo $sub
     echo $rg
     az account set --subscription ${sub}
     az aks get-credentials --resource-group ${rg} --name ${k8s_context}
     loc=$(az group show -g ${rg} --query "[location]" -o tsv)
     kubectl config use-context ${k8s_context}
     notAfter=$(kubectl -n ifs-ingress get secret linkerd-identity-issuer  -o json | jq -r '.data."crt.pem"' | base64 -d | openssl x509 -enddate -noout)
     aksv=$(kubectl get no -o=jsonpath='{.items[0].status.nodeInfo.kubeletVersion}')
     datestr=${notAfter/notAfter=/}
     enddate=$(date --date="$datestr" --utc +"%m-%d-%Y")
     if [[ "$enddate" < "$today" ]];then
        echo Linkerd cert already expired on $enddate.
        echo k8s version $aksv
        echo AKS Location $loc
        echo $k8s_context,$sub,$rg,$enddate,$aksv,$loc >> $log_path/likerd_cert_issue.csv
    elif [[ "$enddate" > "$today" ]];then
        echo cert not expired in the $k8s_context.
        echo Cert Will be expired on $enddate
        echo k8s version $aksv
        echo AKS Location $loc
        echo $k8s_context,$sub,$rg,$enddate,$aksv,$loc >> $log_path/likerd_cert_ok.csv
    else
        echo cert not expired in the $k8s_context.
        echo Cert Will be expired on $enddate
        echo k8s version $aksv
        echo AKS Location $loc
        echo $k8s_context,$sub,$rg,$enddate,$aksv,$loc >> $log_path/likerd_cert_ok.csv    
    fi
    i=$(( $i + 1));
done
rm aks_list.txt
rm subid_list.txt
rm reg_list.txt