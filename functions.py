from gekko import GEKKO
import numpy as np
from math import sinh, cosh
from scipy.integrate import quad
import csv

m = GEKKO()

def Antoine(T, C1, C2, C3, C4, C5):

    
    P = m.exp(C1 + (C2 / T) + (C3 * m.log(T)) + (C4 * (T ** C5)))

    return (P / 1000) # kPa

def AntoineInv(P, C1, C2, C3, C4, C5):

    T = m.Var(value = 298.15, lb = 200, ub = 800)
    m.Equation([(m.exp(C1 + (C2 / T) + (C3 * m.log(T)) + (C4 * (T ** C5))) / 1000) - P == 0])
    m.solve(disp=False)
    return float(T.value[0]) # K

def HeatVap(T, Tc, C1, C2, C3, C4):

    Tr = T / Tc
    Hvap = C1 * (1 - Tr) ** (C2 + C3 * Tr + C4 * Tr * Tr)
    return Hvap/1e6 # kJ / mol

def CP_L(T, C1, C2, C3, C4, C5):

    CPL = C1 +( C2 * T) +( C3 * (T ** 2)) +( C4 * (T ** 3)) + (C5 * (T ** 4))
    return CPL/1e6 # kJ / mol K

def CP_ig(T, C1, C2, C3, C4, C5):

    CPIG = C1 + C2 * pow((C3 / T) / (sinh(C3 / T)), 2) + C4 * pow((C5 / T) / (cosh(C5 / T)), 2)
    return CPIG/1e6 # kJ / mol K

def meanCP(f, T1, T2, ar):

    mcp, err = quad(f, T1, T2, args = ar, limit=1100)
    mcp = mcp / (T2 - T1)
    return mcp # kJ / mol K



with open('compound_data.csv', mode = 'r') as csv_f:
    reader = csv.reader(csv_f)
    compound_data = {row[0]: {'Antoine': {'C1': float(row[7]), 'C2': float(row[8]), 'C3': float(row[9]), 'C4': float(row[10]), 'C5': float(row[11])},
                                'Hvap': {'Tc': float(row[1]), 'C1': float(row[12]), 'C2': float(row[13]), 'C3': float(row[14]), 'C4': float(row[15])},
                                'CPL': {'C1': float(row[2]), 'C2': float(row[3]), 'C3': float(row[4]), 'C4': float(row[5]), 'C5': float(row[6])},
                                'CPIG': {'C1': float(row[16]), 'C2': float(row[17]), 'C3': float(row[18]), 'C4': float(row[19]), 'C5': float(row[20])}} for row in reader}
    csv_f.close()



