import pandas as pd
import streamlit as st
from controller.contracts import get_company_contracts
from controller.email import verify_email
from controller.relationship import get_relationship


def verify_df(df: pd.DataFrame):

    df["email verified"] = None
    df["designation verified"] = None
    df["contracts"] = None
    df["number verified"] = None

    all_websites_contracts = {}
    all_websites_texts = {}
    for i in range(len(df)):
        company_name = df.iloc[i]["Company Name"]
        person_name = df.iloc[i]["POC Name"]
        website = df.iloc[i]["Website"]
        designation = df.iloc[i]["Designation"]
        number = df.iloc[i]["Contact Number"]
        email = df.iloc[i]["Email Address"]

        email_verified = verify_email(email)
        df.loc[i, "email verified"] = email_verified

        verify_designation = get_relationship(person_name, company_name, designation)
        df.loc[i,"designation verified"] = verify_designation

        contracts, number_verification_flag, all_websites_contracts, all_websites_texts = get_company_contracts(website, company_name, number, all_websites_contracts, all_websites_texts)
        df.loc[i,"contracts"] = contracts

        df.loc[i,"number verified"] = number_verification_flag
        st.write(df.iloc[i:i+1])
        
    return df


