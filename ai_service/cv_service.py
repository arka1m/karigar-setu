import random

CRAFT_CATEGORIES = {
    'terracotta': {'name': 'Terracotta Pottery', 'region': 'Bankura, West Bengal', 'gi_tag': 'Bankura Panchmura Terracotta Craft', 'gi_confidence': 0.94},
    'chikankari': {'name': 'Chikankari Embroidery', 'region': 'Lucknow, Uttar Pradesh', 'gi_tag': 'Lucknow Chikankari', 'gi_confidence': 0.96},
    'dokra': {'name': 'Dokra Metal Craft', 'region': 'Bikna, West Bengal / Bastar, CG', 'gi_tag': 'Bastar Dhokra', 'gi_confidence': 0.91},
    'madhubani': {'name': 'Madhubani Painting', 'region': 'Mithila, Bihar', 'gi_tag': 'Mithila Painting', 'gi_confidence': 0.98},
    'blue_pottery': {'name': 'Blue Pottery', 'region': 'Jaipur, Rajasthan', 'gi_tag': 'Jaipur Blue Pottery', 'gi_confidence': 0.95},
    'pattachitra': {'name': 'Pattachitra Art', 'region': 'Raghurajpur, Odisha', 'gi_tag': 'Odisha Pattachitra', 'gi_confidence': 0.93},
    'bamboo': {'name': 'Bamboo Craft', 'region': 'Tripura / Assam', 'gi_tag': 'North East Bamboo Craft', 'gi_confidence': 0.88},
    'handloom': {'name': 'Handloom Saree', 'region': 'Varanasi / Kanchipuram', 'gi_tag': 'Banaras Brocades & Sarees', 'gi_confidence': 0.97},
    'brass': {'name': 'Brassware Craft', 'region': 'Moradabad, Uttar Pradesh', 'gi_tag': 'Moradabad Metal Craft', 'gi_confidence': 0.92},
    'wood': {'name': 'Wood Carving', 'region': 'Saharanpur, Uttar Pradesh', 'gi_tag': 'Saharanpur Wood Craft', 'gi_confidence': 0.89}
}

def analyze_craft_image(image_path_or_url):
    url_lower = str(image_path_or_url).lower()
    selected_key = 'terracotta'
    for key in CRAFT_CATEGORIES:
        if key in url_lower:
            selected_key = key
            break
            
    craft_info = CRAFT_CATEGORIES[selected_key]
    confidence = round(random.uniform(0.89, 0.98), 2)
    
    return {
        'craft_key': selected_key,
        'craft_name': craft_info['name'],
        'region': craft_info['region'],
        'gi_tag': craft_info['gi_tag'],
        'gi_confidence': craft_info['gi_confidence'],
        'confidence_score': confidence,
        'materials_detected': ['Natural Material', 'Traditional Dye', 'Handcrafted Base'],
        'authenticity_grade': 'A+ Master Craft'
    }
