# Indic Multi-Lingual LLM Cataloguing Service (12 Languages)

INDIC_TRANSLATIONS = {
    'hi': {'crafted_by': 'कारीगर द्वारा निर्मित', 'authentic': 'प्रमाणिक हस्तशिल्प'},
    'bn': {'crafted_by': 'কারুশিল্পী দ্বারা তৈরি', 'authentic': 'প্রামাণিক হস্তশিল্প'},
    'or': {'crafted_by': 'କାରିଗର ଦ୍ୱାରା ନିର୍ମିତ', 'authentic': 'ପ୍ରାମାଣିକ ହସ୍ତଶିଳ୍ପ'},
    'ta': {'crafted_by': 'கைவினைஞரால் செய்யப்பட்டது', 'authentic': 'உண்மையான கைவினைப்பொருட்கள்'},
    'te': {'crafted_by': 'చేతివృత్తులవారిచే తయారు చేయబడింది', 'authentic': 'ప్రామాణికమైన హస్తకళలు'},
    'mr': {'crafted_by': 'कारागिराने तयार केलेले', 'authentic': 'अस्सल हस्तकला'},
    'gu': {'crafted_by': 'કારીગર દ્વારા બનાવેલ', 'authentic': 'અસલી હસ્તકલા'},
    'kn': {'crafted_by': 'ಕುಶಲಕರ್ಮಿಗಳಿಂದ ತಯಾರಿಸಲ್ಪಟ್ಟಿದೆ', 'authentic': 'ಅಧಿಕೃತ ಕರಕುಶಲತೆ'},
    'ml': {'crafted_by': 'കൈவினைജ്ഞൻ നിർമ്മിച്ചത്', 'authentic': 'യഥാർത്ഥ ഹസ്തകലകൾ'},
    'pa': {'crafted_by': 'ਕਾਰੀਗਰ ਦੁਆਰਾ ਬਣਾਇਆ ਗਿਆ', 'authentic': 'ਪ੍ਰਮਾਣਿਕ ​​ਹਸਤਕਲਾ'},
    'as': {'crafted_by': 'কাৰিকৰে নিৰ্মাণ কৰা', 'authentic': 'প্ৰামাণিক হস্তশিল্প'},
    'en': {'crafted_by': 'Crafted by Master Artisan', 'authentic': 'Authentic GI Handcraft'}
}

def generate_llm_metadata(craft_name, region, voice_note='', lang='hi'):
    lang_info = INDIC_TRANSLATIONS.get(lang, INDIC_TRANSLATIONS['en'])
    prefix = lang_info['crafted_by']
    
    title = f'Authentic Handcrafted {craft_name} from {region}'
    story = f'{prefix} in {region}. Built using generation-old heritage techniques, preserving sacred Indian craft traditions.'
    seo_title = f'{craft_name} - Direct from Artisan ({region}) | Karigar Setu'
    seo_description = f'Buy certified authentic {craft_name} handcrafted by master artisans of {region}. Fair price guaranteed.'
    instagram_caption = f'✨ Handcrafted with love in {region}. Unique {craft_name} with QR Provenance Certificate! #KarigarSetu #VocalForLocal'
    etsy_listing = f'Handmade {craft_name}, Traditional {region} Craft, Ethically Sourced Indian Artisans'

    return {
        'title': title,
        'story': story,
        'seo_title': seo_title,
        'seo_description': seo_description,
        'instagram_caption': instagram_caption,
        'etsy_listing': etsy_listing,
        'tags': [craft_name, region, 'GI Certified', 'Handmade', 'Ethical Craft', 'SIH 2026'],
        'language': lang
    }
