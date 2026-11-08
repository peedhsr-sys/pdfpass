import io
from google import genai
import pypdf
import streamlit as st

# Page configuration
st.set_page_config(page_title="PDF Unlocker & AI", page_icon="🔓", layout="centered")

st.title("🔓 PDF Unlocker & AI Assistant")
st.write(
    "Apni password-protected PDF upload karein aur unlocked version download"
    " karein."
)

# 1. PDF File Uploader
uploaded_file = st.file_uploader("Apni PDF file yahan drop karein", type=["pdf"])

if uploaded_file is not None:
  reader = pypdf.PdfReader(uploaded_file)

  # Check karein agar encrypted hai
  if reader.is_encrypted:
    st.warning("⚠️ Yeh PDF password se protected hai.")
    password = st.text_input(
        "Document ka Password dalein:",
        type="password",
        help="Jaise PAN ke liye DOB (DDMMYYYY) ya Aadhaar ke liye (ARSH2005)",
    )
  else:
    st.success("✅ Yeh PDF pehle se unlocked hai!")
    password = ""

  # Unlock button
  if st.button("🚀 Unlock & Process PDF"):
    try:
      if reader.is_encrypted:
        if not password:
          st.error("Kripya pehle password dalein!")
          st.stop()

        status = reader.decrypt(password)
        if status == 0:
          st.error("❌ Galat password! Decrypt nahi ho saka.")
          st.stop()

      # Unlocked PDF memory mein create karein
      writer = pypdf.PdfWriter()
      for page in reader.pages:
        writer.add_page(page)

      output_stream = io.BytesIO()
      writer.write(output_stream)
      output_stream.seek(0)

      st.success("🎉 PDF kamyabi se unlock ho gayi!")

      # Download button
      st.download_button(
          label="📥 Download Unlocked PDF",
          data=output_stream,
          file_name=f"unlocked_{uploaded_file.name}",
          mime="application/pdf",
      )

      # Optional: Text analysis
      text = "".join(
          [page.extract_text() or "" for page in reader.pages]
      ).strip()
      if text and "GEMINI_API_KEY" in st.secrets:
        with st.expander("🤖 Gemini AI Document Summary dekhein"):
          client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
          res = client.models.generate_content(
              model="gemini-2.5-flash",
              contents=f"Summarize this document:\n\n{text[:4000]}",
          )
          st.write(res.text)

    except Exception as e:
      st.error(f"Error aaya: {str(e)}")
