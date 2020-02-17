from collections import deque
import re
import sys
import csv
import getopt
import inspect

def PrintLog(message="Here....."):
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    print ("LOG: %s:, %s:, %s:, %s" %(info.filename, info.function, info.lineno, message))



#find and replace data file
dict_data_file='termbase-for-terminology-automation.csv'

text_file='temp2.txt'
#data file
src_text_file='all.txt'

log=open('log.csv','w')

opt=[]
dict_sorted={}
find_data=[]

def concat_data():
    data_dict={}
    for key,value in dict_sorted.items():
        k=1
        temp_data1=""
        for data in opt:
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

def final_out(temp):
    f=open(outfile,'w')
    final_dict={}
    final_dict.update(concat_data())
    for key,value in final_dict.items():
        for data in range(len(temp)):
            data=temp.popleft()
            if(data=='@@@'):
                temp.append('@@@')
                break
            result = re.sub(r"\s(%s)\s" %key, value, data,0, re.MULTILINE | re.UNICODE)
            temp.append(result)
    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)
        f.write("\n")

def sort_dict(dict_file,ind):
    # print(dict_file)
    data_dict={}
    new_d = dict(sorted(dict_file.items(), key=lambda i: -len(i[1][ind])))
    for key,value in new_d.items():
        if (value not in ['NULL']):
            data_dict.update({key:value[ind]})
    # print(data_dict)
    return data_dict


def subs(new_d,temp,col_count):
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
                result = re.sub(r"\s(%s)\s" %values, key, data,0, re.MULTILINE | re.UNICODE)
                if(re.search(r"\s(%s)\s" %values,data, re.MULTILINE | re.UNICODE)):
                    if values in log_dict.keys():
                        log_dict[values]=log_dict[values]+1
                        
                    else:
                        log_dict.update({values:1})
                
                temp.append(result)
    for data,value in log_dict.items():
        log.write(str(data))
        log.write("!@")
        log.write(str(value))
        log.write('\n')

    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)
        f.write("\n")
    final_out(temp)

def make_data():
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
        print(data)
        temp_data=[]
        find=data.split('!')
        for index in range(len(find)):
            if(find[index]):
                find[index]=(find[index]).strip()
            else:
                find[index]='NULL'
        if(j==1):
            col_count=len(find)-1
        find_data.append(find)
        for index in range(1,len(find)):
            temp_data.append(str(find[index]))
        # main_data.append(temp_data)
        for data in range(len(temp_data)):
            if(temp_data[data] not in ['NULL','',' ']):
                mask_id="#"+str(find[0])+"#"+str(temp_data[data])+"#"
                # print(mask_id)
                break
        dict_sorted.update({mask_id:temp_data})
        j=j+1
    for src in src_file:
        temp.append(str(src))
    temp.append('@@@')
    temp=deque(temp)
    subs(dict_sorted,temp,col_count)
    

def start():
    options, remainder = getopt.getopt(sys.argv[1:], 'hi:r:o:',
                                  ['ifile=','rule=', 'ofile=', 'help'])
#print 'OPTIONS   :', options
    for opt, arg in options:
        if opt in ('-i', '--ifile'):
            src_text_file = arg
        elif opt in ('-r', '--rule'):
            dict_data_file = arg 
        elif opt in ('-o', '--ofile'):
            outfile = arg
        elif opt in ('-h', '--help'):
            help = True

    if (help == True):
        print("Usage: \
                \n -i --input file, \
            \n -r, --rule file, \
            \n -o, --output file, \
            \n -h, --help")
        sys.exit(1)	 
    PrintLog("Command line processed...")
    #print 'Command line arguments: ', sys.argv[1:]
        if(len(sys.argv)>=2):
            with open(dict_data_file, mode="rU") as infile:
                reader = csv.reader(infile, dialect="excel")   
                with open(text_file, mode="w") as outfile:
                    writer = csv.writer(outfile, delimiter='!')
                    writer.writerows(reader)
            for i in range(1,len(sys.argv)):
                opt.append(sys.argv[i])
        else:
            print('Unsufficient arguments')
            return
    make_data()

start()