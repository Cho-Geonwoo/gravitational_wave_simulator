import math

ttime=[]
for i in range(5000):
    ttime.append(10/5000.*i)

f1 = open("waveform1.txt", "w")
def wave(t):
    return 1/2*math.sin(t)
template=[]

for i in range(len(ttime)):
    template.append(wave(ttime[i]))
    f1.write("%.30f\n"%(wave(ttime[i])))
    
f1.close()