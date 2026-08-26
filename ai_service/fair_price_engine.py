def calculate_fair_price(material_cost, crafting_hours, labor_rate_per_hr=120.0):
    raw_material = float(material_cost)
    labor_cost = float(crafting_hours) * float(labor_rate_per_hr)
    artisan_cost = raw_material + labor_cost
    
    suggested_price = round(artisan_cost * 1.35, -1) # 35% margin for artisan
    min_price = round(artisan_cost * 1.15, -1)
    max_price = round(artisan_cost * 1.65, -1)
    
    reasoning = f'Fair Price Calculation: Raw Materials (₹{raw_material}) + Fair Labor ({crafting_hours} hrs @ ₹{labor_rate_per_hr}/hr = ₹{labor_cost}) + 35% Fair Artisan Margin.'
    
    return {
        'suggested_price': suggested_price,
        'min_price': min_price,
        'max_price': max_price,
        'breakdown': {
            'material_cost': raw_material,
            'labor_cost': labor_cost,
            'crafting_hours': crafting_hours,
            'labor_rate': labor_rate_per_hr,
            'margin_percentage': 35
        },
        'reasoning': reasoning
    }
