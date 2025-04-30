# streamlit_app_title_top_logo_bottom.py

import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from providian_performance_analysis_text_output_v3_modular import process_summary_multi_rent_rolls, generate_analysis_text

# --- Sidebar for file upload ---
st.sidebar.title("Upload Files")
rent_roll_files = st.sidebar.file_uploader("Upload 12 Rent Roll Excel Files", type=["xlsx"], accept_multiple_files=True)
cash_flow_file = st.sidebar.file_uploader("Upload Cash Flow Excel File", type=["xlsx"])

st.title("Executive Summary Generator")

# Text input for user-defined report title
report_title = st.text_input("Enter report title for PDF", value="Cambridge Place Townhomes - Full Property Performance Analysis")

if rent_roll_files and len(rent_roll_files) == 12 and cash_flow_file:
    with st.spinner("Processing files..."):
        months, expenses, monthly_summary = process_summary_multi_rent_rolls(rent_roll_files, cash_flow_file)
        sections = generate_analysis_text(months, expenses, monthly_summary)

    st.subheader("Property Notes")
    notes = st.text_area("Enter any additional notes to include in the summary PDF")

    if st.button("Generate PDF Summary"):
        pdf = FPDF()
        pdf.add_page()

        # Title at top
        pdf.set_font("Arial", 'B', 14)
        pdf.multi_cell(0, 10, report_title, align='C')
        pdf.ln(5)

        section_titles = {
            "Vacancy": "1. Vacancy Trend Analysis",
            "Delinquency": "2. Delinquency Trend Analysis",
            "Expenses": "3. Expense Trend Analysis",
            "Occupancy": "4. Occupancy vs Income Health",
            "Margins": "5. Operating Margin Pressure",
            "Risks": "6. Specific Risk Points",
            "Grade": "7. Overall Conclusion: Property Health Score"
        }

        for key in section_titles:
            pdf.ln(8)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, section_titles[key], ln=True)
            pdf.set_font("Arial", '', 12)
            for line in sections[key].split("\n"):
                if line.strip():
                    clean_line = line.strip().replace('–', '-').replace('—', '-')
                    if clean_line.startswith("-"):
                        pdf.cell(0, 10, clean_line, ln=True)
                    else:
                        pdf.multi_cell(0, 10, clean_line)

        if notes:
            pdf.ln(8)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Additional Notes:", ln=True)
            pdf.set_font("Arial", '', 12)
            for line in notes.splitlines():
                clean_line = line.strip().replace('–', '-').replace('—', '-')
                pdf.multi_cell(0, 10, clean_line)

        # Add logo at the bottom
        pdf.add_page()
        logo_width = 40
        logo_x = (pdf.w - logo_width) / 2
        pdf.image("Providian Logo (3).jpg", x=logo_x, y=pdf.h - 60, w=logo_width)

        pdf_buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1', 'ignore')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)

        st.success("PDF generated successfully!")
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name="Executive_Summary.pdf",
            mime="application/pdf"
        )

elif rent_roll_files and len(rent_roll_files) != 12:
    st.warning("Please upload exactly 12 Rent Roll files — one for each month.")
else:
    st.info("Please upload 12 Rent Roll files and one Cash Flow file to begin.")
