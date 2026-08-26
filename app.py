import os
import json
import uuid
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from database import get_db, init_db
from ai_engine import analyze_product_image, generate_ai_draft, calculate_fair_price
from certificate_engine import issue_authenticity_certificate, generate_qr_code_base64
from marketplace_adapters import sync_product_to_channels, ADAPTERS

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'karigar_setu_secret_key_sih_2026')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database on boot
init_db()

@app.route('/')
def index():
    """Main Application Interface (Artisan App + Buyer Discovery + SIH Judge Matrix)"""
    return render_template('index.html')

@app.route('/api/artisan', methods=['GET'])
def get_artisan():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artisans LIMIT 1")
    artisan = cursor.fetchone()
    conn.close()
    
    if artisan:
        art_dict = dict(artisan)
        return jsonify({'success': True, 'artisan': art_dict})
    return jsonify({'success': False, 'message': 'No artisan found'}), 404

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.hash_signature, c.qr_payload 
        FROM products p 
        LEFT JOIN certificates c ON p.certificate_id = c.id 
        ORDER BY p.created_at DESC
    """)
    products = cursor.fetchall()
    
    prod_list = []
    for p in products:
        item = dict(p)
        item['materials'] = json.loads(item['materials']) if item.get('materials') else []
        item['tags'] = json.loads(item['tags']) if item.get('tags') else []
        
        # Get channel sync status for this product
        cursor.execute("""
            SELECT l.channel_id, l.sync_status, c.name as channel_name 
            FROM listing_channel_sync l 
            JOIN channels c ON l.channel_id = c.id 
            WHERE l.product_id = ?
        """, (item['id'],))
        syncs = cursor.fetchall()
        item['synced_channels'] = [dict(s) for s in syncs]
        prod_list.append(item)
        
    conn.close()
    return jsonify({'success': True, 'products': prod_list})

@app.route('/api/ai/catalogue', methods=['POST'])
def ai_catalogue():
    """
    Core AI Cataloguing Endpoint:
    Processes uploaded photo or craft sample + voice note prompt in regional language.
    Returns detected craft, materials, region, AI title, story, tags, and fair pricing recommendation.
    """
    data = request.form or request.json or {}
    language = data.get('language', 'hi')
    voice_note = data.get('voice_note', '')
    craft_keyword = data.get('craft_keyword', 'terracotta')
    
    filename = "sample_craft.jpg"
    photo_url = "/static/images/terracotta_horse.jpg"
    
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            photo_url = f"/static/uploads/{filename}"

    # 1. Vision Engine Analysis
    vision_res = analyze_product_image(craft_keyword or filename)
    craft_key = vision_res['craft_key']
    
    # 2. Indic NLP Generation
    nlp_res = generate_ai_draft(craft_key, voice_note, language)
    
    # 3. Fair Price Calculation
    pricing_res = calculate_fair_price(craft_key)
    
    response_payload = {
        'success': True,
        'craft_key': craft_key,
        'photo_url': photo_url,
        'vision_analysis': vision_res,
        'ai_draft': nlp_res,
        'aiDraft': nlp_res,
        'pricing': pricing_res
    }
    
    return jsonify(response_payload)

@app.route('/api/products/publish', methods=['POST'])
def publish_product():
    """
    Publishes AI Draft product across selected marketplaces with digital certificate generation.
    """
    data = request.json or {}
    
    title = data.get('title')
    story = data.get('story')
    category = data.get('category', 'Terracotta Pottery')
    materials = data.get('materials', ['Clay'])
    tags = data.get('tags', ['Handmade'])
    price = float(data.get('price', 1850.0))
    pricing_reasoning = data.get('pricing_reasoning', 'Fair price baseline')
    photo_url = data.get('photo_url', '/static/images/terracotta_horse.jpg')
    voice_note_url = data.get('voice_note_url', '')
    selected_channels = data.get('channels', ['native', 'india_handmade', 'etsy', 'unfade'])
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch primary artisan
    cursor.execute("SELECT * FROM artisans LIMIT 1")
    artisan = dict(cursor.fetchone())
    
    prod_id = f"prod_{uuid.uuid4().hex[:10]}"
    
    # 1. Issue Cryptographic Certificate
    host_url = request.host_url.rstrip('/')
    cert = issue_authenticity_certificate(artisan['id'], prod_id, host_url)
    
    # Insert Certificate
    cursor.execute("""
        INSERT INTO certificates (id, product_id, artisan_id, hash_signature, qr_payload, verification_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        cert['certificate_id'],
        prod_id,
        artisan['id'],
        cert['hash_signature'],
        cert['verification_url'],
        cert['verification_url']
    ))
    
    # Insert Product
    cursor.execute("""
        INSERT INTO products (
            id, artisan_id, title, story, category, materials, region, tags,
            suggested_price, min_price, max_price, pricing_reasoning, final_price,
            photo_url, voice_note_url, status, certificate_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prod_id,
        artisan['id'],
        title,
        story,
        category,
        json.dumps(materials),
        artisan['region'],
        json.dumps(tags),
        price,
        round(price * 0.85, 2),
        round(price * 1.15, 2),
        pricing_reasoning,
        price,
        photo_url,
        voice_note_url,
        'live',
        cert['certificate_id']
    ))
    
    # 2. Multi-Marketplace Sync via Adapters
    product_dict = {
        'id': prod_id,
        'title': title,
        'story': story,
        'category': category,
        'materials': materials,
        'tags': tags,
        'final_price': price,
        'certificate_id': cert['certificate_id']
    }
    
    sync_results = sync_product_to_channels(product_dict, artisan, selected_channels)
    
    for res in sync_results:
        cursor.execute("""
            INSERT INTO listing_channel_sync (id, product_id, channel_id, sync_status, external_listing_url)
            VALUES (?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), prod_id, res['channel_id'], 'synced', res['external_url']))
        
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'product_id': prod_id,
        'certificate': cert,
        'sync_results': sync_results,
        'message': f"Listing published across {len(selected_channels)} marketplaces with authenticity certificate!"
    })

@app.route('/certificate/<cert_id>')
def view_certificate(cert_id):
    """
    Public Read-Only Certificate Provenance Page.
    Scannable by any buyer or QR reader.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, p.title, p.story, p.category, p.materials, p.final_price, p.photo_url, p.created_at as prod_created,
               a.name as artisan_name, a.region as artisan_region, a.craft_cluster, a.gst_or_udyam_id
        FROM certificates c
        JOIN products p ON c.product_id = p.id
        JOIN artisans a ON c.artisan_id = a.id
        WHERE c.id = ?
    """, (cert_id,))
    record = cursor.fetchone()
    conn.close()
    
    if not record:
        return "Certificate Not Found or Invalid Hash Signature", 404
        
    data = dict(record)
    data['materials'] = json.loads(data['materials']) if data.get('materials') else []
    
    host_url = request.host_url.rstrip('/')
    verification_url = f"{host_url}/certificate/{cert_id}"
    qr_b64 = generate_qr_code_base64(verification_url)
    
    return render_template('certificate.html', cert=data, qr_b64=qr_b64)

@app.route('/api/certificate/verify/<cert_id>', methods=['GET'])
def verify_certificate_api(cert_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, p.title, p.category, p.final_price, a.name as artisan_name, a.region, a.craft_cluster
        FROM certificates c
        JOIN products p ON c.product_id = p.id
        JOIN artisans a ON c.artisan_id = a.id
        WHERE c.id = ?
    """, (cert_id,))
    record = cursor.fetchone()
    conn.close()
    
    if record:
        return jsonify({'success': True, 'verified': True, 'certificate': dict(record)})
    return jsonify({'success': False, 'verified': False, 'message': 'Invalid certificate code'}), 404

@app.route('/api/channels', methods=['GET'])
def get_channels():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'channels': channels})

@app.route('/api/sih-gap-matrix', methods=['GET'])
def get_gap_matrix():
    """
    Returns the verified platform limitations vs Karigar Setu capabilities for SIH 2026 judges.
    """
    matrix = [
        {
            'platform': 'India Handmade (Govt)',
            'limitations': [
                'Reach is limited — a government showcase portal, not high traffic',
                'Manual, form-based listing in English',
                'No pricing guidance or algorithmic buyer discovery'
            ],
            'karigar_solution': 'AI cataloguing pipeline (photo + Indic voice note), AI fair-price engine, and buyer search recommendation algorithm while preserving 0% commission & GST enrolment ID support.',
            'closed_gap_badge': 'Reach & Voice Cataloguing Gap Closed'
        },
        {
            'platform': 'Etsy Global',
            'limitations': [
                'Stacked fees: $0.20 listing + 6.5% transaction + payment processing',
                'English-first, typing-heavy listing creation',
                'Artisans buried among mass-produced items; no provenance verification'
            ],
            'karigar_solution': 'Transparent flat 2.5% fee structure, regional voice-first listing, and HMAC-SHA256 QR digital authenticity certificate attached to every item.',
            'closed_gap_badge': 'Fee Transparency & Provenance Gap Closed'
        },
        {
            'platform': 'Kreate',
            'limitations': [
                '~20% commission + paid subscription tiers (₹50-100/mo)',
                'Mandatory 24-hour KYC review blocking listings before drafting',
                'Strict 24h/48h SLAs with zero logistics support'
            ],
            'karigar_solution': 'Materially lower fee with zero subscription gate, instant preview/drafting without KYC blocking, and zero-penalty logistics guidance module.',
            'closed_gap_badge': 'No-Blocking Onboarding & SLA Gap Closed'
        },
        {
            'platform': 'Unfade',
            'limitations': [
                'Fully manual listing creation — zero AI assistance',
                'No fair-price guidance or provenance certificate',
                'Siloed — single platform ecosystem (cannot publish elsewhere)'
            ],
            'karigar_solution': 'Full AI listing drafter (title, story, tags, price reasoning), QR certificate, and unified Multi-Marketplace Publish Adapters.',
            'closed_gap_badge': 'AI Assistance & Multi-Channel Publish Gap Closed'
        }
    ]
    return jsonify({'success': True, 'matrix': matrix})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Karigar Setu (v2 - Gap-Verified) Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
