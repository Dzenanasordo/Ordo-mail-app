import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Ordo – Smart Mail & Invite", page_icon="📧")
st.title("📧 Ordo – Skriv naturligt, få mejl + kalenderinbjudan")

st.write("Skriv ett kommando som: "
         "_“Boka elektriker imorgon 09:00, gå igenom elritning & uppdatera offert. Skicka agenda.”_")

def parse_command(cmd: str):
    cmd_low = cmd.lower()
    m_time = re.search(r'(\d{1,2}):(\d{2})', cmd_low)
    hour, minute = (9,0)
    if m_time:
        hour, minute = int(m_time.group(1)), int(m_time.group(2))
    date = datetime.now()
    if "imorgon" in cmd_low or "i morgon" in cmd_low:
        date = date + timedelta(days=1)
    subject = "Mötesförslag"
    m_subj = re.search(r'boka\s+(.+)', cmd_low)
    if m_subj:
        subject = "Boka " + m_subj.group(1).split(",")[0].strip().capitalize()
    agenda = cmd.strip() or "Genomgång enligt överenskommelse."
    start = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    end = start + timedelta(minutes=30)
    return subject, agenda, start, end

def build_ics(subject, description, start_dt, end_dt, organizer_email, attendee_email=None, location="Telefon/Teams"):
    def fmt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")
    uid = f"{int(datetime.timestamp(start_dt))}@ordo"
    ics = []
    ics.append("BEGIN:VCALENDAR")
    ics.append("PRODID:-//Ordo//Mail+ICS//EN")
    ics.append("VERSION:2.0")
    ics.append("CALSCALE:GREGORIAN")
    ics.append("METHOD:REQUEST")
    ics.append("BEGIN:VEVENT")
    ics.append(f"UID:{uid}")
    ics.append(f"DTSTAMP:{fmt(datetime.utcnow())}Z")
    ics.append(f"DTSTART:{fmt(start_dt)}")
    ics.append(f"DTEND:{fmt(end_dt)}")
    ics.append(f"SUMMARY:{subject}")
    ics.append(f"DESCRIPTION:{description}")
    ics.append(f"LOCATION:{location}")
    ics.append(f"ORGANIZER:mailto:{organizer_email}")
    if attendee_email:
        ics.append(f"ATTENDEE;CN=Elektriker;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee_email}")
    ics.append("END:VEVENT")
    ics.append("END:VCALENDAR")
    return "\r\n".join(ics)

EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS")
APP_PASSWORD  = st.secrets.get("APP_PASSWORD")
SMTP_SERVER   = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT     = int(st.secrets.get("SMTP_PORT", 587))

with st.form("ordo"):
    to_email = st.text_input("Mottagare (t.ex. elektrikern)", placeholder="namn@example.com")
    command = st.text_area("Skriv ditt kommando", height=120, placeholder="Boka elektriker imorgon 09:00 ...")
    auto_send = st.checkbox("Skicka direkt (annars visas utkast först)", value=False)
    submit = st.form_submit_button("Kör")

if submit:
    if not EMAIL_ADDRESS or not APP_PASSWORD:
        st.error("Saknar Secrets: EMAIL_ADDRESS eller APP_PASSWORD.")
    elif not to_email or not command:
        st.error("Fyll i mottagare och kommando.")
    else:
        subj, agenda, start_dt, end_dt = parse_command(command)
        st.info(f"📅 Tolkat: {start_dt.strftime('%Y-%m-%d %H:%M')} – ämne: {subj}")

        ics_str = build_ics(subj, agenda, start_dt, end_dt, EMAIL_ADDRESS, attendee_email=to_email)
        ics_bytes = ics_str.encode("utf-8")

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = f"{subj}"

        body_text = f"Hej,\n\nFörslag: {start_dt.strftime('%Y-%m-%d kl. %H:%M')}.\n\nAgenda:\n{agenda}\n\nVänliga hälsningar,\nDženana"
        msg.attach(MIMEText(body_text, "plain", _charset="utf-8"))

        part = MIMEApplication(ics_bytes, Name="invite.ics")
        part.add_header("Content-Disposition", 'attachment; filename="invite.ics"')
        part.add_header("Content-Class", "urn:content-classes:calendarmessage")
        msg.attach(part)

        if not auto_send:
            st.subheader("Utkast – det här skickas:")
            st.code(body_text, language="text")
            st.download_button("Ladda ner .ics (kalenderinbjudan)", data=ics_bytes, file_name="invite.ics", mime="text/calendar")
            st.success("🔎 Kolla utkastet ovan. Kryssa i 'Skicka direkt' för att sända.")
        else:
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_ADDRESS, APP_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, [to_email], msg.as_string())
                st.success(f"✅ Mejlet skickades till {to_email} med .ics-inbjudan.")
            except Exception as e:
                st.error(f"Fel vid utskick: {e}")
