import streamlit as st
import flash as fd
from stream import Stream
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Flash Drum app", page_icon="🔥", initial_sidebar_state="expanded")

header = st.container()
mixture = st.container()
calculations = st.container()
simulations = st.container()
diagrams = st.container()
footer = st.container()

compounds = ["benzene", "toluene", "chlorobenzene", "p-xylene",  "styrene"]

################################################################################
################################################################################
################################################################################
################################################################################
with header:
    st.title("FLASH DRUM PORJECT 🔥!")
    st.text("In this app you can play simulations flash drum calculations for ideal mixtures.")
    st.image("https://images.pexels.com/photos/3105242/pexels-photo-3105242.jpeg?auto=compress&cs=tinysrgb&h=750&w=1260")
################################################################################
################################################################################
################################################################################
################################################################################
with mixture:
    st.header("👩‍🔬 Prepare your mixture! 👨‍🔬")
    st.markdown("Chose at leats two comoponents and introduce its molar composition.  \n"
        "**NOTE:** the sum of the mole fractions must be equals to **ONE** (_1.0_). If it is greater molar, compositions will be normalized.")


    components = st.multiselect(label="Choose the mixture components", options= compounds)
    

    fraction = {}    
   
    for i in components:
        fraction[i] = st.number_input(label=i, key="Component_" + i, min_value=0.0000, max_value=1.0000, step=0.0001, format = "%.4f", value = 0.0)
    components = fd.parameters([key for key in fraction.keys()])  
    nonZero = sum([z for z in fraction.values()])
################################################################################
################################################################################
################################################################################
################################################################################
if len(fraction) > 0:

    with calculations:
        st.header("1.- Mixture calculations 💥")
        st.markdown("Here you can find four type of calculations.")

        flash_c = fd.FlashDrum()
        stream_c = Stream(mComposition = fraction)
        Calculation = st.selectbox("Choose the calculation type:", ["BubbleT point", "BubbleP point", "DewT point", "DewP point"] )
        if nonZero > 0:
            flash_c.setFeedStream(stream_c)

            if Calculation == "BubbleT point":

                st.subheader("1.1- BubbleT point")

                with st.form(key = "BubbleT"):
                    
                    st.markdown("**Temperature of the Bubble point given a pressure:**")
                    colBT1, colBT2 = st.columns([1, 1])

                    with colBT1:
                        
                        P1 = st.number_input(label = "Pressure in kPa", min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
                                            
                        buttonBT = st.form_submit_button("GO!")

                        if buttonBT:

                            with colBT2:
                                st.markdown("__Temperature__")
                                with st.spinner('Calculating...'):
                                    st.markdown("**{:.2f} K**".format(flash_c.bubbleT(P1, components)))
                                    st.success("Calculations complete!")


            elif Calculation == "BubbleP point":

                st.subheader("1.2- BubbleP point")

                with st.form(key = "BubbleP"):
                    st.markdown("**Pressure of the Bubble point given a temperature:**")
                    colBP1, colBP2 = st.columns([1, 1])
                    with colBP1:

                        T1 = st.number_input(label = "Temperature in K", min_value=200.0, max_value=800.0, step=1.0, format = "%.2f")
                        buttonBP = st.form_submit_button("GO!")

                        if buttonBP:


                            with colBP2:
                                st.markdown("__Pressure__")
                                with st.spinner('Calculating...'):
                                    st.markdown("**{:.2f} kPa**".format(flash_c.bubbleP(T1, components)))
                                    st.success("Calculations complete!")


            elif Calculation == "DewT point":

                    st.subheader("1.3- DewT point")

                    with st.form(key = "DewT"):
                        
                        st.markdown("**Temperature of the Dew point given a pressure:**")
                        colDT1, colDT2 = st.columns([1, 1])
                        with colDT1:
                            
                            P2 = st.number_input(label = "Pressure in kPa", min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
                                            
                            buttonDT = st.form_submit_button("GO!")

                            if buttonDT:
                

                                with colDT2:
                                    st.markdown("__Temperature__")
                                    with st.spinner('Calculating...'):
                                        st.markdown("**{:.2f} K**".format(flash_c.dewT(P2, components)))
                                        st.success("Calculations complete!")


            elif Calculation == "DewP point":

                st.subheader("1.4- DewP point")
                
                with st.form(key = "DewP"):
                    st.markdown("**Pressure of the Dew point given a temperature:**")
                    colDP1, colDP2 = st.columns([1, 1])
                    with colDP1:

                        T2 = st.number_input(label = "Temperature in K", min_value=200.0, max_value=800.0, step=1.0, format = "%.2f")
                        buttonDP = st.form_submit_button("GO!")

                        if buttonDP:
    

                            with colDP2:
                                st.markdown("__Pressure__")
                                with st.spinner('Calculating...'):
                                    st.markdown("**{:.2f} kPa**".format(flash_c.dewP(T2, components)))
                                    st.success("Calculations complete!")
        
        else:
            st.error("Fracction values sum must be non-zero!")   
    ################################################################################
    ################################################################################
    ################################################################################
    ################################################################################           
    with simulations:
        st.header("2.- Flash Drum simulations 💻")
        st.markdown("In this section you can make flash drum simulations")
        flash_s = fd.FlashDrum()

        simulation = st.selectbox(label = "Choose simulation type", options=["Isothermal Flash Drum", "Adiabatic Flash Drum"])
        if nonZero > 0:
            
            Tfeed = st.number_input(label = "Feedstream temperature in K", min_value=200.0, max_value=800.0, step=1.0, format = "%.2f")
            Pfeed = st.number_input(label = "Feedstream pressure in kPa", min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
            mFfeed = st.number_input(label = "Feedstream molar flow in mol/h", min_value= 0.01, max_value=1000000.00, step = 0.01, format= "%.2f")
            stream_s = Stream(name = "FEED", Temperature = Tfeed, Pressure = Pfeed, mComposition = fraction, molarFlow= mFfeed)
            flash_s.setFeedStream(stream_s)

            if simulation == "Isothermal Flash Drum":

                st.subheader("2.1- Isothermal Flash Drum")        

                with st.form(key = "IsothermalFlash"):
                    st.markdown("**Isothermal flash drum simulation given a temperature and pressure:**")

                    colIF1, colIF2 = st.columns([1, 2])
                    with colIF1:
                        T3 = st.number_input(label = "Drum Temperature in K", min_value=200.0, max_value=800.0, step=1.0, format = "%.2f")
                        P3 = st.number_input(label = "Drum Pressure in kPa",min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
                        energyBalance = st.selectbox(label = "Energy balance?", options=[True, False])
                        buttonIF = st.form_submit_button("GO!")
                    with colIF2:
                        # ESPACIO PARA UNA IMAGEN
                        pass

                    if buttonIF:
                            
                        if energyBalance:

                            with st.spinner("Calculating..."):
                                flash_s.isothermal(T3, P3, components, True)
                                st.text(flash_s.Streams(True))
                                st.success("Calculations complete!")
                        else:
                            with st.spinner("Calculating..."):
                                flash_s.isothermal(T3, P3, components)
                                st.text(flash_s.Streams())
                                st.success("Calculations complete!")

            elif simulation == "Adiabatic Flash Drum":

                st.subheader("2.2- Adiabatic Flash Drum")
            

                with st.form(key = "AdiabaticFlash"):
                    st.markdown("**Adiabatic flash drum calculations given a pressure:**")

                    colAF1, colAF2 = st.columns([1, 2])
                    with colAF1:
                        P4 = st.number_input(label = "Drum Pressure in kPa", min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
                        buttonAF = st.form_submit_button("GO!")
                    with colAF2:
                        # ESPACIO PARA UNA IMAGEN
                        pass

                    if buttonAF:

                        with st.spinner("Calculating..."):
                            flash_s.adiabatic(P4, components)
                            st.text(flash_s.Streams(True))
                            st.success("Calculations complete!")


        else: 
            st.error("Fracction values sum must be non-zero!") 

        

    ################################################################################
    ################################################################################
    ################################################################################
    ################################################################################
    with diagrams:
        st.header("3.- Binary phase diagrams ☁")

        # with st.form(key = "Diagrams"):
        #     colc1, colc2 = st.columns([1, 1])
        #     with colc1:
        #         C1 = st.selectbox(label="Compound 1", options=["benzene", "toluene", "chlorobenzene", "p-xylene",  "styrene"])

        #         with colc2:
        #             C2 = st.selectbox(label="Compound 1", options=["benzene", "toluene", "chlorobenzene", "p-xylene",  "styrene"].remove(C1))

        # volatility = ["benzene", "toluene", "chlorobenzene", "p-xylene",  "styrene"]
        # current_mixture = ["benzene", "toluene", "p-xylene"]
        # diagrams = np.zeros((5,5), dtype=int)
        # for i in range(len(diagrams)):
        #     for j in range(len(diagrams)):
        #         if volatility[i] in current_mixture and volatility[j] in current_mixture:
        #             diagrams[i, j] = 1
        # diagrams = np.triu(diagrams, 1)
        # flash_d = fd.FlashDrum()
        
        

        




        # if Calculation == "T vs x Diagram":
        #     st.subheader("3.1- T vs x Diagram")

        #     with st.form(key = "Tvsx"):
        #         if len(current_mixture) > 1:
        #             col13, col14 = st.columns([1, 1])
        #             with col13:
        #                 C1 = st.selectbox(label="Compound 1", options=current_mixture)
        #                 if C1:
        #                     with col14:
        #                         C2 = st.selectbox(label="Compund 2", options=current_mixture.remove(C1))

        #         else:
        #             st.error("You need at least two compounds")

                
                

        #         Px = st.number_input(label = "System pressure in kPa", min_value= 10.0, max_value=1100.0, step = 10.0, format="%.2f")
        #         button7 = st.form_submit_button("Generate diagrams!")

                # if button7:

                #     with st.spinner("Generating diagrams..."):
                        
                        
                #         x = np.linspace(0.0, 1.0, num = 21)
                #         for i, x1 in enumerate(volatility):
                #             for j, x2 in enumerate(volatility):
                #                 if diagrams[i, j] == 1:
                #                     T_b = []
                #                     T_d = []
                #                     fig = go.Figure()
                #                     for k in x:
                #                         fraction_d = {x1: k, x2: 1 - k}
                #                         components_d = fd.parameters(current_mixture)
                #                         stream_d = Stream(mComposition = fraction_d)
                #                         flash_d.setFeedStream(stream_d)
                #                         T_b.append(flash_d.bubbleT(Px, components_d))
                #                         T_d.append(flash_d.dewT(Px, components_d))

                #                     fig.add_trace(go.Scatter(x = x, y = T_b, mode = "lines", name = "x_"  + x1, line = {'color': '#3D78FD'}))
                #                     fig.add_trace(go.Scatter(x = x, y = T_d, mode = "lines", name = "x_"  + x1, line = {'color': '#3DFDB2'}))
                #         st.write(fig)

    ################################################################################
    ################################################################################
    ################################################################################
    ################################################################################


with footer:
    st.text("Here goes extra infromation about me or the app.")