import streamlit as st
import flash as fd
from stream import Stream

st.set_page_config(page_title="Flash Drum app", page_icon="🔥", initial_sidebar_state="expanded")

header = st.container()
mixture = st.container()
calculations = st.container()
footer = st.container()



with header:
    st.title("FLASH DRUM PORJECT 🔥!")
    st.text("In this app you can play simulations flash drum calculations for ideal mixtures.")
    st.image("https://images.pexels.com/photos/3105242/pexels-photo-3105242.jpeg?auto=compress&cs=tinysrgb&h=750&w=1260")

with mixture:
    st.header("👩‍🔬 Prepare your mixture! 👨‍🔬")
    st.markdown("Chose at leats two comoponents and introduce its molar composition.  \n"
        "**NOTE:** the sum of the mole fractions must be equals to **ONE** (_1.0_), if it is greater than one molar compositions will be normalized.")


    components = st.multiselect(label="Choose the mixture components", options=["benzene", "chlorobenzene", "p-xylene", "toluene", "styrene"])
    

    fraction = {}    
   
    for i in components:
        fraction[i] = st.number_input(label=i, key="Component_" + i, min_value=0.0000, max_value=1.0000, step=0.0001, format = "%.4f")
    components = fd.parameters([key for key in fraction.keys()])
    




with calculations:
    st.header("Calculations and simulation 💻")
    st.markdown("Here you can find four type of calculations.  \n"
    " **NOTE:** Phase diagrams are only available for binary mixtures.")
    st.subheader("1.- Bubble and Dew points")
    flash1 = fd.FlashDrum()
    stream1 = Stream(mComposition = fraction)
    nonZero = sum([z for z in fraction.values()])
    if nonZero > 0:
        flash1.setFeedStream(stream1)
    


    with st.form(key = "BubbleT"):
        
        st.markdown("**Temperature of the Bubble point given a pressure:**")
        col1, col2 = st.columns([1, 1])
        with col1:
            
            P1 = st.number_input(label = "Pressure in kPa", min_value= 10, max_value=1100, step = 10)
            
            
            button1 = st.form_submit_button("GO!")

            if button1:
                 if nonZero > 0:

                    with col2:
                        st.markdown("__Temperature__")
                        with st.spinner('Calculating...'):
                            st.markdown("**{:.2f} K**".format(flash1.bubbleT(P1, components)))
                            st.success("Calculations complete!")
                 else:
                    st.error("Fracction values must be non-zero!")
            
            


    with st.form(key = "BubbleP"):
        st.markdown("**Pressure of the Bubble point given a temperature:**")
        col3, col4 = st.columns([1, 1])
        with col3:

            T1 = st.number_input(label = "Temperature in K", min_value=200, max_value=800, step=1)
            button2 = st.form_submit_button("GO!")

            if button2:
                if nonZero > 0:

                    with col4:
                        st.markdown("__Pressure__")
                        with st.spinner('Calculating...'):
                            st.markdown("**{:.2f} kPa**".format(flash1.bubbleP(T1, components)))
                            st.success("Calculations complete!")
                else:
                    st.error("Fracction values must be non-zero!")


    with st.form(key = "DewT"):
        
        st.markdown("**Temperature of the Dew point given a pressure:**")
        col5, col6 = st.columns([1, 1])
        with col5:
            
            P2 = st.number_input(label = "Pressure in kPa", min_value= 10, max_value=1100, step = 10)
            
            
            button3 = st.form_submit_button("GO!")

            if button3:
                 if nonZero > 0:

                    with col6:
                        st.markdown("__Temperature__")
                        with st.spinner('Calculating...'):
                            st.markdown("**{:.2f} K**".format(flash1.dewT(P2, components)))
                            st.success("Calculations complete!")
                 else:
                    st.error("Fracction values must be non-zero!")
            
            


    with st.form(key = "DewP"):
        st.markdown("**Pressure of the Dew point given a temperature:**")
        col7, col8 = st.columns([1, 1])
        with col7:

            T2 = st.number_input(label = "Temperature in K", min_value=200, max_value=800, step=1)
            button4 = st.form_submit_button("GO!")

            if button4:
                if nonZero > 0:

                    with col8:
                        st.markdown("__Pressure__")
                        with st.spinner('Calculating...'):
                            st.markdown("**{:.2f} kPa**".format(flash1.dewP(T2, components)))
                            st.success("Calculations complete!")
                else:
                    st.error("Fracction values must be non-zero!")

    st.subheader("2.- Isothermal Flash calculations")
    
    

    with st.form(key = "IsotheramlFlash"):
        st.markdown("**Isothermal flash drum calculations given a temperature and pressure:**")
        flash2 = fd.FlashDrum()
        Tfi = st.number_input(label = "Feedstream temperature in K", min_value=200, max_value=800, step=1)
        Pfi = st.number_input(label = "Feedstream pressure in kPa", min_value= 10, max_value=1100, step = 10)
        mFi = st.number_input(label = "Feedstream molar flow in mol/h", min_value= 0.01, max_value=1000000.00, step = 0.01, format= "%.2f")
        stream2 = Stream(name = "FEED", Temperature = Tfi, Pressure = Pfi, mComposition = fraction, molarFlow= mFi)
        nonZero = sum([z for z in fraction.values()])
        
        if nonZero > 0:
            flash2.setFeedStream(stream2)

        col9, col10 = st.columns([1, 2])
        with col9:
            T3 = st.number_input(label = "Drum Temperature in K", min_value=200, max_value=800, step=1)
            P3 = st.number_input(label = "Drum Pressure in kPa", min_value= 10, max_value=1100, step = 10)
            eb = st.selectbox(label = "Energy balance?", options=[True, False])
            button5 = st.form_submit_button("GO!")
            with col10:
                pass
        if button5:
            if nonZero > 0:
                
                if eb:

                    with st.spinner("Calculating..."):
                        flash2.isothermal(T3, P3, components, True)
                        st.text(flash2.Streams(True))
                        st.success("Calculations complete!")
                else:
                    with st.spinner("Calculating..."):
                        flash2.isothermal(T3, P3, components)
                        st.text(flash2.Streams())
                        st.success("Calculations complete!")
            else:
                st.error("Fracction values must be non-zero!")



            


    
with footer:
    st.text("Here goes extra infromation about me or the app.")