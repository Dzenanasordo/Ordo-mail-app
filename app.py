import streamlit as st
from datetime import datetime, timedelta
import json

# Titel och intro
st.title("🛠️ Ordo – Din personliga AI-agent")
st.write("Håll koll på ditt byggprojekt, deadlines och skapa professionella mejl.")

# Spara data i session
if "deadlines" not in st.session_state:
    st.session_state.deadlines = []

if "mails" not in st.session_state:
    st.session_state.mails = []

# Flikar
tab1, tab2, tab3 = st.tabs(["📅 Deadlines & Checklista", "📧 Mejlmallar", "📊 Byggstatus"])

# --- DEADLINES & CHECKLISTA ---
with tab1:
    st.subheader("Lägg till deadline")
    task = st.text_input("Uppgift")
    date = st.date_input("Datum", datetime.today())
    if st.button("Lägg till deadline"):
        st.session_state.deadlines.append({"task": task, "date": str(date)})
        st.success(f"Deadline tillagd: {task} – {date}")

    st.subheader("Mina deadlines")
    if st.session_state.deadlines:
        for d in st.session_state.deadlines:
            days_left = (datetime.fromisoformat(d['date']) - datetime.today()).days
            st.write(f"**{d['task']}** – {d['date']} ({days_left} dagar kvar)")
    else:
        st.write("Inga deadlines tillagda.")

# --- MEJLMALLAR ---
with tab2:
    st.subheader("Skapa mejl")
    recipient = st.text_input("Mottagare")
    subject = st.text_input("Ämne")
    body = st.text_area("Meddelande")
    if st.button("Spara mejl"):
        st.session_state.mails.append({"to": recipient, "subject": subject, "body": body})
        st.success("Mejl sparat.")

    st.subheader("Sparade mejl")
    for m in st.session_state.mails:
        st.markdown(f"**Till:** {m['to']}  \n**Ämne:** {m['subject']}  \n{m['body']}")

# --- BYGGSTATUS ---
with tab3:
    st.subheader("Sammanfattning av byggstatus")
    if st.button("Generera veckosammanfattning"):
        if st.session_state.deadlines:
            summary = "🔹 Veckans byggstatus:\n"
            for d in st.session_state.deadlines:
                summary += f"- {d['task']} (deadline {d['date']})\n"
            st.text_area("Sammanfattning", summary, height=150)
        else:
            st.warning("Inga deadlines att sammanfatta.")
