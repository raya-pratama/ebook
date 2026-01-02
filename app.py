import streamlit as st
from fpdf import FPDF
import google.generativeai as genai
import time

# --- 1. KONFIGURASI AI (KEAMANAN EKSTRA) ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key belum diset di Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inisialisasi model dengan fallback (cadangan)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- 2. MEMORI APLIKASI ---
if 'isi_buku' not in st.session_state:
    st.session_state.isi_buku = []
if 'daftar_bab' not in st.session_state:
    st.session_state.daftar_bab = []

st.title("📚 AI Mega Book Creator")

# --- 3. INPUT ---
topik = st.text_input("Topik Buku:", placeholder="Contoh: Belajar Jaringan dari Nol")
jml_bab_target = st.number_input("Target Total Bab:", min_value=1, value=5)

# --- 4. PROSES OUTLINE ---
if st.button("Langkah 1: Buat Outline"):
    try:
        with st.spinner("Menghubungi AI..."):
            prompt = f"Buat daftar isi e-book tentang {topik} sebanyak {jml_bab_target} bab. Berikan hanya judul bab per baris tanpa angka."
            response = model.generate_content(prompt)
            # Membersihkan hasil teks dari AI
            lines = response.text.split('\n')
            st.session_state.daftar_bab = [l.strip() for l in lines if l.strip()]
            st.success("Outline berhasil dibuat!")
    except Exception as e:
        st.error(f"Gagal menghubungi AI: {e}. Pastikan API Key benar dan aktif.")

# --- 5. PROSES PENULISAN (SISTEM CICIL) ---
if st.session_state.daftar_bab:
    done = len(st.session_state.isi_buku)
    total = len(st.session_state.daftar_bab)
    
    st.progress(done / total if total > 0 else 0)
    st.write(f"Progres: {done} / {total} Bab")

    if done < total:
        if st.button(f"Tulis Bab Selanjutnya: {st.session_state.daftar_bab[done]}"):
            try:
                with st.spinner("AI sedang menulis..."):
                    target_bab = st.session_state.daftar_bab[done]
                    prompt_isi = f"Tulis isi bab '{target_bab}' untuk buku '{topik}'. Tulis sangat detail, minimal 800 kata."
                    res = model.generate_content(prompt_isi)
                    st.session_state.isi_buku.append((target_bab, res.text))
                    st.rerun()
            except Exception as e:
                st.error(f"Error saat menulis: {e}")

# --- 6. RAKIT PDF ---
if len(st.session_state.isi_buku) > 0:
    if st.button("Langkah 2: Rakit PDF & Download"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        for t, b in st.session_state.isi_buku:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            # Menghindari karakter non-latin yang bikin error
            pdf.multi_cell(0, 10, t.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, b.encode('latin-1', 'replace').decode('latin-1'))
        
        # SANGAT PENTING: Gunakan bytes() agar tidak error unsupported data
        pdf_bytes = bytes(pdf.output())
        st.download_button("Klik untuk Download PDF", data=pdf_bytes, file_name="buku_ai.pdf", mime="application/pdf")

if st.button("Reset"):
    st.session_state.isi_buku = []
    st.session_state.daftar_bab = []
    st.rerun()
