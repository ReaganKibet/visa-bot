# 🎯 VFS Visa Appointment Bot  
**Monitor. Alert. Book. Automate.**  

A smart, human-in-the-loop automation system for securing visa appointment slots on [VFS Global](https://visa.vfsglobal.com/) — where slots disappear in seconds.

---

## 🔖 Tags  
`#visa-bot` `#playwright` `#fastapi` `#celery` `#docker` `#automation` `#web-scraping` `#appointment-monitor` `#react` `#postgresql` `#human-in-the-loop`

---

## 📌 Overview

The **VFS Visa Appointment Bot** is a full-stack automation tool that:
- 🕵️‍♂️ **Monitors** the VFS Global website 24/7 for newly released appointment slots
- 📢 **Alerts** you instantly when a slot is found
- 🖥️ **Launches a real browser** so you can complete CAPTCHA, facial verification, and document upload
- ✍️ **Auto-fills** applicant data after verification
- 📎 **Captures and emails** the confirmation PDF

✅ **No bypassing security**  
✅ **You stay in control** at every critical step  
✅ **Ethical, reliable, and effective**

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| ✅ **Real-Time Monitoring** | Checks the VFS site every 60 seconds using Playwright |
| 📊 **Live Dashboard** | React-based UI with real-time logs via WebSocket |
| 🔔 **Instant Alerts** | Logs show: `🔍 Checking...`, `⚠️ CAPTCHA detected`, `🎉 SLOT AVAILABLE!` |
| 🖱️ **One-Click Booking** | Click "Start Booking" → opens real Chrome browser |
| 🤖 **Auto-Fill Form** | After verification, fills: First Name, Surname, DOB, Passport |
| 🧑‍💼 **You Complete Security** | You do CAPTCHA, liveness, uploads — bot waits |
| 📧 **PDF Capture & Email** | Downloads confirmation and emails it via Gmail API |
| 🐳 **Dockerized** | Full stack runs in Docker (FastAPI, Celery, React, PostgreSQL, Redis) |

---

## 🧩 Tech Stack

| Layer | Technology |
|------|-----------|
| **Frontend** | React.js + Tailwind CSS |
| **Backend** | FastAPI (Python 3.11) |
| **Automation** | Playwright (Chromium) |
| **Task Queue** | Celery + Redis |
| **Database** | PostgreSQL |
| **Containerization** | Docker + Docker Compose |

---


---


MIT License

Copyright (c) 2025 Reagan Langat


