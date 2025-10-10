from urllib.parse import quote_plus
from datetime import datetime, timedelta
import random
import string

def random_meet_code():
    """Generate a fake Google Meet link (can be replaced with a real one)."""
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"https://meet.google.com/{code[:3]}-{code[3:7]}-{code[7:]}"

def google_calendar_link(title, description, start_time, duration_minutes, location):
    """Generate an Add-to-Google-Calendar RSVP link."""
    end_time = start_time + timedelta(minutes=duration_minutes)
    fmt = "%Y%m%dT%H%M%SZ"
    base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    params = (
        f"&text={quote_plus(title)}"
        f"&details={quote_plus(description)}"
        f"&location={quote_plus(location)}"
        f"&dates={start_time.strftime(fmt)}/{end_time.strftime(fmt)}"
    )
    return base + params

def whatsapp_link(phone, message):
    """Generate a WhatsApp click-to-chat link."""
    phone = ''.join(filter(str.isdigit, phone))
    return f"https://wa.me/{phone}?text={quote_plus(message)}"

def create_meeting_invite(
    phone: str,
    title: str,
    description: str,
    start_time: datetime,
    duration_minutes: int = 30,
    location: str = "Google Meet"
):
    meet_link = random_meet_code()
    gcal_link = google_calendar_link(title, f"{description}\nJoin here: {meet_link}", start_time, duration_minutes, location)
    
    message = f"""Hey 👋

📅 *{title}*
🕒 {start_time.strftime('%A, %d %b %Y at %I:%M %p')}
📍 {location}: {meet_link}

🗓 RSVP / Add to your Google Calendar:
{gcal_link}

See you then!
"""
    wa_link = whatsapp_link(phone, message)
    return wa_link, message

# Example usage:
if __name__ == "__main__":
    phone = "2348012345678"
    title = "Marketing Strategy Call"
    description = "We’ll review campaign metrics and brainstorm next steps."
    start_time = datetime(2025, 10, 11, 14, 30)  # dynamic date/time
    
    link, preview = create_meeting_invite(phone, title, description, start_time)
    print("✅ WhatsApp Link:\n", link)
    print("\n💬 Message Preview:\n", preview)
