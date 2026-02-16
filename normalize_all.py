"""
Script to normalize all scraped data from Mytek, Tunisianet, and Spacenet
Generates normalized JSON files and a report of matching products
"""
import json
from PromoChecker.normalize import (
    normalize_scraped_data,
    analyze_matches
)


def main():
    print("=" * 70)
    print("PromoChecker - Data Normalization Pipeline")
    print("=" * 70)
    
    # Define source files and output files
    sources = [
        {
            'name': 'mytek',
            'input': 'products.json',
            'output': 'products_normalized.json'
        },
        {
            'name': 'tunisianet',
            'input': 'tunisianet_laptops.json',
            'output': 'tunisianet_laptops_normalized.json'
        },
        {
            'name': 'spacenet',
            'input': 'spacenet_promotions.json',
            'output': 'spacenet_promotions_normalized.json'
        }
    ]
    
    normalized_files = []
    
    # Normalize each source
    for source in sources:
        print(f"\n[*] Processing {source['name'].upper()}...")
        print(f"   Input: {source['input']}")
        
        try:
            normalized_data = normalize_scraped_data(
                source['input'],
                source['name'],
                source['output']
            )
            normalized_files.append(source['output'])
            
            # Show sample
            if normalized_data:
                sample = normalized_data[0]
                print(f"   [OK] Processed {len(normalized_data)} products")
                print(f"   Sample: {sample['name'][:60]}...")
                print(f"   Key: {sample['product_key']}")
                print(f"   Price: {sample.get('final_price', 'N/A')} DT")
        except Exception as e:
            print(f"   [ERROR] {e}")
    
    # Analyze matches across sources
    print("\n" + "=" * 70)
    print("[*] Analyzing Product Matches Across Stores")
    print("=" * 70)
    
    matches = analyze_matches(normalized_files)
    
    print(f"\nFound {len(matches)} unique products available in multiple stores:")
    
    # Show detailed matches
    match_count = 0
    for product_key, products in matches.items():
        if len(products) >= 2:  # Only show products in 2+ stores
            match_count += 1
            if match_count <= 10:  # Show first 10 matches
                print(f"\n{match_count}. Product Key: {product_key}")
                print(f"   Name: {products[0]['name'][:70]}")
                
                for product in products:
                    price = product.get('final_price')
                    source = product['source'].upper()
                    discount = product.get('discount_percentage', 0)
                    
                    if price is not None:
                        print(f"   - {source:12} {price:>10} DT", end='')
                        if discount > 0:
                            print(f" (-{discount}%)", end='')
                        print()
                    else:
                        print(f"   - {source:12}       N/A DT")
                
                # Find best price
                prices = [(p['source'], p.get('final_price')) for p in products if p.get('final_price')]
                if prices:
                    best = min(prices, key=lambda x: x[1])
                    print(f"   [BEST] {best[0].upper()} at {best[1]} DT")
    
    if match_count > 10:
        print(f"\n... and {match_count - 10} more matching products")
    
    # Save matches report
    matches_report = {
        'total_matches': len(matches),
        'matches': {}
    }
    
    for product_key, products in matches.items():
        matches_report['matches'][product_key] = {
            'name': products[0]['name'],
            'stores': [
                {
                    'source': p['source'],
                    'price': p.get('final_price'),
                    'link': p.get('link'),
                    'availability': p.get('availability', 'Unknown')
                }
                for p in products
            ]
        }
    
    with open('product_matches.json', 'w', encoding='utf-8') as f:
        json.dump(matches_report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print(f"[OK] Normalization Complete!")
    print(f"   - Generated {len(normalized_files)} normalized files")
    print(f"   - Found {len(matches)} products in multiple stores")
    print(f"   - Matches report saved to: product_matches.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
