import streamlit as st
from fpdf import FPDF
import google.generativeai as genai
import time

# --- KONFIGURASI AI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def generate_text(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- TAMPILAN ---
st.title("📚 AI E-Book Mega Generator (100+ Hal)")

topik = st.text_input("Topik E-Book:", placeholder="Contoh: Panduan Lengkap Jaringan Komputer")
jml_bab = st.number_input("Jumlah Bab (Misal 20 Bab untuk ~100 hal):", min_value=1, max_value=50, value=10)

if st.button("Generate E-Book Raksasa ✨"):
    if topik:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # LANGKAH 1: Buat Outline
        status_text.text("Membuat Outline/Daftar Isi...")
        outline_prompt = f"Buat daftar isi untuk e-book tentang {topik} sebanyak {jml_bab} bab. Hanya berikan judul babnya saja."
        outline = generate_text(outline_prompt)
        
        # LANGKAH 2: Looping tulis per bab
        seluruh_isi = []
        daftar_bab = outline.split("\n")
        
        for i, bab_title in enumerate(daftar_bab):
            if bab_title.strip():
                status_text.text(f"Menulis {bab_title}...")
                # Perintah tulis 4-5 halaman per bab (sekitar 1500-2000 kata)
                prompt_bab = f"Tuliskan isi lengkap untuk {bab_title} dari e-book {topik}. Tulis minimal 1500 kata agar sangat mendalam."
                konten_bab = generate_text(prompt_bab)
                seluruh_isi.append((bab_title, konten_bab))
                
                # Update Progress
                progress = (i + 1) / len(daftar_bab)
                progress_bar.progress(progress)
                time.sleep(1) # Jeda agar tidak terkena limit API

        # LANGKAH 3: Satukan ke PDF
        status_text.text("Menyusun PDF... Mohon tunggu.")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        for title, body in seluruh_isi:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.multi_cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(5)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, body.encode('latin-1', 'replace').decode('latin-1'))
        
        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
        
        st.success(f"Selesai! {jml_bab} Bab berhasil ditulis.")
        st.download_button("Download E-Book Raksasa (PDF)", data=pdf_output, file_name="ebook_raksasa.pdf")
    else:
        st.error("Masukkan topik terlebih dahulu!")
