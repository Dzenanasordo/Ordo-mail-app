# 📦 Importer
import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import json

# 🔑 Läs nyckel från GitHub Secrets
SERVICE_ACCOUNT = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# 📄 Google Sheet-inställningar
SHEET_ID = "1j6LjaiyaLb0gJk1rRGgUHz1rpniQ46j-ZUBbH6tyCxc"
SHEET_TAB = "task"

# 🔗 Anslut till Google Sheets
creds = Credentials.from_service_account_info(
    SERVICE_ACCOUNT,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB)

# ✅ Bekräfta anslutning
st.write("✅ Lyckad anslutning till Google Sheet:", sheet.title)

# 📱 Layout och stil för mobil
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    body {font-size: 18px;}
    textarea, input, select {font-size: 18px !important;}
    .stButton>button {font-size: 18px !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# 🧠 Titel och intro
st.title("🤖 Ordo – Din personliga AI-agent")
st.write("Håll koll på ditt byggprojekt, deadlines och skapa professionella mejl.")

# 📌 Session state
if "deadlines" not in st.session_state:
    st.session_state.deadlines = []

if "mails" not in st.session_state:
    st.session_state.mails = []

# 🗂️ Flikar
tab1, tab2, tab3 = st.tabs(["📋 Deadlines & Checklista", "📧 Mejlmallar", "📊 Byggstatus"])

# ========================
# 📋 DEADLINES & CHECKLISTA
# ========================
with tab1:
    st.subheader("Lägg till deadline")
    col1, col2 = st.columns([2, 1])

    with col1:
        task = st.text_input("Uppgift", placeholder="Boka elektriker, godkänna offert …")
    with col2:
        d = st.date_input("Datum", value=date.today())

    if st.button("Lägg till deadline"):
        if task.strip():
            st.session_state.deadlines.append({"task": task.strip(), "date": str(d)})
            st.success(f"Deadline tillagd: **{task}** – {d}")
        else:
            st.warning("Skriv en uppgift först.")

    st.divider()
    st.subheader("Mina deadlines")

    if st.session_state.deadlines:
        for item in st.session_state.deadlines:
            days_left = (date.fromisoformat(item['date']) - date.today()).days
            st.write(f"📌 **{item['task']}** – {item['date']} _(om {days_left} dagar)_")

        if st.button("Rensa alla deadlines"):
            st.session_state.deadlines = []
            st.info("Alla deadlines rensade.")
    else:
        st.info("Inga deadlines tillagda ännu.")

# ================
# 📧 MEJLMALLAR
# ================
with tab2:
    st.subheader("Skapa mejl (kopiera till Gmail)")

    templates = {
        "Förfrågan om offert": (
            "Ämne: Förfrågan om offert – {delmoment}\n\n"
            "Hej {namn},\n\n"
            "Vi planerar {delmoment} i vårt husbygge och vill gärna få en uppdaterad offert.\n"
            "Underlag: {underlag}.\n\n"
            "Kan du återkomma med pris, tidsplan och eventuella förutsättningar?\n\n"
            "Vänliga hälsningar,\nDženana"
        ),
        "Uppföljning på offert": (
            "Ämne: Uppföljning – offert {delmoment}\n\n"
            "Hej {namn},\n\n"
            "Jag vill följa upp offerten gällande {delmoment}. Har du möjlighet att återkomma?\n"
            "Vi planerar beslut senast {deadline}.\n\n"
            "Vänliga hälsningar,\nDženana"
        ),
        "Bekräftelse på möte": (
            "Ämne: Bekräftelse möte – {ämne}\n\n"
            "Hej {namn},\n\n"
            "Bekräftar vårt möte {datum} kl {tid} om {ämne}. Vi ses via {plats}.\n\n"
            "Agenda:\n- {punkt1}\n- {punkt2}\n- {punkt3}\n\n"
            "Vänliga hälsningar,\nDženana"
        ),
        "Påminnelse om deadline": (
            "Ämne: Påminnelse – {ärende}\n\n"
            "Hej {namn},\n\n"
            "En vänlig påminnelse om {ärende}. Vi behöver besked senast {deadline}.\n\n"
            "Tack!\nDženana"
        ),
        "Statusförfrågan till entreprenör": (
            "Ämne: Statusförfrågan – {delmoment}\n\n"
            "Hej {namn},\n\n"
            "Hur ligger vi till med {delmoment}? Är det något som blockerar eller där du behöver input?\n"
            "Nuvarande plan säger {plan_info}.\n\n"
            "Tack på förhand!\nDženana"
        )
    }

    val = st.selectbox("Välj mall", list(templates.keys()))

    with st.form("form_mail"):
        f_namn = st.text_input("Namn", "Elektrikern")
        f_delmoment = st.text_input("Delmoment", "elritning och tillval våning 1")
        f_underlag = st.text_input("Underlag", "ritning v2 + tillvalslista")
        f_deadline = st.text_input("Deadline (datum)", "2025-09-20")
        f_ämne = st.text_input("Ämne (möte)", "Genomgång av elritning och offert")
        f_plats = st.text_input("Plats/format", "Telefon/Teams")
        f_datum = st.text_input("Datum", "imorgon")
        f_tid = st.text_input("Tid", "09:00")
        f_p1 = st.text_input("Agenda 1", "Genomgång elritning")
        f_p2 = st.text_input("Agenda 2", "Tillval våning 1")
        f_p3 = st.text_input("Agenda 3", "Uppdaterad offert")

        ok = st.form_submit_button("Skapa text")

    if ok:
        text = templates[val].format(
            namn=f_namn,
            delmoment=f_delmoment,
            underlag=f_underlag,
            deadline=f_deadline,
            ämne=f_ämne,
            plats=f_plats,
            datum=f_datum,
            tid=f_tid,
            punkt1=f_p1,
            punkt2=f_p2,
            punkt3=f_p3,
            plan_info="enligt senaste tidsplan"
        )
        st.text_area("Kopiera och klistra in i Gmail:", value=text, height=280)

# ===============
# 📊 BYGGSTATUS
# ===============
with tab3:
    st.subheader("Veckosammanfattning")
    if st.session_state.deadlines:
        open_items = sorted(st.session_state.deadlines, key=lambda x: x["date"])
        lines = [f"📌 {it['task']} (deadline: {it['date']})" for it in open_items]
        st.text_area("Sammanfattning", "\n".join(lines), height=220)
    else:
        st.info("Lägg till några deadlines i första fliken så visas sammanfattningen här.")
