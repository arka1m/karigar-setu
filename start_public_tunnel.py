import time
from pycloudflared import try_cloudflare

print("Starting Cloudflare Public Tunnel for port 5000...", flush=True)
try:
    urls = try_cloudflare(port=5000)
    url_str = str(urls.tunnel)
    print(f"PUBLIC_URL: {url_str}", flush=True)
    with open("tunnel_url.txt", "w") as f:
        f.write(url_str)
except Exception as e:
    print(f"Error starting tunnel: {e}", flush=True)

while True:
    time.sleep(10)
