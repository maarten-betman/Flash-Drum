from flash import *
from stream import Stream




if __name__ == '__main__':
    flash = FlashDrum()
    C1 = 'benzene'
    C2 = 'toluene'
    z = {C1: 0.5, C2: 0.5}

    c = parameters([C1, C2])

    Tf = 420
    Pf = 400
    feedStream = Stream('Feed', Tf - 40, Pf, 100, z)
    flash.setFeedStream(feedStream)
    T = 393.15
    P = 200

    flash.isothermal(T, P, c, True)
    print(flash.Streams(True))
    # feedStream = Stream('Feed', Tf, Pf, 100, z)
    # flash.setFeedStream(feedStream)
    # flash.adiabatic(P, c)
    # flash.Streams()