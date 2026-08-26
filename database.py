import sqlite3
import os
import json
import uuid
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'karigar_setu.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create Artisans Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artisans (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        preferred_language TEXT DEFAULT 'hi',
        region TEXT,
        craft_cluster TEXT,
        gst_or_udyam_id TEXT,
        bank_account_masked TEXT,
        kyc_status TEXT DEFAULT 'pending_payout',
        monthly_earnings REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        artisan_id TEXT NOT NULL,
        title TEXT,
        story TEXT,
        category TEXT,
        materials TEXT, -- JSON Array
        region TEXT,
        tags TEXT, -- JSON Array
        suggested_price REAL,
        min_price REAL,
        max_price REAL,
        pricing_reasoning TEXT,
        final_price REAL,
        photo_url TEXT,
        voice_note_url TEXT,
        status TEXT DEFAULT 'live',
        certificate_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(artisan_id) REFERENCES artisans(id)
    )
    ''')

    # Create Certificates Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS certificates (
        id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        artisan_id TEXT NOT NULL,
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hash_signature TEXT NOT NULL,
        qr_payload TEXT NOT NULL,
        verification_url TEXT NOT NULL
    )
    ''')

    # Create Channels Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        logo_icon TEXT,
        fee_type TEXT,
        fee_value REAL,
        description TEXT,
        status TEXT DEFAULT 'active'
    )
    ''')

    # Create Listing Sync Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS listing_channel_sync (
        id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        sync_status TEXT DEFAULT 'synced',
        external_listing_url TEXT,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(channel_id) REFERENCES channels(id)
    )
    ''')

    # Create Craft Benchmarks Table (for Fair Pricing Engine)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS craft_benchmarks (
        craft_type TEXT PRIMARY KEY,
        primary_material TEXT,
        avg_material_cost REAL,
        labor_rate_per_hr REAL,
        avg_crafting_hours REAL
    )
    ''')

    conn.commit()
    seed_initial_data(conn)
    conn.close()
    print("Database initialized successfully.")

def seed_initial_data(conn):
    cursor = conn.cursor()

    # Check if channels already seeded
    cursor.execute("SELECT COUNT(*) FROM channels")
    if cursor.fetchone()[0] == 0:
        channels_data = [
            ('native', 'Karigar Setu Storefront', 'storefront', 'flat', 2.5, 'Direct transparent 2.5% platform maintenance fee. Zero listing charges.', 'connected'),
            ('india_handmade', 'India Handmade (Govt)', 'account_balance', 'zero', 0.0, 'Ministry of Textiles official portal. 0% commission, GST Enrolment ID enabled.', 'connected'),
            ('etsy', 'Etsy Global Market', 'public', 'stacked', 6.5, '$0.20 listing fee + 6.5% transaction fee + payment processing charges.', 'connected'),
            ('kreate', 'Kreate Crafts', 'shopping_bag', 'subscription', 20.0, '20% commission + mandatory seller tier subscription.', 'not_connected'),
            ('unfade', 'Unfade Artisans', 'palette', 'flat', 0.0, '0% commission, local Jaipur craft hub.', 'connected')
        ]
        cursor.executemany('''
            INSERT INTO channels (id, name, logo_icon, fee_type, fee_value, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', channels_data)

    # Check craft benchmarks
    cursor.execute("SELECT COUNT(*) FROM craft_benchmarks")
    if cursor.fetchone()[0] == 0:
        crafts_data = [
            ('Terracotta Pottery', 'Natural Red Clay', 150.0, 120.0, 4.5),
            ('Chikankari Embroidery', 'Fine Pure Cotton Cloth & Thread', 450.0, 150.0, 12.0),
            ('Dokra Metal Craft', 'Bell Metal & Beeswax', 600.0, 160.0, 8.0),
            ('Madhubani Painting', 'Handmade Paper & Natural Pigments', 200.0, 140.0, 6.0),
            ('Blue Pottery', 'Quartz Stone Powder & Multani Mitti', 300.0, 130.0, 5.0),
            ('Wood Carving', 'Sheesham Wood', 500.0, 150.0, 9.0),
            ('Tanjore Painting', 'Teak Wood, 22k Gold Foil & Gems', 1800.0, 200.0, 18.0),
            ('Brassware Craft', 'Solid Cast Brass', 700.0, 150.0, 7.5)
        ]
        cursor.executemany('''
            INSERT INTO craft_benchmarks (craft_type, primary_material, avg_material_cost, labor_rate_per_hr, avg_crafting_hours)
            VALUES (?, ?, ?, ?, ?)
        ''', crafts_data)

    # Ensure sample artisan, product, and certificate exist
    sample_artisan_id = "artisan_ramesh_01"
    prod_id = "prod_terracotta_horse_01"
    cert_id = "CERT-KS-2026-883921"
    
    cursor.execute("SELECT COUNT(*) FROM artisans WHERE id = ?", (sample_artisan_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO artisans (id, name, phone, preferred_language, region, craft_cluster, gst_or_udyam_id, bank_account_masked, kyc_status, monthly_earnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sample_artisan_id,
            'Ramesh Prajapati',
            '+91 98765 43210',
            'hi',
            'Bankura, West Bengal',
            'Terracotta Crafts Cluster',
            'UDYAM-WB-03-0019284',
            'XXXX-XXXX-4821',
            'verified',
            42500.0
        ))

    cursor.execute("SELECT COUNT(*) FROM products WHERE id = ?", (prod_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO products (
                id, artisan_id, title, story, category, materials, region, tags,
                suggested_price, min_price, max_price, pricing_reasoning, final_price,
                photo_url, voice_note_url, status, certificate_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prod_id,
            sample_artisan_id,
            'Handcrafted Bankura Terracotta Horse (Traditional GI Motif)',
            'Handmade by Master Craftsman Ramesh Prajapati using traditional clay molding passed down 4 generations in Bankura. Fired in eco-friendly wood kiln.',
            'Terracotta Pottery',
            json.dumps(['Natural Red Clay', 'Eco Kiln Fired Clay', 'Natural Organic Pigment']),
            'Bankura, West Bengal',
            json.dumps(['Handmade', 'Terracotta', 'GI Craft', 'Bankura Horse', 'Eco Friendly', 'Artisan Certified']),
            1850.0,
            1600.0,
            2100.0,
            'Raw Clay & Fuel: ₹250 | Labor (8 hrs @ ₹140/hr): ₹1,120 | Complexity & Artisan Margin: ₹480 | Suggested Retail: ₹1,850',
            1850.0,
            '/static/images/terracotta_horse.jpg',
            '/static/audio/sample_voice.mp3',
            'live',
            cert_id
        ))

    cursor.execute("SELECT COUNT(*) FROM certificates WHERE id = ?", (cert_id,))
    if cursor.fetchone()[0] == 0:
        hash_sig = "a8f9c7e4120b6689d14eef931049581a96572e819b2512f4581c3d6a908f22e1"
        cursor.execute('''
            INSERT INTO certificates (id, product_id, artisan_id, hash_signature, qr_payload, verification_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            cert_id,
            prod_id,
            sample_artisan_id,
            hash_sig,
            f"https://karigarsetu.gov.in/verify/{cert_id}",
            f"/certificate/{cert_id}"
        ))

        # Sync records
        for ch_id in ['native', 'india_handmade', 'etsy', 'unfade']:
            cursor.execute('''
                INSERT INTO listing_channel_sync (id, product_id, channel_id, sync_status, external_listing_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), prod_id, ch_id, 'synced', f"https://{ch_id}.example.com/item/{prod_id}"))

    conn.commit()

if __name__ == '__main__':
    init_db()
