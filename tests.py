from flash import FlashDrum
import numpy as np
from math import sinh, cosh
from scipy.integrate import quad

def Antoine(T, A, B, C):

    P = pow(10 , (A - (B / ((T - 273.15) + C))))
    return round(P * .133322, 2 ) # kPa

def AntoineInv(P, A, B, C):

    T = ((B / (A - np.log10(P/.133322))) - C) + 273.15
    return round(T, 2) # K

def HeatVap(T, Tc, C1, C2, C3, C4):

    Tr = T / Tc
    Hvap = C1 * (1 - Tr) ** (C2 + C3 * Tr + C4 * Tr * Tr)
    return round(Hvap, 2) # J / kmol

def CP_L(T, C1, C2, C3, C4, C5):

    CPL = C1 +( C2 * T) +( C3 * (T ** 2)) +( C4 * (T ** 3)) + (C5 * (T ** 4))
    return round(CPL, 2) # J / kmol K

def CP_ig(T, C1, C2, C3, C4, C5):

    CPIG = C1 + C2 * pow((C3 / T) / (sinh(C3 / T)), 2) + C4 * pow((C5 / T) / (cosh(C5 / T)), 2)
    return round(CPIG, 2) # J / kmol K

def meanCP(f, T1, T2, ar):

    mcp, err = quad(f, T1, T2, args = ar)
    mcp = mcp / (T2 - T1)
    return mcp # J / kmol K



if __name__ == '__main__':
    flash = FlashDrum()
    C1 = 'Benzene'
    C2 = 'Toluene'
    z = {C1: 0.0, C2: 1.0}
    aB = {'A':6.89272, 'B':1203.531, 'C':219.888}
    aT = {'A':6.95805, 'B':1346.773, 'C':219.693}
    vB = {'Tc': 562.05 , 'C1': 4.5346e7, 'C2': 0.39053, 'C3': 0, 'C4': 0}
    vT = {'Tc': 591.75 , 'C1': 4.9507e7, 'C2': 0.37742, 'C3': 0, 'C4': 0}
    cplB = {'C1' : 162940, 'C2': -344.94, 'C3' : 0.85562, 'C4' : 0, 'C5': 0}
    cplT = {'C1' : 140140, 'C2': -152.3, 'C3' : 0.695, 'C4' : 0, 'C5': 0}
    cpigB = {'C1' : 0.44767e5, 'C2': 2.3085e5, 'C3' : 1.4792e3, 'C4' : 1.6836e5, 'C5': 677.66}
    cpigT = {'C1' : 0.5814e5, 'C2': 2.863e5, 'C3' : 1.4406e3, 'C4' : 1.898e5, 'C5': 650.43}
    f = {'Antoine': Antoine, 'AntoineInv' : AntoineInv, 'Hvap' : HeatVap, 'CPL': CP_L, 'CPig' : CP_ig, 'meanCP':meanCP}
    fp = {'Antoine': {C1: aB, C2: aT}, 'AntoineInv' : {C1: aB, C2: aT}, 'Hvap' : {C1: vB, C2: vT}, 'CPL': {C1: cplB, C2: cplT}, 'CPig': {C1: cpigB, C2: cpigT}}

    feedStream = {'molar flow': 100,
                'composition': z}

    flash.setFeedStream(feedStream)
    flash.getFeedStream()

    #T = flash.dewT(101.325, f, fp)
    #print("{:.2f}".format(T-273.15))  
    P = flash.dewP(110.62+273.15,f,fp)
    print(P)
 
