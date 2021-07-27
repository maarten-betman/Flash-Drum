
class Stream():

    def __init__(self, Temperature = None,  Pressure = None, molarFlow = 0.0, mComposition = {}, Enthalpy = None):
        self.Temperature = Temperature
        self.Pressure = Pressure
        self.molarFlow = molarFlow
        self.mComposition = mComposition
        self.Enthalpy = Enthalpy

    def setT(self, T):
        self.Temperature = T

    def setP(self, P):
        self.Pressure = P

    def setmf(self, mF):
        self.molarFlow = mF

    def setmC(self, mC):
        self.mComposition = mC

    def setH(self, H):
        self.Enthalpy = H