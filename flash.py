from gekko import GEKKO
from stream import Stream

class FlashDrum():
    def __init__(self):
        # A flas drum has one inlet stream and two outlet stream. This is how they are built.
        # They a dictionary type, {'molar flow': F, 'composition': z, 'enthanply': h, 'temperature': T, 'pressure': P}
        # This class only works with pressure in kPa and temperature in K.
        self.feed = {'molar flow': None, 'composition': {}, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.vapor = {'molar flow': None, 'composition': {}, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.liquid = {'molar flow': None, 'composition': {}, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.mode = 'Isothermal'
        self.heat = None
        self.pressure = None
        self.Tref = 298.15

    def normalize(self, z):
        Z = sum([zi for zi in z.values()])

        if not ((Z == 1.0) or (Z == 1)):

            for key in z.keys():

                z[key] = z[key] / Z

        return z


    def setFeedStream(self, inputF):
        inputF['composition'] = self.normalize(inputF['composition'])
        self.feed = inputF

    def Streams(self):

        print("-"*90)
        print("\t\t\t\tF L A S H  D R U M")
        print("-"*90)
        print("Streams:\t\t" + "FEED" + " " * 20 + "VAPOR " + " " * 20 + "LIQUID")
        print("-"*90)
        print("\t\t\t" + "T_f = " + str(self.feed['temperature']) + " K" + 
              "\t\t" + "T_v = " + str(self.vapor['temperature']) + " K" + 
              "\t\t  " + "T_l = " + str(self.liquid['temperature']) + " K")
        print("\t\t\t" + "P_f = " + str(self.feed['pressure']) + " kPa" + 
              "\t\t" + "P_v = " + str(self.vapor['pressure']) + " kPa" + 
              "\t\t  " + "P_l = " + str(self.liquid['pressure']) + " kPa")
        print("\t\t\t" + "F = " + str(self.feed['molar flow']) + " mol/h" + 
              "\t\t" + "V = " + str(self.vapor['molar flow']) + " mol/h" + 
              "\t  " + "L = " + str(self.liquid['molar flow']) + " mol/h")
        for key in self.feed['composition'].keys():
            print(key + "\t\t\tz = " + str(round(self.feed['composition'][key], 4)) + 
              "\t\t\t" + "y = " + str(round(self.vapor['composition'][key], 4)) + 
              "\t\t  " + "x = " + str(round(self.liquid['composition'][key],4)))
            
        print("\t\t\t" + "h_f = " + str(self.feed['enthalpy']) + " kJ/mol" + 
              "\t" + "h_v = " + str(self.vapor['enthalpy']) + " kJ/mol" + 
              "\t  " + "h_l = " + str(self.liquid['enthalpy']) + " kJ/mol")
        print("-"*90)
        print("\t\t\tHEAT: Q = " + str(round(self.heat)) + " kJ/mol")
        print("-"*90)



    def idealK(self, T, P, f, fp = {}):
        Psat = f(T, **fp)
        return Psat / P


    def isothermal(self, T, P, f, fp = {}, energy = False):
        self.vapor['temperature'] = T
        self.vapor['pressure'] = P
        self.liquid['temperature'] = T
        self.liquid['pressure'] = P


        # K's 
        Ki = {}
        Tsat = {}
        for key in self.feed['composition'].keys():

            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])
            Tsat[key] = f['AntoineInv'](P,**fp['AntoineInv'][key])

        m = GEKKO()
        Psi = m.Var(value=0.5, lb= 0.0, ub = 1.0)
        x = sum([((self.feed['composition'][key] * (1 - Ki[key])) / (1 + Psi * (Ki[key] - 1))) for key in Ki.keys()])
        m.Equation([x == 0])
        m.solve(disp=False)  
        self.vapor['molar flow'] = round(Psi.value[0] * self.feed['molar flow'], 3)
        self.liquid['molar flow'] = round(self.feed['molar flow'] - self.vapor['molar flow'], 3)

        for key in Ki.keys():
            self.liquid['composition'][key] = (self.feed['composition'][key]) / (1 + Psi.value[0] * (Ki[key] - 1))
            self.vapor['composition'][key] = self.liquid['composition'][key]  * Ki[key]

        if energy:

            #Energy Balance
            Tf = self.feed['temperature']
            Tref = self.Tref
            T_bubble = self.bubbleT(P, f, fp)
            T_dew = self.dewT(P, f, fp)
            cpl = {}
            cpig = {}
            hf = {}
            hg = {}
            hl = {}
            
            for key in self.feed['composition'].keys():

                cpl[key] = f['meanCP'](f['CPL'], T_bubble,  T_dew, tuple([value for value in fp['CPL'][key].values()]))
                cpig[key] = f['meanCP'](f['CPig'], T_bubble,  T_dew, tuple([value for value in fp['CPig'][key].values()]))
                if self.feed['temperature'] < T_dew:
                    hf[key] = self.feed['composition'][key] * cpl[key] * (Tf - Tref)
                    hl[key] = self.liquid['composition'][key] * cpl[key] * (T - Tref)
                    hg[key] = self.vapor['composition'][key] * (cpig[key] * (T - Tref) + f['Hvap'](T, **fp['Hvap'][key]))

            self.feed['enthalpy'] = round( sum([value for value in hf.values()]), 2)
            self.liquid['enthalpy'] = round( sum([value for value in hl.values()]), 2)
            self.vapor['enthalpy'] = round( sum([value for value in hg.values()]), 2)


            self.heat = self.vapor['molar flow'] * self.vapor['enthalpy'] + self.liquid['molar flow'] * self.liquid['enthalpy'] - self.feed['molar flow'] * self.feed['enthalpy']

        
        
        


    def bubbleT(self, P, f, fp = {}):

        m = GEKKO()
        t = 0
        for key in self.feed['composition'].keys():

            t += f['AntoineInv'](P,**fp['AntoineInv'][key])
        
        t = round(t / len(self.feed['composition']))
        T = m.Var(value = t, lb = 0.0, ub = 2000.0)
        # K's 
        Ki = {}

        for key in self.feed['composition'].keys():
            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])
        
        x = sum([self.feed['composition'][key] * Ki[key] for key in Ki.keys()])
        m.Equation([x - 1 == 0])
        m.solve(disp=False) 

        return round(T.value[0], 2)

    def dewT(self, P, f, fp = {}):

        m = GEKKO()
        t = 0
        for key in self.feed['composition'].keys():

            t += f['AntoineInv'](P,**fp['AntoineInv'][key])
        
        t = round(t / len(self.feed['composition']))


        T = m.Var(value = t, lb = 200.0, ub = 800.0)
        # K's 
        Ki = {}

        for key in self.feed['composition'].keys():
            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])

        x = sum([self.feed['composition'][key] / Ki[key] for key in Ki.keys()])
        m.Equation([x - 1 == 0])
        m.solve(disp=False) 

        return round(T.value[0], 2)

    def bubbleP(self, T, f, fp = {}):

        P = sum([self.feed['composition'][key] * f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed['composition'].keys()])

        return round(P, 3)

    def dewP(self, T, f, fp = {}):

        P = sum([self.feed['composition'][key] / f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed['composition'].keys()]) ** (-1)

        return round(P, 3)




      