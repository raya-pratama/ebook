import streamlit as st
from fpdf import FPDF
import google.generativeai as genai
import time

# --- KONFIGURASI AI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # Gunakan flash agar lebih cepat

# --- INISIALISASI SESSION STATE (Memori Penyimpanan) ---
if 'isi_buku' not in st.session_state:
    st.session_state.isi_buku = [] # List untuk menyimpan (Judul Bab, Teks)
if 'daftar_bab' not in st.session_state:
    st.session_state.daftar_bab = []

st.set_page_config(page_title="AI Book Mega Creator", page_icon="📚")
st.title("📚 AI Mega E-Book Creator")
st.write("Gunakan sistem cicil untuk membuat buku hingga ratusan halaman.")

# --- INPUT USER ---
topik = st.text_input("Topik E-Book:", placeholder="Contoh: Sejarah Lengkap Peradaban Dunia")
jml_bab_target = st.number_input("Target Total Bab (Misal 25 bab untuk ~100 hal):", min_value=1, value=10)

# --- LANGKAH 1: BUAT OUTLINE ---
if st.button("1. Buat Outline Daftar Isi"):
    with st.spinner("AI sedang merancang struktur buku..."):
        prompt_outline = f"Buat daftar isi untuk buku tentang {topik} sebanyak {jml_bab_target} bab. Berikan hanya judul bab-babnya saja, dipisahkan dengan baris baru."
        response = model.generate_content(prompt_outline)
        st.session_state.daftar_bab = [line.strip() for line in response.text.split('\n') if line.strip()]
        st.success(f"Outline selesai! {len(st.session_state.daftar_bab)} bab siap ditulis.")

# --- LANGKAH 2: CICIL PENULISAN ---
if st.session_state.daftar_bab:
    st.subheader("Progress Penulisan")
    current_done = len(st.session_state.isi_buku)
    total_bab = len(st.session_state.daftar_bab)
    
    st.write(f"Selesai: {current_done} dari {total_bab} bab")
    
    if current_done < total_bab:
        if st.button(f"Tulis 3 Bab Selanjutnya ({current_done + 1} - {min(current_done + 3, total_bab)})"):
            bab_to_write = st.session_state.daftar_bab[current_done : current_done + 3]
            
            for bab_title in bab_to_write:
                with st.status(f"Menulis {bab_title}...", expanded=True):
                    prompt_bab = f"Tuliskan isi lengkap dan mendalam untuk {bab_title} dari buku {topik}. Tulis sekitar 800-1000 kata dengan detail yang tajam."
                    response = model.generate_content(prompt_bab)
                    st.session_state.isi_buku.append((bab_title, response.text))
                    st.write("Bab selesai ditulis.")
            st.rerun()

# --- LANGKAH 3: RAKIT PDF ---
if len(st.session_state.isi_buku) > 0:
    st.divider()
    st.subheader("Selesaikan Buku")
    
    if st.button("2. Rakit Semua Bab Jadi PDF"):
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            for title, body in st.session_state.isi_buku:
                pdf.add_page()
                # Header
                pdf.set_font("Arial", 'B', 16)
                pdf.multi_cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(5)
                # Body
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 8, body.encode('latin-1', 'replace').decode('latin-1'))
            
            pdf_bytes = bytes(pdf.output())
            
            st.download_button(
                label="📥 Download E-Book Lengkap",
                data=pdf_bytes,
                file_name=f"Ebook_{topik.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Gagal merakit PDF: {e}")

if st.button("Reset Semua"):
    st.session_state.isi_buku = []
    st.session_state.daftar_bab = []
    st.rerun()
