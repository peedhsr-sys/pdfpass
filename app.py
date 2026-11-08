from datetime import date
import io
import pypdf
import streamlit as st

st.set_page_config(
    page_title="Smart PDF Unlocker", page_icon="🔓", layout="centered"
)

st.title("🔓 Smart PDF Unlocker")
st.write(
    "PDF upload karein. Agar password yaad nahi hai toh Auto-Unlock use karein!"
)

uploaded_file = st.file_uploader("Apni PDF file yahan drop karein", type=["pdf"])

if uploaded_file is not None:
  reader = pypdf.PdfReader(uploaded_file)

  if not reader.is_encrypted:
    st.success("✅ Yeh PDF pehle se unlocked hai!")
  else:
    st.warning("🔒 Yeh PDF password se locked hai.")

    tab1, tab2 = st.tabs(
        ["🤖 Auto-Unlock (Aadhaar/PAN/Bank)", "🔑 Direct Password"]
    )

    unlocked_stream = None
    found_password = None

    # TAB 1: Auto Unlock Mode
    with tab1:
      st.info(
          "💡 Agar password bhool gaye hain, toh bas apna Naam aur DOB dalein."
          " App apne aap PAN/Aadhaar formats try karega!"
      )
      col1, col2 = st.columns(2)
      with col1:
        user_name = st.text_input(
            "Aapka Naam (First Name):", value="Arshdeep"
        ).strip()
      with col2:
        user_dob = st.date_input(
            "Date of Birth:",
            value=date(2005, 8, 1),
            min_value=date(1950, 1, 1),
            max_value=date.today(),
        )

      if st.button("⚡ Smart Auto-Unlock Karein", type="primary"):
        # Candidate combinations generate karein
        first4 = user_name[:4].upper() if len(user_name) >= 4 else user_name.upper()
        dd = user_dob.strftime("%d")
        mm = user_dob.strftime("%m")
        yyyy = user_dob.strftime("%Y")
        yy = user_dob.strftime("%y")

        candidates = [
            f"{dd}{mm}{yyyy}",  # PAN Card (DDMMYYYY) -> 01082005
            f"{first4}{yyyy}",  # Aadhaar Card (NAME4+YYYY) -> ARSH2005
            f"{first4.lower()}{yyyy}",
            f"{first4}{dd}{mm}",  # Bank format (NAME4+DDMM) -> ARSH0108
            f"{first4.lower()}{dd}{mm}",
            f"{dd}{mm}{yy}",  # DDMMYY -> 010805
            f"{first4}@{yyyy}",
            f"{first4}@{dd}{mm}",
        ]

        # Auto try combinations
        with st.spinner("Password dhundha ja raha hai..."):
          for cand in candidates:
            if reader.decrypt(cand) > 0:
              found_password = cand
              break

        if found_password:
          st.success(f"🎉 Success! Password mil gaya: `{found_password}`")
          writer = pypdf.PdfWriter()
          for page in reader.pages:
            writer.add_page(page)

          output_stream = io.BytesIO()
          writer.write(output_stream)
          output_stream.seek(0)
          unlocked_stream = output_stream
        else:
          st.error(
              "❌ Diye gaye Naam aur DOB se match nahi mila. Kripya details check"
              " karein."
          )

    # TAB 2: Direct Password Mode
    with tab2:
      direct_pwd = st.text_input("Direct Password dalein:", type="password")
      if st.button("Unlock with Password"):
        if reader.decrypt(direct_pwd) > 0:
          st.success("✅ Password match ho gaya!")
          writer = pypdf.PdfWriter()
          for page in reader.pages:
            writer.add_page(page)

          output_stream = io.BytesIO()
          writer.write(output_stream)
          output_stream.seek(0)
          unlocked_stream = output_stream
        else:
          st.error("❌ Galat password!")

    # Download Button
    if unlocked_stream:
      st.download_button(
          label="📥 Download Unlocked PDF",
          data=unlocked_stream,
          file_name=f"unlocked_{uploaded_file.name}",
          mime="application/pdf",
          type="primary",
      )
