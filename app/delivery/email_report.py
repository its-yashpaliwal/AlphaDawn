"""
Email Report — generates and sends an HTML pre-market report.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from jinja2 import Template
from loguru import logger

from app.config import settings


EMAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; background: #0f0f1a; color: #e0e0e0; padding: 24px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px; text-align: center; margin-bottom: 24px; }
    .header h1 { color: white; margin: 0; font-size: 24px; }
    .pick-card { background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .pick-card h3 { color: #667eea; margin: 0 0 8px 0; }
    .direction-long { color: #00e676; }
    .direction-short { color: #ff5252; }
    .meta { color: #888; font-size: 13px; }
    table { width: 100%; border-collapse: collapse; }
    td { padding: 4px 8px; }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 24px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>📈 AlphaDawn Report</h1>
    <p style="color: rgba(255,255,255,0.7); margin: 8px 0 0;">{{ date }}</p>
  </div>

  {% if picks %}
  {% for pick in picks %}
  <div class="pick-card">
    <h3>
      {{ '🟢' if pick.direction == 'LONG' else '🔴' }}
      {{ pick.symbol }} ({{ pick.exchange }})
    </h3>
    <table>
      <tr>
        <td>Direction</td>
        <td class="{{ 'direction-long' if pick.direction == 'LONG' else 'direction-short' }}">
          <strong>{{ pick.direction }}</strong>
        </td>
      </tr>
      <tr><td>Entry</td><td>₹{{ "%.2f"|format(pick.entry_price) }}</td></tr>
      <tr><td>Target</td><td>₹{{ "%.2f"|format(pick.target_price) }}</td></tr>
      <tr><td>Stop Loss</td><td>₹{{ "%.2f"|format(pick.stop_loss) }}</td></tr>
      <tr><td>Confidence</td><td>{{ "%.0f"|format(pick.confidence * 100) }}%</td></tr>
    </table>
    <p class="meta">{{ pick.catalyst_summary or 'N/A' }}</p>
  </div>
  {% endfor %}
  {% else %}
  <div class="pick-card">
    <p>No actionable picks today. Sit tight! 🧘</p>
  </div>
  {% endif %}

  <div class="footer">
    <p>⚠️ Not financial advice. Do your own research.</p>
    <p>AlphaDawn &copy; {{ year }}</p>
  </div>
</body>
</html>
""")


async def send_email_report(picks: list[dict]):
    """Generate and send the HTML email report."""
    if not settings.smtp_user or not settings.email_recipients:
        logger.warning("⚠️  Email not configured — skipping delivery")
        return

    from datetime import date, datetime

    recipients = [r.strip() for r in settings.email_recipients.split(",") if r.strip()]

    html = EMAIL_TEMPLATE.render(
        picks=picks,
        date=date.today().strftime("%A, %d %B %Y"),
        year=datetime.now().year,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 AlphaDawn — {date.today().isoformat()}"
    msg["From"] = settings.smtp_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=True,
        )
        logger.info(f"📧  Email report sent to {len(recipients)} recipients")
    except Exception as exc:
        logger.error(f"❌  Email delivery failed: {exc}")
