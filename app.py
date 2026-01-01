import streamlit as st
from fpdf import FPDF

# Fungsi dasar membuat PDF
def generate_pdf(judul, konten_per_bab):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Halaman Judul
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(80)
    pdf.cell(0, 10, judul.upper(), ln=True, align='C')
    
    # Isi Konten
    pdf.set_font("Helvetica", size=12)
    for bab, isi in konten_per_bab.items():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, bab, ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 7, isi) # 7 adalah line spacing agar pas 400 kata/hal
        
    return pdf.output()

st.title("🤖 AI E-Book Generator")

topic = st.text_input("Topik E-Book", placeholder="Misal: Belajar Python untuk Pemula")
pages = st.number_input("Jumlah Halaman", min_value=1, max_value=20, value=5)

if st.button("Mulai Buat E-Book"):
    total_words = pages * 400
    st.info(f"AI akan menulis kurang lebih {total_words} kata...")
    
    # SIMULASI ALUR AI
    # 1. Panggil AI untuk buat outline
    # 2. Loop per Bab dan panggil AI untuk nulis @400 kata
    
    # Contoh Dummy Data
    dummy_konten = {
        "Bab 1: Pendahuluan": "Ini adalah isi bab satu... " * 80, # Sekitar 400 kata
        "Bab 2: Pembahasan": "Ini adalah isi bab dua... " * 80
    }
    
    pdf_data = generate_pdf(topic, dummy_konten)
    
    st.download_button(
        label="Download E-Book (PDF)",
        data=pdf_data,
        file_name=f"{topic}.pdf",
        mime="application/pdf"
    )
