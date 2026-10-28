<div align="center">

# 🏛️ Centralized Hybrid Complaint Management System

**An enterprise-grade, secure, and distributed complaint management architecture built for scale.**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](#)
[![Security](https://img.shields.io/badge/Security-TLS_1.3_%7C_AES--256-green?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Hackathon_Ready-FF6F00?style=for-the-badge)](#)

<br>

*Insert your architecture workflow image here by dragging and dropping it into the GitHub editor!*
<!-- ![Architecture Workflow](link-to-your-image.png) -->

</div>

---

## 🌟 The Specialty: Why This System Stands Out

Most complaint portals are simple web applications. This project is different. It is built as a **Distributed Cyber-Physical Architecture** simulating real-world government and enterprise networks. 

Instead of routing everything to a single admin, this system mimics a massive organization by deploying a **Central Hybrid Server** that communicates with distributed, independent department nodes (PGRC, RB, Regional). It features live network monitoring, secure tunneling, and load balancing, making it a highly resilient, enterprise-ready solution.

---

## 🔥 Core Features

*   **🧠 Intelligent Dynamic Routing:** The Central Server acts as a traffic controller. When a user submits a complaint, the server instantly categorizes it (e.g., *Fees/Harassment* $\rightarrow$ PGRC, *Affiliation* $\rightarrow$ RB, *Infrastructure* $\rightarrow$ Regional) and forwards it to the correct department node.
*   **🤝 Multi-Department Collaboration:** Complex complaints often require multiple departments. Our system allows seamless collaborative workflow across nodes **without any repetition of action**, ensuring efficient resolution.
*   **📡 Live Master Node Monitoring:** A dedicated System Master Node uses SNMP protocols to actively monitor all intermediate servers and computers. It tracks live IP addresses, detects active/inactive nodes, and grants super-admin override/deletion capabilities.
*   **🛡️ Military-Grade Security:** 
    *   **In Transit:** All data passes through secure HTTPS/TLS 1.3 encrypted tunnels via Ngrok.
    *   **At Rest:** Sensitive PII (like Aadhaar and Govt IDs) is masked and hashed using AES-256.
    *   **Authentication:** Multi-step OTP (SMS/Aadhaar) ensures only verified users can generate complaints.

---

## 🔄 How It Works (The Lifecycle)

The system operates on a strict, automated, and secure 3-phase workflow:

### Phase 1: Client Node (Registration & Submission)
1.  **Identity Verification:** Users create accounts by providing names, emails, and uploading Government IDs.
2.  **Multi-Step Auth:** The system triggers an OTP validation step to authenticate the identity securely.
3.  **Complaint Generation:** The user selects a category (fees, harassment, faculty, etc.) and submits the issue.

### Phase 2: Transit & Central Processing
1.  **Secure Pipeline:** The complaint travels through intermediate servers and load balancers via TCP/IP and HTTPS protocols.
2.  **The Heart of the System:** The `FastAPI & Uvicorn` Central Hybrid Server receives the data, logs it into the `SQLite` database, and applies the dynamic routing rules.

### Phase 3: Collaborative Resolution
The complaint appears on the targeted Department Admin's Web Portal. It goes through a strict **3-Stage Status Protocol**:
> 🟡 **Status 1: Submitted Complaint** *(Actions Pending)* <br>
> 🔵 **Status 2: Actions Taken** *(In-Progress / Partial Actions)* <br>
> 🟢 **Status 3: Complaint Resolved** *(All necessary actions taken by all involved departments)*

---

## 💻 Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend & UI** | HTML5, CSS3, Vanilla JS, Tailwind CSS |
| **Core Backend** | FastAPI, Uvicorn (ASGI), Python 3 |
| **Database** | SQLite (Relational Storage) |
| **Network & Tunneling** | Ngrok (Public Port Forwarding), TCP/IP, HTTP/1.1 |
| **Security Auth** | OAuth 2.0 / Token-Based Sessions, TLS 1.3, AES-256 |

---

## 📂 Architecture Map

<details>
<summary><b>Click to expand the project directory structure</b></summary>
<br>

```text
mini-aicte/
│
├── server.py              # The Heart: FastAPI Central Hybrid Server
├── client.py              # End-User CLI for Registration & Complaints
├── node_master.py         # System Master Node (SNMP Live Monitoring)
├── node_pgrc.py           # Department Node: PGRC
├── node_rb.py             # Department Node: RB
├── node_regional.py       # Department Node: Regional
├── admin.html             # Web-based Collaborative Dashboard
├── How to create...docx   # Detailed System Documentation
└── .gitignore             # Secures DB and Session tokens from Git
