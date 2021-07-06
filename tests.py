from flash import FlashDrum
from gekko import GEKKO
import numpy as np


def Antoine(T, A, B, C):
    P = pow(10 , (A - (B / ((T - 273.15) + C))))
    return P * .133322


def AntoineInv(P, A, B, C):
    T = ((B / (A - np.log10(P/.133322))) - C) + 273.15
    return round(T, 2)


if __name__ == '__main__':
    flash = FlashDrum()
    C1 = 'Benzene'
    C2 = 'Toluene'
    z = {C1: 0.5, C2: 0.5}
    pB = {'A':6.89272, 'B':1203.531, 'C':219.888}
    pT = {'A':6.95805, 'B':1346.773, 'C':219.693}
    f = {'Antoine': Antoine, 'AntoineInv' : AntoineInv}
    fp = {'Antoine': {C1: pB, C2: pT}, 'AntoineInv' : {C1: pB, C2: pT}}

    feedStream = {'molar flow': 100,
                'composition': z}

    flash.setFeedStream(feedStream)
    flash.getFeedStream()

    T = flash.dewT(101.325, f, fp)
    print("{:.2f}".format(T-273.15))  
 
