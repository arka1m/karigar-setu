import random
import json

# Craft Catalog Rules & Pre-trained Heuristics
CRAFT_DATABASE = {
    'terracotta': {
        'category': 'Terracotta Pottery',
        'materials': ['Natural Red Clay', 'Eco Kiln Fired Clay', 'Natural Organic Pigment'],
        'region': 'Bankura, West Bengal',
        'default_hours': 7.5,
        'material_cost': 220.0,
        'hourly_rate': 140.0,
        'tags': ['Handmade', 'Terracotta', 'GI Craft', 'Bankura Horse', 'Eco Friendly', 'Artisan Certified'],
        'title_templates': {
            'hi': 'हस्तनिर्मित बांकुरा टेराकोटा क्राफ्ट ({style})',
            'en': 'Handcrafted Bankura Terracotta ({style})',
            'ta': 'கலப்பில்லாத கைவினை டெர்ராகோட்டா ({style})',
            'bn': 'হস্তনির্মিত বাকুড়া টেরাকোটা ({style})'
        },
        'story_templates': {
            'hi': 'बांकुरा की पीढ़ियों पुरानी मिट्टी कला शैली में प्राकृतिक लाल मिट्टी से निर्मित। पारंपरिक भट्टी में पकाकर तैयार किया गया एक अनुपम पारंपरिक उत्पाद।',
            'en': 'Handmade using heritage red clay crafting techniques passed down through generations in Bankura. Wood-kiln fired with zero chemical synthetic glazes.',
            'ta': 'தலைமுறை தலைமுறையாக பேணப்படும் பாரம்பரிய கைவினை நுட்பத்தில் இயற்கை சிவப்பு களிமண்ணால் செய்யப்பட்டது.',
            'bn': 'বাঁকুড়ার ঐতিহ্যবাহী লাল মাটি দিয়ে তৈরি এবং কাঠের ভাঁটিতে পোড়ানো খাঁটি হস্তশিল্প।'
        }
    },
    'chikankari': {
        'category': 'Chikankari Embroidery',
        'materials': ['Pure Mulberry Cotton', 'Resham Silk Thread', 'Hand Needlework'],
        'region': 'Lucknow, Uttar Pradesh',
        'default_hours': 14.0,
        'material_cost': 550.0,
        'hourly_rate': 150.0,
        'tags': ['Chikankari', 'Hand Embroidered', 'Lucknow Heritage', 'GI Tagged', 'Pure Cotton'],
        'title_templates': {
            'hi': 'लखनवी हस्तनिर्मित चिकनकारी कुरता / वस्त्र ({style})',
            'en': 'Authentic Lucknowi Hand-Embroidered Chikankari ({style})',
            'ta': 'பாரம்பரிய லக்னோ சிகன்காரி கைத்தறி ({style})',
            'bn': 'ঐতিহ্যবাহী লখনউই চিকনকারী হস্তশিল্প ({style})'
        },
        'story_templates': {
            'hi': 'लखनऊ के मास्टर कारीगरों द्वारा बारीकी से सुई-धागे से की गई शैडो-वर्क चिकनकारी कढ़ाई। 100% शुद्ध कॉटन कपड़ा।',
            'en': 'Intricately hand-embroidered by Lucknow master artisans using shadow-work and bakhiya stitching on breathable pure muslin cotton.',
            'ta': 'லக்னோ கைவினைஞர்களால் பிரத்யேகமாக தையல் செய்யப்பட்ட தூய பருத்தி ஆடை.',
            'bn': 'লখনউয়ের কারিগরদের সূক্ষ্ম হাতের কাজ এবং খাঁটি সুতির কাপড়ে তৈরি।'
        }
    },
    'dokra': {
        'category': 'Dokra Metal Craft',
        'materials': ['Bell Metal Alloy', 'Natural Beeswax Core', 'Clay Mold'],
        'region': 'Bastar, Chhattisgarh',
        'default_hours': 10.0,
        'material_cost': 650.0,
        'hourly_rate': 160.0,
        'tags': ['Dokra Metal', 'Lost Wax Casting', 'Tribal Art', 'Bastar Craft', 'Brass Bell Metal'],
        'title_templates': {
            'hi': 'हस्तनिर्मित बस्तर ढोकरा मेटल मूर्ति / सजावट ({style})',
            'en': 'Handcrafted Bastar Dokra Lost-Wax Metal Art ({style})',
            'ta': 'பாரம்பரிய தோக்ரா உலோக சிற்பம் ({style})',
            'bn': 'হস্তনির্মিত ডোকরা ধাতু শিল্প ({style})'
        },
        'story_templates': {
            'hi': '4000 साल पुरानी प्राचीन "लॉस्ट-वैक्स" (मोम मोल्डिंग) तकनीक से बनाई गई प्रामाणिक पीतल-कांसा जनजाति कला।',
            'en': 'Crafted using the 4,000-year-old non-ferrous lost-wax casting technique by tribal artisans of Chhattisgarh. Every piece is a unique non-replicable mastercraft.',
            'ta': '4000 ஆண்டுகள் பழமையான மெழுகு வார்ப்பு முறையில் தயாரிக்கப்பட்ட பழங்குடியினர் உலோக கலைப்பொருள்.',
            'bn': 'প্রাচীন ডোকরা লস্ট-ওয়াক্স পদ্ধতিতে হাতে তৈরি অনন্য ধাতব শিল্পকলা।'
        }
    },
    'madhubani': {
        'category': 'Madhubani Painting',
        'materials': ['Handmade Recycled Cotton Paper', 'Natural Plant Extracts & Pigments', 'Bamboo Pen'],
        'region': 'Mithila, Bihar',
        'default_hours': 8.0,
        'material_cost': 250.0,
        'hourly_rate': 140.0,
        'tags': ['Madhubani', 'Mithila Folk Painting', 'Natural Pigments', 'GI Tagged', 'Wall Art'],
        'title_templates': {
            'hi': 'प्राकृतिक रंगों से बनी पारंपरिक मधुबनी लोक चित्रकला ({style})',
            'en': 'Original Mithila Madhubani Folk Painting ({style})',
            'ta': 'இயற்கை சாயங்கள் கொண்ட மதுபானி ஓவியம் ({style})',
            'bn': 'হাতে আঁকা ঐতিহ্যবাহী মধুবনী চিত্রশিল্প ({style})'
        },
        'story_templates': {
            'hi': 'मिथिला की महिला कारीगरों द्वारा बांस की तीलियों और प्राकृतिक वनस्पति रंगों से हाथ से बनाई गई पारंपरिक लोक कला चित्रकारी।',
            'en': 'Hand-drawn by Mithila women artisans using twigs, nibs, and natural dyes derived from leaves, turmeric, and flowers on handmade paper.',
            'ta': 'இயற்கை சாயங்கள் மற்றும் மூங்கில் குச்சிகளைப் பயன்படுத்தி கைகளால் வரையப்பட்ட ஓவியம்.',
            'bn': 'প্রাকৃতিক রঙের সাহায্যে হাতে আঁকা ঐতিহ্যবাহী মিথিলা মধুবনী শিল্প।'
        }
    },
    'blue_pottery': {
        'category': 'Blue Pottery',
        'materials': ['Quartz Stone Powder', 'Multani Mitti', 'Natural Oxide Colors'],
        'region': 'Jaipur, Rajasthan',
        'default_hours': 6.0,
        'material_cost': 320.0,
        'hourly_rate': 130.0,
        'tags': ['Blue Pottery', 'Jaipur Craft', 'Quartz Ceramic', 'Hand Painted', 'Glazed Home Decor'],
        'title_templates': {
            'hi': 'जयपुर प्रसिद्ध हस्तनिर्मित ब्लू पॉटरी डिश / शोपीस ({style})',
            'en': 'Authentic Jaipur Hand-Painted Blue Pottery ({style})',
            'ta': 'ஜெய்ப்பூர் ப்ளூ பாட்டரி கைவினை ({style})',
            'bn': 'জয়পুর ব্লু পটরি হস্তশিল্প ({style})'
        },
        'story_templates': {
            'hi': 'जयपुर की ऐतिहासिक ब्लू पॉटरी बिना मिट्टी के केवल क्वार्ट्ज पत्थर पाउडर और मुल्तानी मिट्टी से बनाई गई है। हाथ से चित्रित।',
            'en': 'Traditional Jaipur Blue Pottery made without clay using ground quartz stone and natural cobalt oxide glazes. Low-temperature kiln fired.',
            'ta': 'களிமண் இன்றி குவார்ட்ஸ் பாறைக் பொடியால் செய்யப்பட்ட ஜெய்ப்பூர் நீல பானைக்கலை.',
            'bn': 'জয়পুরের ঐতিহ্যবাহী ব্লু পটরি কোয়ার্টজ ও প্রাকৃতিক রঙ্গে হাতে তৈরি।'
        }
    }
}

def analyze_product_image(image_bytes_or_name):
    """
    Simulates on-device / Python vision model pipeline (TensorFlow Lite / OpenCV).
    Detects craft category, material components, regional origin, and confidence score.
    """
    # Deterministic mapping based on filename keyword or random high confidence pick
    name_lower = str(image_bytes_or_name).lower()
    
    selected_key = 'terracotta'
    for key in CRAFT_DATABASE.keys():
        if key in name_lower:
            selected_key = key
            break
    else:
        # Pick based on hash if unknown name to ensure consistency
        keys = list(CRAFT_DATABASE.keys())
        selected_key = keys[hash(name_lower) % len(keys)]
        
    craft = CRAFT_DATABASE[selected_key]
    
    return {
        'craft_key': selected_key,
        'category': craft['category'],
        'materials': craft['materials'],
        'region': craft['region'],
        'confidence': 0.94 + round(random.uniform(0.01, 0.05), 2),
        'suggested_tags': craft['tags']
    }

def generate_ai_draft(craft_key, voice_notes="", language="hi", artisan_name="Ramesh Prajapati"):
    """
    Indic NLP & Multilingual Listing Drafter.
    Converts craft features + voice input into rich title, story, and tags in specified language.
    """
    craft = CRAFT_DATABASE.get(craft_key, CRAFT_DATABASE['terracotta'])
    
    style_keywords = ["Traditional Motif", "Heritage Pattern", "Artisan Special Edition", "Classic Handcrafted"]
    selected_style = random.choice(style_keywords)
    
    title = craft['title_templates'].get(language, craft['title_templates']['en']).format(style=selected_style)
    story = craft['story_templates'].get(language, craft['story_templates']['en'])
    
    if voice_notes and len(voice_notes) > 3:
        story += f"\n\n[Artisan Note / आवाज की बात]: \"{voice_notes}\""
        
    return {
        'title': title,
        'story': story,
        'category': craft['category'],
        'materials': craft['materials'],
        'region': craft['region'],
        'tags': craft['tags']
    }

def calculate_fair_price(craft_key, custom_hours=None, custom_materials_cost=None):
    """
    Python Fair Pricing Engine with Transparent Rationale.
    Calculates:
    - Base Material Cost
    - Artisan Fair Labor Wage (Hours * Hourly Rate)
    - Complexity & Craft Skill Multiplier
    - Fair Price Suggestion with Min/Max Acceptable Range
    - Net Payouts across marketplaces with explicit fee transparency
    """
    craft = CRAFT_DATABASE.get(craft_key, CRAFT_DATABASE['terracotta'])
    
    mat_cost = custom_materials_cost if custom_materials_cost is not None else craft['material_cost']
    hours = custom_hours if custom_hours is not None else craft['default_hours']
    labor_cost = round(hours * craft['hourly_rate'], 2)
    artisan_skill_margin = round((mat_cost + labor_cost) * 0.25, 2)
    
    suggested = round(mat_cost + labor_cost + artisan_skill_margin, -1) # rounded to nearest 10
    min_price = round(suggested * 0.88, -1)
    max_price = round(suggested * 1.15, -1)
    
    rationale = (
        f"Raw Materials ({', '.join(craft['materials'][:2])}): ₹{mat_cost:g} | "
        f"Artisan Labor ({hours:g} hrs @ ₹{craft['hourly_rate']:g}/hr): ₹{labor_cost:g} | "
        f"Artisan Heritage Margin: ₹{artisan_skill_margin:g} | "
        f"Fair Suggested Retail: ₹{suggested:g}"
    )
    
    # Net Fee Breakdown across marketplaces
    fee_breakdown = {
        'native': {
            'name': 'Karigar Setu (Native)',
            'fee_pct': 2.5,
            'fee_amount': round(suggested * 0.025, 2),
            'net_payout': round(suggested * (1 - 0.025), 2),
            'notes': 'Flat 2.5% transparent platform maintenance fee. No hidden listing charges.'
        },
        'india_handmade': {
            'name': 'India Handmade (Govt)',
            'fee_pct': 0.0,
            'fee_amount': 0.0,
            'net_payout': suggested,
            'notes': '0% commission. Ministry of Textiles portal. GST Enrolment ID path supported.'
        },
        'etsy': {
            'name': 'Etsy Global Market',
            'fee_pct': 11.5, # 6.5% transaction + payment processing + listing fee conversion
            'fee_amount': round(suggested * 0.115 + 16.5, 2), # $0.20 approx ₹16.50
            'net_payout': round(suggested - (suggested * 0.115 + 16.5), 2),
            'notes': 'Stacked charges: $0.20 (₹16.50) per listing + 6.5% transaction fee + payment gateway fee.'
        },
        'kreate': {
            'name': 'Kreate Marketplace',
            'fee_pct': 20.0,
            'fee_amount': round(suggested * 0.20, 2),
            'net_payout': round(suggested * 0.80, 2),
            'notes': '20% commission + monthly seller tier subscription.'
        },
        'unfade': {
            'name': 'Unfade Artisans',
            'fee_pct': 0.0,
            'fee_amount': 0.0,
            'net_payout': suggested,
            'notes': '0% commission, local Jaipur ecosystem reach.'
        }
    }
    
    return {
        'suggested_price': suggested,
        'min_price': min_price,
        'max_price': max_price,
        'material_cost': mat_cost,
        'labor_cost': labor_cost,
        'labor_hours': hours,
        'artisan_margin': artisan_skill_margin,
        'reasoning': rationale,
        'fee_breakdown': fee_breakdown
    }

if __name__ == '__main__':
    print("Testing AI Engine...")
    img_res = analyze_product_image("terracotta_pot")
    print("Vision Analysis:", img_res)
    draft = generate_ai_draft("terracotta", "बहुत ही सुंदर मिट्टी का घोड़ा बनाया है", "hi")
    print("AI Draft:", draft)
    pricing = calculate_fair_price("terracotta")
    print("Fair Price:", pricing['suggested_price'], pricing['reasoning'])
