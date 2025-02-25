# Teknik Analiz Raporu Filtreleme ve E-posta Gönderme

Bu proje, Yahoo Mail üzerinden gelen günlük teknik analiz raporlarını okuyarak, BIST Katılım Pay Endeksine göre filtrelenmiş hisse listesini içeren bir e-posta oluşturur ve gönderir. Python ile geliştirilmiş olup, GitHub Actions ile her gün otomatik olarak çalıştırılır.

## Amaç
- "RAPOR" klasöründen günlük teknik analiz raporunu çekmek.
- Belirtilen hisse listesine (`data/katilim.txt`) BIST Katılım endeksindekilerine göre raporu filtrelemek.
- Filtrelenmiş raporu HTML formatında e-posta olarak göndermek.

## Özellikler
- **E-posta Konusu**: `Filtrelenmiş Hisse Raporu` 
- **Gönderici**: `KATILIM TEKNIK <email@yahoo.com>` (Buradaki adresi yahoo mail adresiniz ile değiştiriniz.)
- **Ek Bilgi**: "Yahoo E-Mail alt yapısına göre düzenlenmiştir."

## Gereksinimler
- Python 3.11
- Kütüphaneler:
  - `imaplib`
  - `email`
  - `smtplib`
  - `pandas`
  - `beautifulsoup4`

## Kurulum
1. **Depoyu Klonlayın**:
   ```bash
   git clone https://github.com/kullanici/technicalreportmail.git
   cd technicalreportmail

---
# Technical Analysis Report Filtering and Email Sending

This project reads daily technical analysis reports from Yahoo Mail, filters them based on the BIST Participation Index using a specified stock list, and sends the filtered report as an email in HTML format. It is developed in Python and runs automatically every day via GitHub Actions.

## Purpose
- Retrieve the daily technical analysis report from the "RAPOR" folder.
- Filter the report according to the stock list (`data/katilim.txt`) based on the BIST Participation Index.
- Send the filtered report as an HTML-formatted email.

## Features
- **Email Subject**: `Filtrelenmiş Hisse Raporu` (Filtered Stock Report)
- **Sender**: `KATILIM TEKNIK <email@yahoo.com>` (Replace this address with your Yahoo Mail address.)
- **Additional Info**: "Configured for the Yahoo Email infrastructure."

## Requirements
- Python 3.11
- Libraries:
  - `imaplib`
  - `email`
  - `smtplib`
  - `pandas`
  - `beautifulsoup4`

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/username/technicalreportmail.git
   cd technicalreportmail
