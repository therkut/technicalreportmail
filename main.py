import imaplib
import email
from email.mime.text import MIMEText
import smtplib
from datetime import date
import pandas as pd
import os
from bs4 import BeautifulSoup
from typing import List, Optional

# Sabitler
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.mail.yahoo.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.mail.yahoo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
HISSE_LISTESI_FILE = "data/katilim.txt"

def load_hisse_listesi(file_path: str = HISSE_LISTESI_FILE) -> List[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip().rstrip(",") for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{file_path} bulunamadı.")
        return []

def get_latest_email() -> Optional[str]:
    if not EMAIL or not PASSWORD:
        print("E-posta veya şifre tanımlı değil.")
        return None

    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
            mail.login(EMAIL, PASSWORD)
            mail.select("RAPOR")
            today = date.today().strftime("%d-%b-%Y")
            result, data = mail.search(None, f'SINCE {today}')

            if not data[0]:
                print("Bugün RAPOR klasöründe e-posta yok.")
                return None

            latest_id = data[0].split()[-1]
            _, msg_data = mail.fetch(latest_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode()
            print("HTML içerik bulunamadı.")
            return None
    except Exception as e:
        print(f"E-posta alma hatası: {e}")
        return None

def parse_and_filter_table(html_content: Optional[str], hisse_listesi: List[str]) -> Optional[pd.DataFrame]:
    if not html_content:
        print("HTML içerik boş.")
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        headers = [th.text.strip() for th in table.find_all("th")]
        if "Hisse" in headers:
            expected_cols = len(headers)
            rows = []
            for tr in table.find_all("tr")[1:]:
                cells = [td.text.strip() for td in tr.find_all("td")]
                if cells:
                    cells = cells[:expected_cols] if len(cells) > expected_cols else cells + [""] * (expected_cols - len(cells))
                    rows.append(cells)

            if not rows:
                print("Tabloda veri satırı yok.")
                return None

            df = pd.DataFrame(rows, columns=headers)
            filtered_df = df[df["Hisse"].isin(hisse_listesi)].copy()
            filtered_df["Sinyal_Order"] = filtered_df["Sinyal"].map({"Al": 0, "Sat": 1})
            filtered_df = filtered_df.sort_values("Sinyal_Order").drop(columns=["Sinyal_Order"])
            print(f"Filtrelenmiş satır sayısı: {len(filtered_df)}")
            return filtered_df

    print("Veri tablosu bulunamadı.")
    return None

def generate_html_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>Filtrelenecek hisse bulunamadı.</p>"

    styled_html = '<table cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse;">'
    styled_html += '<tr style="background-color:#f5f5f5;">' + "".join(
        f'<th style="padding:12px 8px;border:1px solid #e0e0e0;font-size:12px;font-weight:600;color:#2c3e50;">{col}</th>'
        for col in df.columns
    ) + "</tr>"

    for i, row in df.iterrows():
        bg_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
        sinyal_style = "background-color:#28a745;color:white;padding:4px 8px;border-radius:4px;" if row["Sinyal"] == "Al" else "background-color:#dc3545;color:white;padding:4px 8px;border-radius:4px;"
        hacim_style = "color:#28a745;font-weight:bold;" if row["Hacim %"].startswith("+") else "color:#dc3545;font-weight:bold;"
        styled_html += f"""
        <tr style="background-color:{bg_color};">
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;"><strong>{row['Hisse']}</strong></td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['Son Fiyat']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['RSI']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['Pivota Göre']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['EMA Str.']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;"><span style="{sinyal_style}">{row['Sinyal']}</span></td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['Sharpe']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;"><span style="{hacim_style}">{row['Hacim %']}</span></td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['Stop']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['H1']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['H2']}</td>
            <td style="padding:12px 8px;border:1px solid #e0e0e0;text-align:center;">{row['H3']}</td>
        </tr>
        """
    styled_html += "</table>"
    return styled_html

def send_filtered_email(filtered_df: Optional[pd.DataFrame]) -> None:
    if filtered_df is None or filtered_df.empty:
        print("Gönderilecek veri yok.")
        return

    today = date.today().strftime("%d %B %Y")
    html_content = f"""
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:600px;margin:0 auto;background-color:#ffffff;border-radius:8px;">
        <tbody>
            <tr>
                <td style="padding:25px;text-align:center;">
                    <h2 style="margin:0;font-size:24px;color:#333;">Filtrelenmiş Günlük Teknik Analiz Raporu<br>{today}</h2>
                </td>
            </tr>
            <tr>
                <td style="padding:20px;">
                    {generate_html_table(filtered_df)}
                </td>
            </tr>
            <tr>
                <td style="padding:20px;">
                    <div style="background-color:#fff3e0;padding:15px;border-radius:8px;text-align:center;color:#e65100;font-size:13px;font-weight:600;">
                        ⚠️ YASAL UYARI: Bu rapor bilgilendirme amaçlıdır, yatırım tavsiyesi içermez.
                    </div>
                </td>
            </tr>
            <tr>
                <td style="background-color:#f5f5f5;padding:20px;text-align:center;border-top:1px solid #e0e0e0;">
                    <p style="margin:0 0 10px 0;font-size:12px;color:#666;">Bu liste BIST Katılım Pay Endeksine göre filtrelenmiştir.</p>
                    <p style="margin:0 0 10px 0;font-size:12px;color:#666;">Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıt vermeyiniz.</p>
                    <p style="margin:0;font-size:12px;color:#666;">Author: © 2025 by Alper INCE, Edited by: @Magnus Trade</p>
                </td>
            </tr>
        </tbody>
    </table>
    """

    msg = MIMEText(html_content, "html", "utf-8")
    msg["Subject"] = "Filtrelenmiş Hisse Raporu"
    msg["From"] = f"KATILIM TEKNIK <{EMAIL}>"
    msg["To"] = EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print("Filtrelenmiş rapor HTML formatında başarıyla gönderildi.")
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")

def main():
    hisse_listesi = load_hisse_listesi()
    if not hisse_listesi:
        print("Hisse listesi boş.")
        return

    print(f"Filtrelenecek hisse listesi: {hisse_listesi[:10]}... (Toplam: {len(hisse_listesi)})")
    email_content = get_latest_email()
    filtered_df = parse_and_filter_table(email_content, hisse_listesi)
    send_filtered_email(filtered_df)

if __name__ == "__main__":
    main()
