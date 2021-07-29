from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt
from stream import Stream

class FlashDrum():

    def __init__(self, mode = 'Isothermal'):
        ''' The Flash Drum has one inlet stream and two outlet stream.
         The program uses the class Stream to represent the inlet and outlet process streams.
         -> feed is the inlet object from the class Stream.
         -> vapor is an outlet object from the class Stream.
         -> liquid is an outlet object from the class Stream.
         -> mode refers to calculations made by the program, default is "Isothermal", it also can work in "Adiabatic".
         -> psi is the vapor outlet / feed inlet ratio.
         -> Heat is the heat in kJ/mol that the Flash Drum requires.
         -> Temperature is the Flash Drum operating temperature in K.
         -> Pressure is the Flash Drum operating pressure kPa.
         -> Tref is the reference temperature in K for the energy balance calculations. 
         This class only works with pressure in kPa and temperature in K. '''
        self.feed = Stream("FEED")
        self.vapor = Stream("VAPOR")
        self.liquid = Stream("LIQUID")
        self.mode = mode
        self.psi = 0
        self.Heat = None
        self.Temperature = None
        self.Pressure = None
        self.Tref = 298.15


    def setFeedStream(self, inletStream = Stream("FEED")):
        '''Set the feed stream properties.'''
        inletStream.normalize()
        self.feed.setT(inletStream.Temperature)
        self.feed.setP(inletStream.Pressure)
        self.feed.setmF(inletStream.molarFlow)
        self.feed.setmC(inletStream.mComposition)
        self.feed.setH(inletStream.Enthalpy)
        

    def Streams(self):
        ''' Display the stream results in a table. '''
        print("-"*100)
        print("\t\t\t\tF L A S H  D R U M: \t" + self.mode.upper())
        print("-"*100)
        print("Streams:\t\t" + "FEED" + " " * 20 + "VAPOR " + " " * 20 + "LIQUID")
        print("-"*100)
        print("\t\t\t" + "T_f = " + str(round(self.feed.getT(), 2)) + " K" + 
              "\t\t" + "T_v = " + str(round(self.vapor.getT(), 2)) + " K" + 
              "\t\t  " + "T_l = " + str(round(self.liquid.getT(), 2)) + " K")
        print("\t\t\t" + "P_f = " + str(self.feed.getP()) + " kPa" + 
              "\t\t" + "P_v = " + str(self.vapor.getP()) + " kPa" + 
              "\t\t  " + "P_l = " + str(self.liquid.getP()) + " kPa")
        print("\t\t\t" + "F = " + str(round(self.feed.getmF(), 3)) + " mol/h" + 
              "\t\t" + "V = " + str(round(self.vapor.getmF(), 3)) + " mol/h" + 
              "\t  " + "L = " + str(round(self.liquid.getmF(), 3)) + " mol/h")
        for key in self.feed.getmC().keys():
            print(key + "\t\t\tz = " + str(round(self.feed.getmC(key), 3)) + 
              "\t\t\t" + "y = " + str(round(self.vapor.getmC(key), 3)) + 
              "\t\t  " + "x = " + str(round(self.liquid.getmC(key),3)))
            
        print("\t\t\t" + "h_f = " + str(round(self.feed.getH(), 3)) + " kJ/mol" + 
              "\t" + "h_v = " + str(round(self.vapor.getH(), 3)) + " kJ/mol" + 
              "\t  " + "h_l = " + str(round(self.liquid.getH(), 3)) + " kJ/mol")
        print("-"*100)
        print("\t\t\tHEAT: Q = " + str(round(self.Heat)) + " kJ/mol")
        print("-"*100)

    
    def saveResults(self):
        feed = {'name': self.feed.getName(),
                'Temeperature': self.feed.getT(),
                'Pressure': self.feed.getP(),
                'Molar Flow': self.feed.getmF(),
                'Molar Composition': self.feed.getmC(),
                'Enthalpy': self.feed.getH()}
        vapor = {'name': self.vapor.getName(),
                'Temeperature': self.vapor.getT(),
                'Pressure': self.vapor.getP(),
                'Molar Flow': self.vapor.getmF(),
                'Molar Composition': self.vapor.getmC(),
                'Enthalpy': self.vapor.getH()}
        liquid = {'name': self.liquid.getName(),
                'Temeperature': self.liquid.getT(),
                'Pressure': self.liquid.getP(),
                'Molar Flow': self.liquid.getmF(),
                'Molar Composition': self.liquid.getmC(),
                'Enthalpy': self.liquid.getH()}
        Q = self.Heat
        Psi = self.psi
        mode = self.mode
        results = {'Drum': {'mode': mode, 'Heat': Q, 'Psi': Psi},
                    'Feed': feed,
                    'Vapor': vapor,
                    'Liquid': liquid}
        return  results


    def idealK(self, T, P, f, fp):
        ''' Caculates an ideal K parameter with Raoult's Law'''
        Psat = f(T, **fp)
        return Psat / P


    def isothermal(self, T, P, f, fp, energy = False):
        ''' It makes isothermal flash caculations given an operating temperature and pressure.'''
        self.mode = "Isothermal"
        self.vapor.setT(T)
        self.vapor.setP(P)
        self.liquid.setT(T)
        self.liquid.setP(P)
        self.vapor.setmC(None)
        self.liquid.setmC(None)
        T_bubble = self.bubbleT(P, f, fp)
        T_dew = self.dewT(P, f, fp)
        # K's 
        Ki = {}
        # Ki calculations are made.
        for key in self.feed.getmC().keys():

            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])

        # Check if the operating temperature is between the limits for the PSI calculations.
        if T <= T_bubble:

            self.psi = 0
            
        elif T >= T_dew:

            self.psi = 1

        else:
            # If the operating temperature is inside the limits calculations for PSI are made.
            m = GEKKO()
            Psi = m.Var(value=0.5, lb= 0.0, ub = 1.0)
            x = sum([((self.feed.getmC(key) * (1 - Ki[key])) / (1 + Psi * (Ki[key] - 1))) for key in Ki.keys()])
            m.Equation([x == 0])
            m.solve(disp=False) 
            self.psi = Psi.value[0] 
        # Calulate vapor and liquid molar flows.
        self.vapor.setmF(self.psi * self.feed.getmF()) 
        self.liquid.setmF(self.feed.getmF() - self.vapor.getmF())
        # Calculate vapor and liquid molar compositions
        for key in Ki.keys():
            self.liquid.setmC((self.feed.getmC(key)) / (1 + self.psi * (Ki[key] - 1)), key)
            self.vapor.setmC(self.liquid.getmC(key)  * Ki[key], key)
        # Check if energy == True for the energy balance calculation         
        if energy:

            #Energy Balance
            Tf = self.feed.getT()
            Tref = self.Tref            
            cpl = {}
            cpig = {}
            hf = {}
            hg = {}
            hl = {}
            
            for key in self.feed.getmC().keys():
                # Mean heat capacity
                cpl[key] = f['meanCP'](f['CPL'], T_bubble,  T_dew, tuple([value for value in fp['CPL'][key].values()]))
                cpig[key] = f['meanCP'](f['CPig'], T_bubble,  T_dew, tuple([value for value in fp['CPig'][key].values()]))
                # Enthalply calculation.
                hf[key] = self.feed.getmC(key) * cpl[key] * (Tf - Tref)
                hl[key] = self.liquid.getmC(key) * cpl[key] * (T - Tref)
                hg[key] = self.vapor.getmC(key) * (cpig[key] * (T - Tref) + f['Hvap'](T, **fp['Hvap'][key]))

            self.feed.setH(sum([value for value in hf.values()])) 
            self.liquid.setH( sum([value for value in hl.values()]))
            self.vapor.setH(sum([value for value in hg.values()]))

            # Energy balance for heat (Q) caculation.
            self.Heat = self.vapor.getmF() * self.vapor.getH() + self.liquid.getmF() * self.liquid.getH() - self.feed.getmF() * self.feed.getH()


    def adiabatic(self, P, f, fp):
        ''' It makes adibatic flash caculations given an operating pressure.'''
        self.mode ="Adiabatic"
        self.Pressure = P
        self.vapor.setP(P)
        self.liquid.setP(P)
        self.vapor.setmC(None)
        self.liquid.setmC(None)
        T_bubble = self.bubbleT(P, f, fp)
        T_dew = self.dewT(P, f, fp)
        Tf = self.feed.getT()
        Tref = self.Tref        
        cpl = {}
        cpig = {}
        hf = {}
        hg = {}
        hl = {}
        # Here is defined the variables PSI and T of the model
        m = GEKKO()
        #m.options.MAX_ITER = 500
        Psi = m.Var(value=0.5, lb= 0.0, ub = 1.0)
        T = m.Var(value=(T_bubble + T_dew) * 0.5, lb = T_bubble * 0.85, ub = T_dew * 1.15)
        # K's 
        Ki = {}
        # Ki calculations are made.
        for key in self.feed.getmC().keys():

            Ki[key] = self.idealK(T,P, f['Antoine'], fp['Antoine'][key])
        # First equation; f(PSI) == 0
        x = sum([((self.feed.getmC(key) * (1 - Ki[key])) / (1 + Psi * (Ki[key] - 1))) for key in Ki.keys()])
        # Intermediate equations:
        self.vapor.setmF( Psi * self.feed.getmF()) 
        self.liquid.setmF(self.feed.getmF() - self.vapor.getmF())

        for key in Ki.keys():
            self.liquid.setmC((self.feed.getmC(key)) / (1 + Psi * (Ki[key] - 1)), key)
            self.vapor.setmC(self.liquid.getmC(key)  * Ki[key], key)

        # Intermediate energy Balance        
        for key in self.feed.getmC().keys():

            cpl[key] = f['meanCP'](f['CPL'], T_bubble,  T_dew, tuple([value for value in fp['CPL'][key].values()]))
            cpig[key] = f['meanCP'](f['CPig'], T_bubble,  T_dew, tuple([value for value in fp['CPig'][key].values()]))
            hf[key] = self.feed.getmC(key) * cpl[key] * (Tf - Tref)
            hl[key] = self.liquid.getmC(key) * cpl[key] * (T - Tref)
            hg[key] = self.vapor.getmC(key) * (cpig[key] * (T - Tref) + f['Hvap'](T, **fp['Hvap'][key]))

        self.feed.setH( sum([value for value in hf.values()])) 
        self.liquid.setH( sum([value for value in hl.values()]))
        self.vapor.setH( sum([value for value in hg.values()]))
        # Second equaion: f(T) == 0
        y = self.vapor.getmF() * self.vapor.getH() + self.liquid.getmF() * self.liquid.getH() - self.feed.getmF() * self.feed.getH()
        # Solve the equations system
        m.Equation([x == 0, y == 0])
        m.solve(disp=False)
        # Evaluate the results of T and PSI in the intermediate equations
        self.psi = Psi.value[0]
        self.Temperature = T.value[0]
        # Real Ki calculations are made.
        for key in self.feed.getmC().keys():

            Ki[key] = self.idealK(self.Temperature,P, f['Antoine'], fp['Antoine'][key])
        # Calulate vapor and liquid molar flows.
        self.vapor.setmF( self.psi * self.feed.getmF()) 
        self.liquid.setmF(self.feed.getmF() - self.vapor.getmF())
        # Calculate vapor and liquid molar compositions
        for key in Ki.keys():

            self.liquid.setmC((self.feed.getmC(key)) / (1 + self.psi * (Ki[key] - 1)), key)
            self.vapor.setmC(self.liquid.getmC(key)  * Ki[key], key)

        #Real Energy Balance        
        for key in self.feed.getmC().keys():
            # Mean heat capacity
            cpl[key] = f['meanCP'](f['CPL'], T_bubble,  T_dew, tuple([value for value in fp['CPL'][key].values()]))
            cpig[key] = f['meanCP'](f['CPig'], T_bubble,  T_dew, tuple([value for value in fp['CPig'][key].values()]))
            # Enthalply calculation.
            hf[key] = self.feed.getmC(key) * cpl[key] * (Tf - Tref)
            hl[key] = self.liquid.getmC(key) * cpl[key] * (self.Temperature - Tref)
            hg[key] = self.vapor.getmC(key) * (cpig[key] * (self.Temperature - Tref) + f['Hvap'](self.Temperature, **fp['Hvap'][key]))

        self.feed.setH( sum([value for value in hf.values()])) 
        self.liquid.setH( sum([value for value in hl.values()]))
        self.vapor.setH( sum([value for value in hg.values()]))
        Q = self.vapor.getmF() * self.vapor.getH() + self.liquid.getmF() * self.liquid.getH() - self.feed.getmF() * self.feed.getH()
        self.vapor.setT(self.Temperature)
        self.liquid.setT(self.Temperature)
        self.Heat = Q


    def bubbleT(self, P, f, fp):
        ''' Bubble temperature calculation given an operating pressure.'''
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
        ''' Dew temperature calculation given an operating pressure.'''
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
        ''' Bubble pressure calculation given an operating temperature.'''
        P = sum([self.feed.getmC(key) * f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed.getmC().keys()])

        return round(P, 3)


    def dewP(self, T, f, fp):
        ''' Dew pressure calculation given an operating temperature.'''
        P = sum([self.feed.getmC(key) / f['Antoine'](T, **fp['Antoine'][key]) for key in self.feed.getmC().keys()]) ** (-1)

        return round(P, 3)

