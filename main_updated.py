from collections import deque
import re
import sys

opt=""
try:
    opt=sys.argv[1]
except:
    pass

#find and replace data file
dict_data_file='two-coloumn-array.txt'

#data file
src_text_file='sample-input-file-test.txt'

dict_data=open(dict_data_file,'r')
src_file=open(src_text_file,'r')

dict_sorted={}
mask_dict={}
new_d = {}
span_dict={}
temp=[]

def make_span(hid_text,showed_text):
    prefix=' <span style="color:blue" onmouseover="" title="'
    mid='">'
    suffix='</span> '
    return(prefix+hid_text+mid+showed_text+suffix)

mask=' ###ZZZ'
i=1
for data in dict_data:
    mask_key=mask+str(i)+" "
    find_data,replace_data=data.split(',')
    find_data=str(find_data.strip())
    replace_data=str(replace_data.strip())
    replace_data=" "+str(replace_data)+" "    
    dict_sorted.update({mask_key.strip():replace_data})
    mask_dict.update({find_data:mask_key})
    span_text=str(make_span(replace_data,find_data))
    span_dict.update({mask_key.strip():span_text})
    i=i+1

for k in sorted(mask_dict, key=len, reverse=True):
    new_d[k] = mask_dict[k]


for src in src_file:
    temp.append(str(src))
temp.append('@@@')
temp=deque(temp)

for row in new_d:
    for data in range(len(temp)):
        data=temp.popleft()
        if(data=='@@@'):
            temp.append('@@@')
            break
        result = re.sub(r"\s(%s)\s|\s(%s)[.,।!|?]|^(%s)\s" %row, new_d[row], data,0, re.MULTILINE | re.UNICODE | re.IGNORECASE)
        temp.append(result)

if(opt=='span'):
    f=open('output.html','w')
    for row in span_dict:
        for data in range(len(temp)):
            data=temp.popleft()
            if(data=='@@@'):
                temp.append('@@@')
                break
            result = re.sub(r"\s(%s)\s" %row, span_dict[row], data,0, re.MULTILINE | re.UNICODE)
            temp.append(result)
    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)


else:
    f=open('output.txt','w')
    for row in dict_sorted:
        for data in range(len(temp)):
            data=temp.popleft()
            if(data=='@@@'):
                temp.append('@@@')
                break
            result = re.sub(r"\s(%s)\s" %row, dict_sorted[row], data,0, re.MULTILINE | re.UNICODE)
            temp.append(result)
    for d in temp:
        d=d.replace('@@@','')
        d=d.strip()
        f.write(d)
