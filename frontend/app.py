from flask import Flask, request, render_template
import re
import urllib.parse
import urllib.request
import ipaddress
import socket

app = Flask(__name__)

def is_forbidden_ip(url):
    """
    Checks if the URL's scheme is HTTP/HTTPS AND if its hostname resolves 
    to a loopback or private address.
    """
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname

    # GOPHER BYPASS: Only check HTTP/HTTPS
    if parsed.scheme not in ['http', 'https']:
        return False
    
    if hostname:
        try:
            ip_obj = ipaddress.ip_address(hostname)
        except ValueError:
            if hostname in ['admin', 'ctf_admin', 'frontend', 'ctf_frontend', 'localhost']:
                return True
            return False

        if ip_obj.is_loopback or ip_obj.is_private:
            return True
    
    return False    

def fetch_gopher(url):
    """Custom gopher protocol handler"""
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    port = parsed.port or 70
    
    # Get the selector (everything after the first _ in gopher URL)
    path = parsed.path
    if path.startswith('/_'):
        selector = path[2:]  # Remove /_
    elif path.startswith('/'):
        selector = path[1:]
    else:
        selector = path
    
    # URL decode the selector - this converts %20 to space, %0D%0A to CRLF, etc.
    selector = urllib.parse.unquote(selector)
    
    # Create socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    
    # Send the selector (gopher doesn't add CRLF automatically, it's part of the payload)
    # The selector already contains the full HTTP request with CRLFs
    sock.sendall(selector.encode('latin-1'))
    
    # Receive response
    response = b''
    while True:
        data = sock.recv(4096)
        if not data:
            break
        response += data
    
    sock.close()
    return response.decode('utf-8', errors='replace')

@app.route('/', methods=['GET', 'POST'])
def index():
    fetched_content = None

    if request.method == 'POST':
        user_url = request.form.get('url')

        # 1. Block dangerous protocols
        blocked_protocols = ['data://', 'expect://', 'php://', 'jar://']
        if any(user_url.lower().startswith(proto) for proto in blocked_protocols):
            fetched_content = "Filter BLOCKED: Unauthorized protocols are forbidden.(try another)"
            return render_template('index.html', fetched_content=fetched_content)
        
        # 2. Basic regex filter
        if re.search(r'(localhost|0x7f|\[::1\]|0177|0\.0\.0\.0)', user_url, re.IGNORECASE):
            fetched_content = "Don't TRY TO BYPASS ME: Access to loopback addresses is forbidden."
            return render_template('index.html', fetched_content=fetched_content)
        
        # 3. Block HTTP/HTTPS to internal resources
        if is_forbidden_ip(user_url):
            fetched_content = "Don't TRY TO BYPASS MEEE"
            return render_template('index.html', fetched_content=fetched_content)

        try:
            parsed = urllib.parse.urlparse(user_url)
            
            if parsed.scheme == 'gopher':
                # Use custom gopher handler
                response_text = fetch_gopher(user_url)
                fetched_content = f"<h3>Gopher Response:</h3><pre>{response_text}</pre>"
            else:
                # Use urllib for other protocols
                with urllib.request.urlopen(user_url, timeout=5) as response:
                    body = response.read()
                    try:
                        response_text = body.decode('utf-8')
                    except:
                        response_text = body.decode('latin-1')
                    fetched_content = f"<h3>Response Status: {response.status}</h3><pre>{response_text}</pre>"

        except Exception as e:
            fetched_content = f"Fetch Error: Could not connect to the specified URL. ({str(e)})"

    return render_template('index.html', fetched_content=fetched_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


## 🎯 Correct Payload Format:

