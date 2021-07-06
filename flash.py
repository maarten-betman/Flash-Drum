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
        self.heat = 0.0
        self.pressure = 1.0

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


    def isothermal(self, T, P, f, fp = {}):
        self.gas['temperature'] = T
        self.gas['pressure'] = P
        self.liquid['temperature'] = T


        # K's 
        Ki = {}
        for key in self.feed['composition'].value.keys():

            Ki[key] = self.idealK(T.value,P.value, f['Antoine'], fp[key])

        m = GEKKO()
        Psi = m.Var(value=0.5, lb= 0.0, ub = 1.0)
        x = sum([((self.feed['composition'].value[key] * (1 - Ki[key])) / (1 + Psi * (Ki[key] - 1))) for key in Ki.keys()])
        m.Equation([x == 0])
        m.solve(disp=False)  
        self.gas['molar flow'] = MolarFlow(Psi.value[0] * self.feed['molar flow'].value, self.feed['molar flow'].units)
        self.feed['molar flow'] = MolarFlow(self.feed['molar flow'].value - self.gas['molar flow'].value, self.gas['molar flow'].units)

        for key in self.Ki.keys():
            self.liquid['composition'].value['key'] = (self.feed['composition'].value[key]) / (1 + Psi.value[0] * (Ki[key] - 1))
            self.gas['composition'].value['key'] = self.liquid['composition'].value['key']  * Ki[key]

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




      