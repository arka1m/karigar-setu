import hashlib
import hmac
import time
import base64
import io
import qrcode
from datetime import datetime, timezone

SECRET_KEY = b"karigar_setu_sih_2026_authentic_provenance_secret_key"

def generate_certificate_hash(artisan_id, product_id, timestamp=None):
    """
    Generates a cryptographic SHA-256 HMAC hash signature for artisan provenance.
    Ensures tamper-evident authentication.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
        
    payload = f"ARTISAN:{artisan_id}|PRODUCT:{product_id}|TIMESTAMP:{timestamp}|GOVT_CLUSTER:INDIA_HANDMADE"
    signature = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return {
        'hash': signature,
        'timestamp': timestamp,
        'payload': payload
    }

def generate_qr_code_base64(verification_url):
    """
    Generates a high-contrast QR code image encoded as Base64 string for direct inline rendering.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#4A2318", back_color="#FBF9F3")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return f"data:image/png;base64,{img_str}"

def issue_authenticity_certificate(artisan_id, product_id, base_url="http://localhost:5000"):
    """
    Issues a complete QR-verifiable certificate.
    """
    clean_base_url = base_url.rstrip('/')
    cert_id = f"CERT-KS-2026-{hashlib.md5(f'{artisan_id}{product_id}{time.time()}'.encode()).hexdigest()[:6].upper()}"
    hash_info = generate_certificate_hash(artisan_id, product_id)
    
    verification_url = f"{clean_base_url}/certificate/{cert_id}"
    qr_b64 = generate_qr_code_base64(verification_url)
    
    return {
        'certificate_id': cert_id,
        'artisan_id': artisan_id,
        'product_id': product_id,
        'issued_at': hash_info['timestamp'],
        'hash_signature': hash_info['hash'],
        'verification_url': verification_url,
        'qr_base64': qr_b64
    }

if __name__ == '__main__':
    cert = issue_authenticity_certificate("artisan_ramesh_01", "prod_001")
    print("Certificate Issued:", cert['certificate_id'])
    print("Verification URL:", cert['verification_url'])
    print("Hash:", cert['hash_signature'])
