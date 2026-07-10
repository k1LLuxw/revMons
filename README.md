💀 revMons – Advanced Reverse Shell & Persistence Generator

**revMons** is a modular, offensive security tool designed for red team operations and authorized penetration testing.

> **⚠️ YASAL UYARI / LEGAL WARNING**
> Bu araç **sadece** kendi sistemleriniz, yetkili penetrasyon testleri, eğitim ve CTF ortamları için geliştirilmiştir. İzinsiz kullanım suçtur.
> This tool is **only** for your own systems, authorized penetration tests, educational labs and CTF competitions. Unauthorized use is illegal.

---

<img width="1698" height="710" alt="image" src="https://github.com/user-attachments/assets/f6510f45-8215-4934-9025-bdd2a708819d" />


## 🔥 Features / Özellikler

- **25+ payloads / dil desteği:** Bash, SH, Netcat, Python3, PHP, Ruby, Perl, PowerShell, AWK, Lua, Go, Rust…
- **Staged & Stageless:** Tek komut veya indirme beşiği ile çalıştırma
- **Encryption / Şifreleme:** XOR ve AES‑256‑CBC, otomatik çözücü üretimi
- **Obfuscation / Gizleme:** Base64 sarmalama, SSL/TLS tünel
- **Persistence / Kalıcılık:** Linux (cron, systemd), Windows (Registry, Scheduled Task)
- **Alternatif protokoller:** SMB, RDP, DNS tünel (iodine), SOCKS proxy, LOLBAS (mshta, regsvr32, msiexec)
- **SSL/TLS listener:** Python tabanlı şifreli dinleyici
- **Docker test lab:** Konteyner içinde anında payload doğrulama
- **Türkçe ve İngilizce yardım mesajları**

---

## 📦 Installation / Kurulum

```bash
git clone https://github.com/k1LLuxw/revMons.git
cd revMons
python3 revMons.py
