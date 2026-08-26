import random

def get_recommendations(product_id, products_list):
    if not products_list:
        return []
    target = next((p for p in products_list if p.get('id') == product_id), None)
    if not target:
        return products_list[:3]
    
    # Filter products in same craft category or region
    similar = [p for p in products_list if p.get('id') != product_id and (p.get('category') == target.get('category') or p.get('region') == target.get('region'))]
    if len(similar) < 3:
        others = [p for p in products_list if p.get('id') != product_id and p not in similar]
        similar.extend(others)
    
    return similar[:4]
