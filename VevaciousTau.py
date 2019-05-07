import numpy as np
import os
y=np.linspace(1000,10000,10)
x=np.linspace(0,30000,30)
results=list()
extrater=1000/50
At=x[:]+1000/50
print(At)
for i in range(0,len(y)):
   for j in range(0,len(At)):
        if ((y[i]>0.3*x[j]-500 and y[i]<0.3*x[j]+1500)):
            with open("./SPheno-4.0.3/LesHouches.in.MSSM","r") as file:
                data=file.readlines()
            if y[i]<3000:
                data[4]='# 12 2000\n'
            else:
                data[4]=' 12 2000\n'
            data[17]=' 11 '+str(At[j])+' #Atinput \n'
            data[18]=' 12 '+str(At[j])+' #Abinput \n'
            data[19]=' 13 '+str(At[j])+' #Atauinput \n'
            data[96]=' 1 1 '+str(y[i]**2)+'         # md2(1,1)\n'
            data[100]=' 2 2 '+str(y[i]**2)+'         # md2(2,2)\n'
            data[104]=' 3 3 '+str(y[i]**2)+'         # md2(3,3)\n'

            data[106]=' 1 1 '+str(y[i]**2)+'         # me2(1,1)\n'
            data[110]=' 2 2 '+str(y[i]**2)+'         # me2(2,2)\n'
            data[114]=' 3 3 '+str(y[i]**2)+'         # me2(3,3)\n'

            data[116]=' 1 1 '+str(y[i]**2)+'         # ml2(1,1)\n'
            data[120]=' 2 2 '+str(y[i]**2)+'         # ml2(2,2)\n'
            data[124]=' 3 3 '+str(y[i]**2)+'         # ml2(3,3)\n'

            data[126]=' 1 1 '+str(y[i]**2)+'         # mq2(1,1)\n'
            data[130]=' 2 2 '+str(y[i]**2)+'         # mq2(2,2)\n'
            data[134]=' 3 3 '+str(y[i]**2)+'         # mq2(3,3)\n'

            data[136]=' 1 1 '+str(y[i]**2)+'         # mu2(1,1)\n'
            data[140]=' 2 2 '+str(y[i]**2)+'         # mu2(2,2)\n'
            data[144]=' 3 3 '+str(y[i]**2)+'         # mu2(3,3)\n'



            with open("./SPheno-4.0.3/LesHouches.in.MSSM","w") as file:
                file.writelines( data )
            os.chdir('./SPheno-4.0.3')
            os.system('./bin/SPhenoMSSM ')
            os.chdir('../')
            mycmd='./Vevacious-1.2.03/Vevacious/bin/Vevacious.exe --input=./VevaciousInitializationTau.xml'
            os.system(mycmd)
	    exists=os.path.isfile('./Tau.vout')
            if exists:            
                with open("./Tau.vout","r") as file:
                    data=file.readlines()
                print(data[3])
                if data[3]=='  <quantum_stability> long-lived </quantum_stability>\n':
                    results.append([x[j],y[i],1])
                elif data[3]=='  <quantum_stability> short-lived </quantum_stability>\n':
                    results.append([x[j],y[i],0])
                else:
                    results.append([x[j],y[i],2])
            else:
                results.append([x[j],y[i],3])

with open('./resultsTau.txt', 'w+') as filehandle:
    filehandle.writelines("%s\n" % place for place in results)
print(results)
