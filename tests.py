from flash import FlashDrum
from stream import Stream
from functions import *



if __name__ == '__main__':
    flash = FlashDrum()
    C1 = 'Benzene'
    C2 = 'Toluene'
    z = {C1: 0.5, C2: 0.5}

    f = {'Antoine': Antoine, 'AntoineInv' : AntoineInv, 'Hvap' : HeatVap, 'CPL': CP_L, 'CPig' : CP_ig, 'meanCP':meanCP}
    fp = {'Antoine': {C1 : compound_data[C1]['Antoine'], C2: compound_data[C2]['Antoine']},
         'AntoineInv' : {C1: compound_data[C1]['Antoine'], C2: compound_data[C2]['Antoine']}, 
         'Hvap' : {C1: compound_data[C1]['Hvap'], C2: compound_data[C2]['Hvap']},
         'CPL': {C1: compound_data[C1]['CPL'], C2: compound_data[C2]['CPL']},
         'CPig': {C1: compound_data[C1]['CPIG'], C2: compound_data[C2]['CPIG']}}

    Tf = 420
    Pf = 400
    feedStream = Stream('Feed', Tf - 40, Pf, 100, z)
    flash.setFeedStream(feedStream)
    T = 393.15
    P = 200

    flash.isothermal(T, P, f, fp, True)
    flash.Streams()
    feedStream = Stream('Feed', Tf, Pf, 100, z)
    flash.setFeedStream(feedStream)
    flash.adiabatic(P, f, fp)
    flash.Streams()