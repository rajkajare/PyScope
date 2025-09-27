import streamlit as st
from logic import new_negative_update, new_positive_update, reset, get_options, start_engine, get_path

st.set_page_config(page_title="Package Explorer", page_icon="📦", layout="wide")

options = ["", "Python's Package/Module", "Custom Package/Module Path"]

# Top layout
col1, col2 = st.columns([8, 1])
with col1:
    st.title("📦 Package Explorer")
with col2:
    if st.button("RESET", type="primary"):
        st.session_state.selected = options[0]   # reset to default
        reset()   # call reset from logic.py if defined

# Tabs
tab1, tab2 = st.tabs(["Home", "Explore"])

with tab1:
    # Session state for selectbox
    if "selected" not in st.session_state:
        st.session_state.selected = options[0]

    select_input = st.selectbox(
        "Select Input",
        options,
        index=options.index(st.session_state.selected),
        key="selected"
    )

    # If "Python's Package/Module" is selected
    if select_input == "Python's Package/Module":
        with st.form("explore_form"):
            give_input = st.text_input("Enter Python's Package/Module Name")
            if st.form_submit_button("Submit"):
                start_engine(give_input)
                st.success("✅ Success : Please go to Explore tab")

    # If "Custom Package/Module Path" is selected
    elif select_input == "Custom Package/Module Path":
        with st.form("explore_form"):
            give_input = st.text_input("Enter Path")
            if st.form_submit_button("Submit"):
                start_engine(give_input)
                st.success("✅ Success : Please go to Explore tab")

with tab2:
    if st.button("Back", type="primary"):
        new_negative_update()

    st.subheader(get_path())
    result = get_options()

    cols_per_row = 5
    for i in range(0, len(result), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, item in enumerate(result[i:i+cols_per_row]):
            with cols[j]:
                if st.button(item):
                    new_positive_update(item)
