import os
from flask import Flask, request, jsonify
from cv_service import analyze_craft_image
from llm_catalog import generate_llm_metadata
from fair_price_engine import calculate_fair_price
from recommendation_engine import get_recommendations

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'Karigar Setu AI Microservice v3'})

@app.route('/api/ai/classify', methods=['POST'])
def classify_craft():
    data = request.json or {}
    image_url = data.get('image_url', '')
    lang = data.get('language', 'hi')
    
    cv_res = analyze_craft_image(image_url)
    llm_res = generate_llm_metadata(cv_res['craft_name'], cv_res['region'], lang=lang)
    price_res = calculate_fair_price(350, 4.5)
    
    return jsonify({
        'success': True,
        'cv_analysis': cv_res,
        'llm_metadata': llm_res,
        'pricing': price_res
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'AI Microservice running on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
