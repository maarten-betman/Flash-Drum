import streamlit as st

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


with calculations:
    st.header("Calculations and simulation 💻")
    st.markdown("Here you can find four type of calculations.  \n"
    " **NOTE:** Phase diagrams are only available for binary mixtures.")
    
with footer:
    st.text("Here goes extra infromation about me or the app.")