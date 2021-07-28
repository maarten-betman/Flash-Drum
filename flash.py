from gekko import GEKKO
from stream import Stream

class FlashDrum():
    def __init__(self, mode = 'Isothermal'):
        # A flas drum has one inlet stream and two outlet stream. This is how they are built.
        # They a dictionary type, {'molar flow': F, 'composition': z, 'enthanply': h, 'temperature': T, 'pressure': P}
        # This class only works with pressure in kPa and temperature in K.
        self.feed = Stream("FEED")
        self.vapor = Stream("VAPOR")
        self.liquid = Stream("LIQUID")
        self.mode = mode
        self.heat = None
        self.pressure = None
        self.Tref = 298.15



    def setFeedStream(self, inletStream = Stream("FEED")):
        inletStream.normalize()
        self.feed.setT(inletStream.Temperature)
        self.feed.setP(inletStream.Pressure)
        self.feed.setmF(inletStream.molarFlow)
        self.feed.setmC(inletStream.mComposition)
        self.feed.setH(inletStream.Enthalpy)
        

    def Streams(self):

        print("-"*90)
        print("\t\t\t\tF L A S H  D R U M")
        print("-"*90)
        print("Streams:\t\t" + "FEED" + " " * 20 + "VAPOR " + " " * 20 + "LIQUID")
        print("-"*90)
        print("\t\t\t" + "T_f = " + str(self.feed.getT()) + " K" + 
              "\t\t" + "T_v = " + str(self.vapor.getT()) + " K" + 
              "\t\t  " + "T_l = " + str(self.liquid.getT()) + " K")
        print("\t\t\t" + "P_f = " + str(self.feed.getP()) + " kPa" + 
              "\t\t" + "P_v = " + str(self.vapor.getP()) + " kPa" + 
              "\t\t  " + "P_l = " + str(self.liquid.getP()) + " kPa")
        print("\t\t\t" + "F = " + str(self.feed.getmF()) + " mol/h" + 
              "\t\t" + "V = " + str(self.vapor.getmF()) + " mol/h" + 
              "\t  " + "L = " + str(self.liquid.getmF()) + " mol/h")
        for key in self.feed.getmC().keys():
            print(key + "\t\t\tz = " + str(round(self.feed.getmC(key), 4)) + 
              "\t\t\t" + "y = " + str(round(self.vapor.getmC(key), 4)) + 
              "\t\t  " + "x = " + str(round(self.liquid.getmC(key),4)))
            
        print("\t\t\t" + "h_f = " + str(self.feed.getH()) + " kJ/mol" + 
              "\t" + "h_v = " + str(self.vapor.getH()) + " kJ/mol" + 
              "\t  " + "h_l = " + str(self.liquid.getH()) + " kJ/mol")
        print("-"*90)
        print("\t\t\tHEAT: Q = " + str(round(self.heat)) + " kJ/mol")
        print("-"*90)



    def idealK(self, T, P, f, fp):
        Psat = f(T, **fp)
        return Psat / P


    def isothermal(self, T, P, f, fp, energy = False):
        self.vapor.setT(T)
        self.vapor.setP(P)
        self.liquid.setT(T)
        self.liquid.setP(P)


        self.vapor.setmC(None)
        self.liquid.setmC(None)



        # K's 
        Ki = {}
        Tsat = {}
        for key in self.feed.getmC().keys():

            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])
            Tsat[key] = f['AntoineInv'](P,**fp['AntoineInv'][key])

        m = GEKKO()
        Psi = m.Var(value=0.5, lb= 0.0, ub = 1.0)
        x = sum([((self.feed.getmC(key) * (1 - Ki[key])) / (1 + Psi * (Ki[key] - 1))) for key in Ki.keys()])
        m.Equation([x == 0])
        m.solve(disp=False)  
        self.vapor.setmF( round(Psi.value[0] * self.feed.getmF(), 3)) 
        self.liquid.setmF(round(self.feed.getmF() - self.vapor.getmF(), 3))

        for key in Ki.keys():
            self.liquid.setmC((self.feed.getmC(key)) / (1 + Psi.value[0] * (Ki[key] - 1)), key)
            self.vapor.setmC(self.liquid.getmC(key)  * Ki[key], key)

            
        if energy:

            #Energy Balance
            Tf = self.feed.getT()
            Tref = self.Tref
            T_bubble = self.bubbleT(P, f, fp)
            T_dew = self.dewT(P, f, fp)
            cpl = {}
            cpig = {}
            hf = {}
            hg = {}
            hl = {}
            
            for key in self.feed.getmC().keys():

                cpl[key] = f['meanCP'](f['CPL'], T_bubble,  T_dew, tuple([value for value in fp['CPL'][key].values()]))
                cpig[key] = f['meanCP'](f['CPig'], T_bubble,  T_dew, tuple([value for value in fp['CPig'][key].values()]))
                if self.feed.getT() < T_dew:
                    hf[key] = self.feed.getmC(key) * cpl[key] * (Tf - Tref)
                    hl[key] = self.liquid.getmC(key) * cpl[key] * (T - Tref)
                    hg[key] = self.vapor.getmC(key) * (cpig[key] * (T - Tref) + f['Hvap'](T, **fp['Hvap'][key]))

            self.feed.setH(round( sum([value for value in hf.values()]), 2)) 
            self.liquid.setH(round( sum([value for value in hl.values()]), 2))
            self.vapor.setH(round( sum([value for value in hg.values()]), 2))


            self.heat = self.vapor.getmF() * self.vapor.getH() + self.liquid.getmF() * self.liquid.getH() - self.feed.getmF() * self.feed.getH()

        
        
        


    def bubbleT(self, P, f, fp):

        m = GEKKO()
        t = 0
        for key in self.feed.getmC().keys():

            t += f['AntoineInv'](P,**fp['AntoineInv'][key])
        
        t = round(t / len(self.feed.getmC()))
        T = m.Var(value = t, lb = 0.0, ub = 2000.0)
        # K's 
        Ki = {}

        for key in self.feed.getmC().keys():
            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])
        
        x = sum([self.feed.getmC(key) * Ki[key] for key in Ki.keys()])
        m.Equation([x - 1 == 0])
        m.solve(disp=False) 

        return round(T.value[0], 2)

    def dewT(self, P, f, fp ):

        m = GEKKO()
        t = 0
        for key in self.feed.getmC().keys():

            t += f['AntoineInv'](P,**fp['AntoineInv'][key])
        
        t = round(t / len(self.feed.getmC()))


        T = m.Var(value = t, lb = 200.0, ub = 800.0)
        # K's 
        Ki = {}

        for key in self.feed.getmC().keys():
            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])

        x = sum([self.feed.getmC(key) / Ki[key] for key in Ki.keys()])
        m.Equation([x - 1 == 0])
        m.solve(disp=False) 

        return round(T.value[0], 2)

    def bubbleP(self, T, f, fp):

        P = sum([self.feed.getmC(key) * f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed.getmC().keys()])

        return round(P, 3)

    def dewP(self, T, f, fp):

        P = sum([self.feed.getmC(key) / f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed.getmC().keys()]) ** (-1)

        return round(P, 3)




      