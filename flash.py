from gekko import GEKKO

class FlashDrum():
    def __init__(self):
        # A flas drum has one inlet stream and two outlet stream. This is how they are built.
        # They a dictionary type, {'molar flow': F, 'composition': z, 'enthanply': h, 'temperature': T, 'pressure': P}
        # This class only works with pressure in kPa and temperature in K.
        self.feed = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.gas = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.liquid = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
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

    def getFeedStream(self):
        for key,val in self.feed.items():
            if val != None:
                print(str(key) + ': ' + str(val))

    def setGasStream(self, outputG):
        self.gas = outputG

    def getGasStream(self):
        for key,val in self.gas.items():
            if val != None:
                print(str(key) + ': ' + str(val) )

    def setLiquidStream(self, outputL):
        self.liquid = outputL

    def getLiquidsStream(self):
        for key,val in self.liquid.items():
            if val != None:
                print(str(key) + ': ' + str(val) )

    def idealK(self, T, P, f, fp = {}):
        Psat = f(T, **fp)
        return Psat / P


    def isothermal(self, T, P, f, fp = {}, energy = False):
        self.gas['temperature'] = T
        self.gas['pressure'] = P
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
        self.gas['molar flow'] = Psi.value[0] * self.feed['molar flow']
        self.feed['molar flow'] = self.feed['molar flow'] - self.gas['molar flow']

        for key in self.Ki.keys():
            self.liquid['composition'][key] = (self.feed['composition'][key]) / (1 + Psi.value[0] * (Ki[key] - 1))
            self.gas['composition'][key] = self.liquid['composition'][key]  * Ki[key]

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
                    hg[key] = self.gas['composition'][key] * (cpig[key] * (T - Tref) + f['Hvap'](T, **fp['Hvap'][key]))

            self.feed['enthalpy'] = round( sum([value for value in hf.values()]), 2)
            self.liquid['enthalpy'] = round( sum([value for value in hl.values()]), 2)
            self.gas['enthalpy'] = round( sum([value for value in hg.values()]), 2)

            self.heat = self.gas['molar flow'] * self.gas['enthalpy'] + self.liquid['molar flow'] * self.liquid['enthalpy'] - self.feed['molar flow'] * self.feed['enthalpy']

        
        
        


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


        T = m.Var(value = t, lb = 0.0, ub = 2000.0)
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




      