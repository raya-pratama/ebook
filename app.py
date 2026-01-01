import streamlit as st
from fpdf import FPDF
import google.generativeai as genai

# --- KONFIGURASI AI ---
# Masukkan API Key kamu di Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def buat_pdf(judul, isi):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Judul
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, judul.upper(), ln=True, align='C')
    pdf.ln(10)
    
    # Isi
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, isi)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- TAMPILAN ---
st.title("📚 AI E-Book Generator")

topik = st.text_input("Apa topik e-book yang ingin dibuat?", placeholder="Contoh: Strategi Trading Crypto")
jml_hal = st.number_input("Jumlah Halaman (1 hal = 400 kata):", min_value=1, max_value=10, value=2)

if st.button("Generate E-Book ✨"):
    if topik:
        total_kata = jml_hal * 400
        
        with st.spinner(f"AI sedang menulis {total_kata} kata... Mohon tunggu."):
            # PROMPT UNTUK AI
            prompt = f"""Tuliskan isi e-book yang mendalam tentang {topik}. 
            Tuliskan dalam bahasa Indonesia. 
            Panjang tulisan harus sekitar {total_kata} kata.
            Gunakan struktur Bab 1, Bab 2, dst. 
            Jangan berikan teks pembuka seperti 'Tentu, ini e-booknya', langsung saja ke isinya."""
            
            response = model.generate_content(prompt)
            teks_ebook = response.text
            
            # Convert ke PDF
            pdf_bytes = buat_pdf(topik, teks_ebook)
            
            st.success("E-Book Selesai Dibuat!")
            st.download_button(
                label="Download E-Book (PDF) 📥",
                data=pdf_bytes,
                file_name=f"Ebook_{topik.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Isi topiknya dulu ya!")
