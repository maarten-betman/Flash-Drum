from process_units import *

class FlashDrum():
    def __init__(self):
        # A flas drum has one inlet stream and two outlet stream. This is how they are built.
        # They a dictionary type, {'molar flow': F, 'composition': z, 'enthanply': h, 'temperature': T, 'pressure': P}
        self.feed = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.gas = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.liquid = {'molar flow': None, 'composition': None, 'enthanply': None, 'temperature': None, 'pressure': None}
        self.mode = 'Isothermal'
        self.heat = 0.0
        self.pressure = Pressure(1.0, 'atm')

    def setFeedStream(self, inputF):
        self.feed = inputF

    def getFeedStream(self):
        for key,val in self.feed.items():
            print(str(key) + ': ' + str(val.value) + ' ' + val.units)

    def setGasStream(self, outputG):
        self.gas = outputG

    def getGasStream(self):
        for key,val in self.gas.items():
            print(str(key) + ': ' + str(val.value) + ' ' + val.units)

    def setLiquidStream(self, outputL):
        self.liquid = outputL

    def getLiquidsStream(self):
        for key,val in self.liquid.items():
            print(str(key) + ': ' + str(val.value) + ' ' + val.units)
