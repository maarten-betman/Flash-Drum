from flash import FlashDrum
import numpy as np
from math import sinh, cosh
from scipy.integrate import quad
from stream import Stream

def Antoine(T, A, B, C):

    P = pow(10 , (A - (B / ((T - 273.15) + C))))
    return (P * 0.133322) # kPa

def AntoineInv(P, A, B, C):

    T = ((B / (A - np.log10(P/0.133322))) - C) + 273.15
    return round(T, 2) # K

def HeatVap(T, Tc, C1, C2, C3, C4):

    Tr = T / Tc
    Hvap = C1 * (1 - Tr) ** (C2 + C3 * Tr + C4 * Tr * Tr)
    return round(Hvap/1e6, 2) # J / mol

def CP_L(T, C1, C2, C3, C4, C5):

    CPL = C1 +( C2 * T) +( C3 * (T ** 2)) +( C4 * (T ** 3)) + (C5 * (T ** 4))
    return round(CPL/1e6, 2) # J / mol K

def CP_ig(T, C1, C2, C3, C4, C5):

    CPIG = C1 + C2 * pow((C3 / T) / (sinh(C3 / T)), 2) + C4 * pow((C5 / T) / (cosh(C5 / T)), 2)
    return round(CPIG/1e6, 2) # J / mol K

def meanCP(f, T1, T2, ar):

    mcp, err = quad(f, T1, T2, args = ar, limit=1100)
    mcp = mcp / (T2 - T1)
    return mcp # J / mol K



if __name__ == '__main__':
    flash = FlashDrum()
    C1 = 'Benzene'
    C2 = 'Toluene'
    z = {C1: 0.5, C2: 0.5}
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



    Tf = 363.15
    Pf = 400
    feedStream = Stream('Feed', Tf, Pf, 100, z)

    flash.setFeedStream(feedStream)
    #flash.getFeedStream()
    T = 393.15
    P = 200

    flash.isothermal(T,P,f,fp, True)
    flash.Streams()

    #print(flash.heat)
    # CPL_B = meanCP(CP_L, Tb, Td, tuple([value for value in cplB.values()]))
    # CPIG_B = meanCP(CP_ig, Tb, Td, tuple([value for value in cpigB.values()]))
    # CPL_T = meanCP(CP_L, Tb, Td, tuple([value for value in cplT.values()]))
    # CPIG_T = meanCP(CP_ig, Tb, Td, tuple([value for value in cpigT.values()]))
    # print("CP liquid of benzene "+ str(round(CPL_B,2)) +  " kJ/mol K")
    # print("CP gas of benzene "+ str(round(CPIG_B,2)) +  " kJ/mol K")
    # print("CP liquid of toluene "+ str(round(CPL_T,2)) +  " kJ/mol K")
    # print("CP liquid of toluene "+ str(round(CPIG_T,2)) +  " kJ/mol K")

    # Hvap_b = HeatVap(T,**vB)
    # Hvap_t = HeatVap(T,**vT)
    # print("Hvap benzene"+str(round(Hvap_b,2)) + "kj/mol")
    # print("Hvap toluene"+str(round(Hvap_t,2)) + "kj/mol")
