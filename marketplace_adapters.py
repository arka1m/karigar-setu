import json
import random
from datetime import datetime

class BaseMarketplaceAdapter:
    def __init__(self, channel_id, name, fee_type, fee_value):
        self.channel_id = channel_id
        self.name = name
        self.fee_type = fee_type
        self.fee_value = fee_value

    def transform(self, product, artisan):
        raise NotImplementedError

    def publish(self, product, artisan):
        payload = self.transform(product, artisan)
        return {
            'channel_id': self.channel_id,
            'channel_name': self.name,
            'status': 'synced',
            'external_id': f"{self.channel_id}_item_{product['id'][:8]}",
            'external_url': f"https://{self.channel_id}.example.com/listing/{product['id']}",
            'published_at': datetime.utcnow().isoformat(),
            'payload': payload
        }

class NativeMarketplaceAdapter(BaseMarketplaceAdapter):
    def __init__(self):
        super().__init__('native', 'Karigar Setu Storefront', 'flat', 2.5)

    def transform(self, product, artisan):
        return {
            'ks_product_id': product['id'],
            'title': product['title'],
            'description': product['story'],
            'category': product['category'],
            'materials': json.loads(product['materials']) if isinstance(product['materials'], str) else product['materials'],
            'price_inr': product['final_price'],
            'artisan_info': {
                'name': artisan['name'],
                'region': artisan['region'],
                'cluster': artisan['craft_cluster'],
                'kyc_ready': True
            },
            'authenticity_certificate_id': product.get('certificate_id'),
            'fee_structure': '2.5% flat platform fee'
        }

class IndiaHandmadeAdapter(BaseMarketplaceAdapter):
    def __init__(self):
        super().__init__('india_handmade', 'India Handmade (Govt)', 'zero', 0.0)

    def transform(self, product, artisan):
        return {
            'govt_portal_sku': f"IH-{product['id'][:6]}",
            'product_name_hi': product['title'],
            'craft_category_code': product['category'],
            'artisan_enrolment_id': artisan.get('gst_or_udyam_id', 'UDYAM-MICRO-TEMP-88392'),
            'selling_price': product['final_price'],
            'commission_rate': '0%',
            'gst_exemption_flag': True
        }

class EtsyAdapter(BaseMarketplaceAdapter):
    def __init__(self):
        super().__init__('etsy', 'Etsy Global', 'stacked', 6.5)

    def transform(self, product, artisan):
        # Convert price to USD approx for global listing (83 INR = 1 USD)
        usd_price = round(product['final_price'] / 83.0, 2)
        return {
            'title': product['title'][:140], # Etsy title limit
            'description': f"{product['story']}\n\nAuthentic Indian Craftsmanship from {artisan['region']}.",
            'price_usd': usd_price,
            'price_inr': product['final_price'],
            'quantity': 5,
            'tags': json.loads(product['tags'])[:13] if isinstance(product['tags'], str) else product['tags'][:13],
            'shipping_origin': 'India',
            'fee_breakdown': {
                'listing_fee_usd': 0.20,
                'transaction_fee_pct': 6.5,
                'payment_processing': '3% + ₹25'
            }
        }

class KreateAdapter(BaseMarketplaceAdapter):
    def __init__(self):
        super().__init__('kreate', 'Kreate Crafts', 'subscription', 20.0)

    def transform(self, product, artisan):
        return {
            'item_title': product['title'],
            'seller_id': artisan['id'],
            'listing_price': product['final_price'],
            'commission_cut_20pct': round(product['final_price'] * 0.20, 2),
            'net_seller_realization': round(product['final_price'] * 0.80, 2),
            'instant_preview_mode': True # Karigar Setu bypasses pre-KYC 24h block for drafting
        }

class UnfadeAdapter(BaseMarketplaceAdapter):
    def __init__(self):
        super().__init__('unfade', 'Unfade Artisans', 'flat', 0.0)

    def transform(self, product, artisan):
        return {
            'unfade_craft_story': product['story'],
            'jaipur_hub_sync': True,
            'listing_price': product['final_price'],
            'zero_commission': True
        }

# Adapter Registry
ADAPTERS = {
    'native': NativeMarketplaceAdapter(),
    'india_handmade': IndiaHandmadeAdapter(),
    'etsy': EtsyAdapter(),
    'kreate': KreateAdapter(),
    'unfade': UnfadeAdapter()
}

def sync_product_to_channels(product, artisan, selected_channel_ids):
    """
    Publishes a single product across multiple marketplaces simultaneously.
    """
    results = []
    for ch_id in selected_channel_ids:
        adapter = ADAPTERS.get(ch_id)
        if adapter:
            res = adapter.publish(product, artisan)
            results.append(res)
    return results

if __name__ == '__main__':
    dummy_artisan = {'id': 'art_01', 'name': 'Ramesh', 'region': 'Bankura', 'craft_cluster': 'Terracotta'}
    dummy_product = {'id': 'prod_99', 'title': 'Bankura Horse', 'story': 'Clay horse', 'category': 'Terracotta Pottery', 'materials': '["Clay"]', 'tags': '["Horse"]', 'final_price': 1850.0}
    
    sync_res = sync_product_to_channels(dummy_product, dummy_artisan, ['native', 'india_handmade', 'etsy'])
    print("Sync Results:", json.dumps(sync_res, indent=2))
