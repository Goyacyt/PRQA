
import os
import time
from tools.askchatGPT import *
import sys
sys.path.append(".")
sys.path.append("./tools")

def programming_language():
    run=0
    count=0
    outfile=open("programresult3.txt","w",encoding="utf-8")
    for root, dirs, files in os.walk(".\p04043", topdown=False):
        for name in files:
            if ".cpp.gcov" in name:
                count+=1
                filecpp=root+"/"+name[:-5]
                filegcov=root+"/"+name
                filetxt=root+"/"+name[:-9]+".txt"
                filec=root+"/"+name[:-7]
                print(filecpp,filegcov,filetxt,count)
                if filecpp==".\p04043/s363199795.cpp":
                    run=1
                if not run:
                    continue
                f=open(filecpp,"r",encoding='utf-8')
                cppline=f.readlines()
                f=open(filegcov,"r",encoding='utf-8')
                gcovline=f.readlines()
                not_cover=[]
                for id,line in enumerate(gcovline):
                    line.replace(" ","").replace("\n","").replace("\r","")
                    #print(line)
                    change=line.startswith('    #####')
                    if change:
                        part=line.split(":")
                        #print("part: ",part)
                        not_cover.append((int)(part[1]))
                if not_cover!=[]:
                    cppline[0]="#include<assert.h>\n"+cppline[0]
                for notcoverid in not_cover:
                    if (";" in cppline[notcoverid-1]) and ("{" not in cppline[notcoverid-1]) and ("}" not in cppline[notcoverid-1]):
                        cppline[notcoverid-1]="{"+cppline[notcoverid-1]+"assert(0);}"
                cppmod=''.join(cppline)
                f=open(filec,"w",encoding='utf-8')
                print(cppmod,file=f)
                f=open(filetxt,"r",encoding='utf-8')
                input=f.read()
                input.replace("\n","").replace("\r","")
                print(input)
                print(cppmod)
                messages = [
                    {"role": "user", "content": cppmod},
                    {"role":"user","content":f"The input is {input}. Will this program trigger the assertion?Answer yes or no in one word."},
                ]
                res=askGPT(messages).lower()
                print(res)
                if "yes" in res:
                    print("here is a mistake!")
                    print(filecpp,file=outfile)
                    print(cppmod,file=outfile)
                    print("\n",file=outfile)
                    print("input:",input,file=outfile)
                    print("chatgpt answer",res,file=outfile)
                    print("\n",file=outfile)
                time.sleep(20)

            
                


if __name__=='__main__':
    #text(args=args)
    #answerAnalysis(args=args)
    programming_language()