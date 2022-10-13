#!/bin/sh
k8s_context=$1
sub=$2
rg=$3
#echo $k8s_context
#echo $sub
#echo $rg
az account set --subscription ${sub}
az aks get-credentials --resource-group ${rg} --name ${k8s_context}
kubectl config use-context ${k8s_context}