import streamlit as st
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Ordo Mail", page_icon="📧")
st.title("📧 Ordo – Skicka e-post")

st.write("Fyll i och klicka **Skicka**. Appen använder säkra *secrets* för din e-post.")

with st.form("mailform"):
    to_email = st.text_input("Mottagare", placeholder="namn@example.com")
    subject = st.text_input("Ämne", placeholder="Förslag på mötestid – genomgång av elritning")
    body = st.text_area("Meddelande", height=200, placeholder="Hej ...")
    send_btn = st.form_submit_button("Skicka")

if send_btn:
    if not to_email or not subject or not body:
        st.error("Fyll i mottagare, ämne och meddelande.")
    else:
        try:
            email_address = st.secrets["EMAIL_ADDRESS"]
            app_password = st.secrets["APP_PASSWORD"]
            smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(st.secrets.get("SMTP_PORT", 587))

            msg = MIMEText(body, _charset="utf-8")
            msg["Subject"] = subject
            msg["From"] = email_address
            msg["To"] = to_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_address, app_password)
                server.sendmail(email_address, [to_email], msg.as_string())

            st.success(f"✅ E-post skickat till {to_email}")
        except KeyError as e:
            st.error(f"Saknar secret: {e}. Lägg till EMAIL_ADDRESS och APP_PASSWORD i appens Secrets.")
        except Exception as e:
            st.error(f"Något gick fel: {e}")
            st.info("Kontrollera att app-lösenordet är korrekt och att SMTP inte blockeras.")
