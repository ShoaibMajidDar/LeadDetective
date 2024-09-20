import streamlit as st

from controller.contracts import get_company_contracts
from controller.email import verify_email
from controller.relationship import get_relationship



def main():
    if "person_name" not in st.session_state:
        st.session_state.person_name = None
    if "person_email" not in st.session_state:
        st.session_state.person_email = None
    if "company_name" not in st.session_state:
        st.session_state.company_name = None
        st.session_state.number = None
        st.session_state.verified = None
        st.session_state.domain_name= None
        st.session_state.relationship = None
        st.session_state.contracts = None
        st.session_state.flag = None



    if st.session_state.flag is None or st.session_state.flag == False:
        st.session_state.person_name = st.text_input("Enter the name of the person")
        st.session_state.person_email = st.text_input("Enter the email of the person")
        st.session_state.number = st.text_input("Enter the phone number of the person")
        st.session_state.company_name = st.text_input("Enter the name of the company here")
    
        st.session_state.flag = st.button("verify lead")

    if st.session_state.flag and st.session_state.person_name and st.session_state.person_email and st.session_state.company_name:
        st.session_state.verified, st.session_state.domain_name = verify_email(st.session_state.person_email)
        if st.session_state.verified:
            st.write("Email is valid")
        else:
            st.write("Email is not valid")


        st.session_state.relationship = get_relationship(st.session_state.person_name, st.session_state.company_name)
        rel = st.session_state.relationship["relationship"]
        st.write(f"{st.session_state.person_name} is the {rel} of {st.session_state.company_name}")


        st.write(st.session_state.domain_name)

        if st.button("Verify Number and Get Company Contracts"):
            with st.spinner("Working..."):
                st.session_state.contracts, number_verification_flag = get_company_contracts(st.session_state.domain_name, st.session_state.company_name, st.session_state.number)
                if number_verification_flag: st.write("Number is from the website")
                else: ("Number is not from the website")
                st.write(st.session_state.contracts)
        
    if st.button("check new lead"):
        st.session_state.flag = False
        st.session_state.company_name = None
        st.session_state.person_email = None
        st.session_state.person_name = None
        st.session_state.verified = None
        st.session_state.domain_name= None
        st.session_state.relationship = None
        st.session_state.contracts = None



if __name__ == "__main__":
    main()