import os
from collections import deque
import re
import sys
import csv
import getopt
import inspect
import pandas as pd
from pyexcel_ods import get_data
import pyexcel
import json


def PrintLog(message="Here....."):
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    print ("LOG: %s:, %s:, %s:, %s" %(info.filename, info.function, info.lineno, message))



log=open('log.csv','w')

dict_sorted={}
# find_data=[]

def concat_data(ind_arr):
    data_dict={}
    for key,value in dict_sorted.items():
        k=1
        temp_data1=""
        for data in ind_arr:
            # print(data,value)
            if(k==1):
                if(value[int(data)-1]=="NULL"):
                    value[int(data)-1]=" "
                temp_data1=str(value[int(data)-1])
            else:
                if(value[int(data)-1]=="NULL"):
                    value[int(data)-1]=" "
                temp_data1=temp_data1+"|"+str(value[int(data)-1])
            k=k+1        
        res=" (("+str(temp_data1)+")) "
        data_dict.update({key:res})
    return data_dict

def final_out(temp,output_file,ind_arr):
    # print(ind_arr)
    PrintLog(message="In final_out Module,Replacement from the specified index is performed.")
    f=open(output_file ,'w')
    final_dict={}
    final_dict.update(concat_data(ind_arr))
    for key,value in final_dict.items():
        for data in range(len(temp)):
            data=temp.popleft()
            if(data=='@@@'):
                temp.append('@@@')
                break
            result = re.sub(r"(\s|^)(%s)(\s|[-.,।!|?:;-~`'\"\[\]\(\)]|$)" %key, r"\1"+(str(value)).strip()+r"\3", data,0, re.MULTILINE | re.UNICODE | re.IGNORECASE)
            temp.append(result)
    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)
        f.write("\n")
    if os.path.exists("temp2.txt"):
        os.remove("temp2.txt")
    if os.path.exists("a.csv"):
        os.remove("a.csv")
    PrintLog("Done")

def sort_dict(dict_file,ind):
    # print(dict_file)
    data_dict={}
    new_d = dict(sorted(dict_file.items(), key=lambda i: -len(i[1][ind])))
    for key,value in new_d.items():
        if (value not in ['NULL']):
            data_dict.update({key:value[ind]})
    # print(data_dict)
    return data_dict


def subs(new_d,temp,col_count,output_file,ind_arr):
    PrintLog(message="In subs Module, data substitution started...")
    f=open('intermediate.txt','w')
    log_dict={}
    for col in range(col_count):
        make_dict={}
        make_dict.update(sort_dict(new_d,col))
        # print(make_dict)

        for key,values in make_dict.items():
            key=" "+str(key)+" "
            for data in range(len(temp)):
                data=temp.popleft()
                if(data=='@@@'):
                    temp.append('@@@')
                    break 
#Strings in any of the three given format is will be substituted i.e " str ","str "," str[.,।!|?:/]"
                result = re.sub(r"(\s|^)(%s)(\s|[-.,।!|?:;-~`'\"\[\]\(\)]|$)" %(values), r"\1"+(str(key)).strip()+r"\3", data,0, re.MULTILINE | re.UNICODE | re.IGNORECASE)
                if(re.search(r"(\s|^)(%s)(\s|[-.,।!|?:-;-~`'\"\[\]\(\)]|$)" %(values),data, re.MULTILINE | re.UNICODE | re.IGNORECASE)):
                    if values in log_dict.keys():
                        log_dict[values]=log_dict[values]+1
                        
                    else:
                        log_dict.update({values:1})
                
                temp.append(result)
    tot_rep,uniq_repl=0,0
    for data,value in log_dict.items():
        uniq_repl=uniq_repl+1
        tot_rep=tot_rep+value
        log.write(str(data))
        log.write("!@")
        log.write(str(value))
        log.write('\n')

    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)
        f.write("\n")
    PrintLog("Intermediate File is created")
    PrintLog("Terms replaced :"+str(tot_rep)+"("+str(uniq_repl)+" unique)")
    final_out(temp,output_file,ind_arr)

def make_data(text_file,src_text_file,output_file,ind_arr):
    PrintLog(message="data Preprocessing started(make_data module)...")
    dict_data=open(text_file,'r')
    src_file=open(src_text_file,'r')
    find=[]
    col_count=0
    j=1
    temp=[]
    mask_id=''
    for data in dict_data:
        if data.startswith('"'):
            data=data[1:-2]
        temp_data=[]
        find=data.split('!')
        for index in range(len(find)):
            if(find[index]):
                find[index]=(find[index]).strip()
            else:
                find[index]='NULL'
        if(j==1):
            col_count=len(find)-1
        # find_data.append(find)
        for index in range(1,len(find)):
            temp_data.append(str(find[index]))
        # main_data.append(temp_data)
        for data in range(len(temp_data)):
            if(temp_data[data] not in ['NULL','',' ']):
                a=[]
                a=temp_data[data].split()
                var=a[0]
                for q in a[1:]:
                    var=var+"_"+str(q)

                mask_id="#"+str(find[0])+"#"+str(var)+"#"
                # PrintLog(mask_id)
                break
        dict_sorted.update({mask_id:temp_data})
        j=j+1
    for src in src_file:
        src=src.strip()
        a=src.split(' ')
        data1=a[0]
        for data in a[1:]:
            if(data):
                data1=data1+" "+str(data)
        temp.append(str(data1))
    temp.append('@@@')
    temp=deque(temp)
    subs(dict_sorted,temp,col_count,output_file,ind_arr)
    

def start():
    ind_arr=[]
    text_file='temp2.txt'
    src_text_file='all.txt'
    dict_data_file='termbase-for-terminology-automation.csv'
    output_file='output.txt'
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'hi:r:o:v:',['ifile=','rule=', 'ofile=', 'help' ,'value='])
    except getopt.GetoptError:
        print ('array_subs.py -i <inputfile> -r <rulefile> -o <outputfile> -v <index>')
        sys.exit(2)

    
    for opt, arg in options:
        if opt in ('-h', '--help'):
            print("Usage: \
                \n -i --input file, \
                \n -r, --rule file, \
                \n -o, --output file, \
                \n -v, --index value, \
                \n -h, --help")
            print('coammand: \
            \n array_subs.py -i <inputfile> -r <rulefile> -o <outputfile> -v "<index1>,<index2>,..."')
            sys.exit(1)	
        elif opt in ('-v', '--value'):
            ind_arr = arg.split(',')
            PrintLog('index are=%s'%arg)
        elif opt in ('-i', '--ifile'):
            src_text_file = arg
            PrintLog('input file=%s'%arg)
        elif opt in ('-r', '--rule'):
            if(arg.endswith('.xlsx')):
                file = pd.read_excel(arg)
                file.to_csv('a.csv',sep="!",index=False)
                dict_data_file = 'a.csv'
            elif(arg.endswith('.ods')):
                data11 = get_data(arg)
                new_data11=json.dumps(data11)
                new_data11=json.loads(new_data11)
                key11=''
                for key11, value11 in new_data11.items() :
                    break
                pyexcel.save_as(array=new_data11[key11],dest_file_name="a.csv",dest_delimiter="!")
                dict_data_file = 'a.csv'

            else:
                dict_data_file = arg
            PrintLog('rule file=%s'%arg)
        elif opt in ('-o', '--ofile'):
            output_file = arg
            PrintLog('output file=%s'%arg)
    # print(ind_arr)

    
    with open(dict_data_file, mode="rU") as infile:
        reader = csv.reader(infile, dialect="excel")   
        with open(text_file, mode="w") as outfile:
            writer = csv.writer(outfile, delimiter='!')
            writer.writerows(reader)
    make_data(text_file,src_text_file,output_file,ind_arr)

start()
