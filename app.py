import streamlit as st
import pandas as pd

from controller.verifydataframe import verify_df


def main():
    # Initialize session state variables if they don't exist
    if "flag" not in st.session_state:
        st.session_state.flag = False
        st.session_state.uploaded_file = None

    # File upload section
    if not st.session_state.flag:
        st.session_state.uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=['csv', 'xlsx'])

        if st.session_state.uploaded_file is not None:
            # Check for button click, set the flag when clicked
            if st.button("Verify"):
                st.session_state.flag = True

    # Verification section
    if st.session_state.flag and st.session_state.uploaded_file is not None:
        try:
            # Handle both CSV and Excel file types
            file_extension = st.session_state.uploaded_file.name.split(".")[-1].lower()
            if file_extension == "csv":
                df = pd.read_csv(st.session_state.uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(st.session_state.uploaded_file)
            else:
                st.error("Unsupported file format.")
                return

            # Verify the DataFrame
            verified_df = verify_df(df)
            st.write("Verified Data:")
            st.write(verified_df)

            # Convert verified DataFrame to CSV
            csv_data = verified_df.to_csv(index=False)

            # Download button for verified data
            st.download_button(label='Download Verified Data', data=csv_data, file_name='verified_df.csv', mime='text/csv')

        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    main()
