import math

ttime=[]
for i in range(5000):
    ttime.append(9.00+0.98/5000.*i)

c = 2.99792458e8                # m/s
# Newton's gravitational constant
G = 6.67259e-11                      # m^3/kg/s^2 
# one parsec, popular unit of astronomical distance (around 3.26 light years)
parsec = 3.08568025e16              # m
# solar mass
MSol = 1.989e30                      # kg
# solar mass in seconds (isn't relativity fun?):
tSol = MSol*G/c**3     # s
m1 = 36*MSol
m2 = 29*MSol
mtot = m1+m2  # the total mass
eta = (m1*m2)/mtot**2
mchirp = ((m1*m2)**(3./5.))/((m1+m2)**(1./5.))
R = 500*10**6*parsec
f1 = open("waveform.txt", "w")
a = len(ttime)
print mchirp/MSol
def wave(t):
    amplitude = (-G*mchirp)/(c**2*R)
    constant = (c**3*(10-t)/(5*G*mchirp))**(-0.25)
    wave = math.cos(math.pi-2*((c**3*(10-t))/(5.*G*mchirp))**(5./8.))
    return amplitude*constant*wave*10**22/20.
template=[]

for i in range(len(ttime)):
    template.append(wave(ttime[i]))
    f1.write("%.30f\n"%(wave(ttime[i])))
    
f1.close()