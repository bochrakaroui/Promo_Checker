"""
Data normalization module for PromoChecker
Standardizes product data from different sources (Mytek, Tunisianet, Spacenet)
"""
import re
import json
from typing import Dict, Any, Optional, List

from PromoChecker.images import clean_image_url


# A price can never exceed this; anything above means the string was misread.
MAX_PLAUSIBLE_PRICE = 1_000_000


def normalize_price(price_string: str) -> Optional[float]:
    """
    Normalize price from various formats to float

    Tunisian stores quote dinars with 3-decimal millimes and use a space
    (often \xa0 or \u202f) as the thousands separator:
        "1 099,000 DT"  (Tunisianet, Spacenet) -> 1099.0
        "1099.000 DT"   (Mytek)                -> 1099.0
        "1.399,000 DT"                         -> 1399.0
        "29,000 DT"     (a 29 dinar accessory) -> 29.0
        "1459 DT"                              -> 1459.0

    Args:
        price_string: Raw price string from scraper

    Returns:
        Float price value or None if invalid
    """
    if not price_string or not str(price_string).strip():
        return None

    # Drop the currency and every kind of space (spaces only ever separate
    # thousands here, never decimals).
    price_clean = re.sub(r'(?i)\bdt\b|dinar[s]?', '', str(price_string))
    price_clean = re.sub(r'[\s\xa0\u202f\u2009\u200a]+', '', price_clean)
    price_clean = re.sub(r'[^\d.,]', '', price_clean)

    if not price_clean or not any(c.isdigit() for c in price_clean):
        return None

    last_dot = price_clean.rfind('.')
    last_comma = price_clean.rfind(',')
    decimal_pos = max(last_dot, last_comma)

    if decimal_pos == -1:
        # Plain integer: "1459"
        value = float(price_clean)
    else:
        decimals = len(price_clean) - decimal_pos - 1
        if decimals == 3 or decimals in (1, 2):
            # Trailing separator is the decimal point (millimes or centimes);
            # everything before it is grouping. "1.399,000" -> 1399.000
            integer_part = re.sub(r'[.,]', '', price_clean[:decimal_pos])
            value = float(f"{integer_part}.{price_clean[decimal_pos + 1:]}")
        else:
            # Separators are grouping only: "1,459,000" -> 1459000
            value = float(re.sub(r'[.,]', '', price_clean))

    if value <= 0 or value > MAX_PLAUSIBLE_PRICE:
        # Better to record no price than a value that is off by 1000x.
        return None

    return value


def normalize_product_name(name: str) -> str:
    """
    Clean and standardize product names
    - Remove "en Tunisie" suffix
    - Remove extra spaces
    
    Args:
        name: Raw product name
        
    Returns:
        Cleaned product name
    """
    if not name:
        return ""
    
    # Remove "en Tunisie" suffix
    name = re.sub(r'\s+en\s+Tunisie\s*$', '', name, flags=re.IGNORECASE)
    
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def extract_brand(name: str) -> Optional[str]:
    """Extract brand from product name"""
    name_lower = name.lower()
    
    brands = ['lenovo', 'hp', 'dell', 'asus', 'acer', 'msi', 'apple', 'samsung', 
              'toshiba', 'sony', 'lg', 'microsoft', 'huawei', 'xiaomi', 'gigabyte']
    
    for brand in brands:
        if brand in name_lower:
            return brand
    
    return None


def extract_model(name: str, brand: Optional[str]) -> Optional[str]:
    """Extract model/series from product name"""
    if not brand:
        return None
    
    name_lower = name.lower()
    
    # Specific model patterns - order matters (most specific first)
    model_patterns = [
        # HP models with full part number
        r'(\d+-[\w\d]+nk)',  # Pattern like "15-fd0421nk"
        # Dell specific models
        r'(vostro\s+\d{4})',  # vostro 3520
        r'(inspiron\s+\d{4})',
        r'(latitude\s+\d{4})',
        r'(xps\s+\d{2,4})',
        # Lenovo specific
        r'(ideapad\s+(?:slim\s+)?\d+\s+\w+)',  # ideapad slim 3 15ian8 or ideapad 1 15ijl7
        r'(thinkpad\s+\w+\d+)',  # thinkpad e14
        r'(thinkbook\s+\d+)',
        r'(legion\s+\w*\d+)',
        r'(v\d+\s+g\d+)',  # v15 g2
        # HP other patterns
        r'(elitebook\s+\d+\s+g\d+)',
        r'(probook\s+\d+\s+g\d+)',
        r'(pavilion\s+[\w\d-]+)',
        r'(victus\s+[\w\d-]+)',
        r'(omen\s+[\w\d-]+)',
        # ASUS
        r'(vivobook\s+[\w\d\s]+?)(?:\s+[/]|\s+ultra|\s+i\d|\s+ryzen|\s+core)',
        r'(zenbook\s+[\w\d\s]+?)(?:\s+[/]|\s+ultra|\s+i\d|\s+ryzen)',
        r'(zenscreen\s+[\w\d]+)',
        r'(rog\s+[\w\s]+?)(?:\s+[/]|\s+i\d|\s+ultra|\s+ryzen)',
        r'(tuf\s+gaming\s+[\w\d]+)',
        # Acer
        r'(extensa\s+\d+)',
        r'(aspire\s+[\w\d]+)',
        r'(nitro\s+\d+)',
        # MSI
        r'(modern\s+\d+\s+[\w\d]+)',
        r'(katana\s+\d+\s+[\w\d]+)',
        r'(cyborg\s+\d+\s+[\w\d]+)',
        r'(thin\s+\d+\s+[\w\d]+)',
        # Apple
        r'(macbook\s+(?:air|pro)\s+m\d+(?:\s+pro)?)',
    ]
    
    for pattern in model_patterns:
        match = re.search(pattern, name_lower)
        if match:
            model = match.group(1).strip()
            # Normalize spaces to underscores
            model = re.sub(r'\s+', '_', model)
            return model
    
    return None


def extract_cpu(name: str) -> Dict[str, Optional[str]]:
    """
    Extract CPU information from product name
    Returns dict with 'type', 'generation', and 'full' keys
    """
    name_lower = name.lower()
    
    cpu_info = {
        'type': None,
        'generation': None,
        'full': None
    }
    
    # Intel Core patterns with specific model numbers (more precise)
    # Pattern: i5-1335U, i7-13620H, i5 12Gén
    core_specific_pattern = r'(i[3579])[\s-]*(\d{4,5}[a-z]*)'
    core_specific_match = re.search(core_specific_pattern, name_lower)
    if core_specific_match:
        cpu_type = core_specific_match.group(1)
        cpu_model = core_specific_match.group(2)
        cpu_info['type'] = cpu_type
        cpu_info['generation'] = cpu_model
        cpu_info['full'] = f"{cpu_type}_{cpu_model}"
        return cpu_info
    
    # Intel Core with generation only
    core_gen_pattern = r'(i[3579])[\s-]*(\d{1,2})(?:th\s+gen|gen|gén|ème\s+génération)'
    core_gen_match = re.search(core_gen_pattern, name_lower)
    if core_gen_match:
        cpu_info['type'] = core_gen_match.group(1)
        cpu_info['generation'] = core_gen_match.group(2)
        cpu_info['full'] = f"{cpu_info['type']}_{cpu_info['generation']}"
        return cpu_info
    
    # Intel Core 3/5/7 (new naming)
    core_new_pattern = r'core\s+([357])[\s-]*(\d{3}[a-z]*)'
    core_new_match = re.search(core_new_pattern, name_lower)
    if core_new_match:
        cpu_info['type'] = f"core{core_new_match.group(1)}"
        cpu_info['generation'] = core_new_match.group(2)
        cpu_info['full'] = f"core{core_new_match.group(1)}_{core_new_match.group(2)}"
        return cpu_info
    
    # Intel Ultra (new naming)
    ultra_pattern = r'ultra\s+([579])[\s-]*(\d{3}[a-z]*)'
    ultra_match = re.search(ultra_pattern, name_lower)
    if ultra_match:
        cpu_info['type'] = f"ultra{ultra_match.group(1)}"
        cpu_info['generation'] = ultra_match.group(2)
        cpu_info['full'] = f"ultra{ultra_match.group(1)}_{ultra_match.group(2)}"
        return cpu_info
    
    # Intel Celeron/Pentium with model number
    celeron_pattern = r'(?:celeron|pentium)\s+([nj]?\d+[a-z]*)'
    celeron_match = re.search(celeron_pattern, name_lower)
    if celeron_match:
        cpu_info['type'] = 'celeron' if 'celeron' in name_lower else 'pentium'
        cpu_info['generation'] = celeron_match.group(1)
        cpu_info['full'] = f"{cpu_info['type']}_{cpu_info['generation']}"
        return cpu_info
    
    # Intel N-series (N100, N305, etc.)
    n_series_pattern = r'\bn(\d{3,4})\b'
    n_match = re.search(n_series_pattern, name_lower)
    if n_match:
        cpu_info['type'] = 'n_series'
        cpu_info['generation'] = n_match.group(1)
        cpu_info['full'] = f"n{cpu_info['generation']}"
        return cpu_info
    
    # AMD Ryzen with model number
    ryzen_specific_pattern = r'ryzen\s+(?:ai\s+)?([3579])[\s-]*(\d{4}[a-z]*)'
    ryzen_specific_match = re.search(ryzen_specific_pattern, name_lower)
    if ryzen_specific_match:
        cpu_info['type'] = f"ryzen{ryzen_specific_match.group(1)}"
        cpu_info['generation'] = ryzen_specific_match.group(2)
        cpu_info['full'] = f"ryzen{ryzen_specific_match.group(1)}_{ryzen_specific_match.group(2)}"
        return cpu_info
    
    # AMD Ryzen general
    ryzen_pattern = r'ryzen\s+([3579])[\s-]*(\d+)?'
    ryzen_match = re.search(ryzen_pattern, name_lower)
    if ryzen_match:
        cpu_info['type'] = f"ryzen{ryzen_match.group(1)}"
        if ryzen_match.group(2):
            cpu_info['generation'] = ryzen_match.group(2)
            cpu_info['full'] = f"{cpu_info['type']}_{cpu_info['generation']}"
        else:
            cpu_info['full'] = cpu_info['type']
        return cpu_info
    
    # Apple Silicon
    apple_pattern = r'm(\d+)(?:\s+(pro|max|ultra))?'
    apple_match = re.search(apple_pattern, name_lower)
    if apple_match and 'macbook' in name_lower:
        chip = f"m{apple_match.group(1)}"
        if apple_match.group(2):
            chip += f"_{apple_match.group(2)}"
        cpu_info['type'] = 'apple_silicon'
        cpu_info['generation'] = chip
        cpu_info['full'] = chip
        return cpu_info
    
    return cpu_info


def extract_ram(name: str) -> Optional[int]:
    """Extract RAM size in GB from product name"""
    # Patterns: "8Go", "8 Go", "8G", "8 G", "8GB", "8 GB", "32Go"
    # Look for RAM-specific context to avoid confusion with storage
    ram_pattern = r'(\d+)\s*g[ob]?(?:\s+(?:ddr|ram|mémoire|de\s+mémoire)|\s+ddr\d+|\b)'
    match = re.search(ram_pattern, name.lower())
    if match:
        ram_size = int(match.group(1))
        # RAM is typically 2, 4, 8, 12, 16, 24, 32, 48, 64 GB
        if ram_size in [2, 3, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64]:
            return ram_size
    
    # Fallback: look for first small Go/GB/G value (< 64)
    all_go_pattern = r'(\d+)\s*g[ob]?'
    all_matches = re.findall(all_go_pattern, name.lower())
    if all_matches:
        for match in all_matches:
            size = int(match)
            if size in [2, 3, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64]:
                return size
    
    return None


def extract_storage(name: str) -> Optional[int]:
    """Extract storage size in GB from product name"""
    # Patterns: "256Go SSD", "512 Go", "256G SSD", "1To", "1 To"
    
    # Check for TB/To first
    tb_pattern = r'(\d+)\s*to(?:\s+ssd|\s+hdd|\b)'
    tb_match = re.search(tb_pattern, name.lower())
    if tb_match:
        return int(tb_match.group(1)) * 1024  # Convert to GB
    
    # Check for storage with SSD/HDD/NVMe explicitly mentioned
    storage_explicit_pattern = r'(\d+)\s*g[ob]?\s*(?:ssd|hdd|nvme)'
    storage_match = re.search(storage_explicit_pattern, name.lower())
    if storage_match:
        storage_size = int(storage_match.group(1))
        # Storage is typically 128, 256, 512, 1024, 2048
        if storage_size >= 128:
            return storage_size
    
    # Look for storage-specific context
    storage_context_pattern = r'(\d+)\s*g[ob]?\s*(?:de\s+)?(?:disque|stockage)'
    storage_context_match = re.search(storage_context_pattern, name.lower())
    if storage_context_match:
        return int(storage_context_match.group(1))
    
    # Find all "XGo" or "XG" patterns and identify storage
    # Storage is usually the largest number >= 128
    all_go_pattern = r'(\d+)\s*g[ob]?'
    all_matches = re.findall(all_go_pattern, name.lower())
    if all_matches:
        numbers = [int(m) for m in all_matches]
        # Storage sizes: 128, 256, 512, 1024, 2048
        storage_candidates = [n for n in numbers if n >= 128 and n in [128, 256, 512, 1024, 2048]]
        if storage_candidates:
            return max(storage_candidates)
    
    return None


def extract_specs(name: str) -> Dict[str, Any]:
    """
    Extract all specifications from product name
    
    Returns:
        Dict with brand, model, cpu, ram, storage
    """
    clean_name = normalize_product_name(name)
    
    specs = {
        'brand': extract_brand(clean_name),
        'model': None,
        'cpu': extract_cpu(clean_name)['full'],
        'cpu_type': extract_cpu(clean_name)['type'],
        'cpu_generation': extract_cpu(clean_name)['generation'],
        'ram': extract_ram(clean_name),
        'storage': extract_storage(clean_name)
    }
    
    specs['model'] = extract_model(clean_name, specs['brand'])
    
    return specs


def generate_product_key(specs: Dict[str, Any]) -> str:
    """
    Generate unique product key for matching
    Format: {brand}_{model}_{cpu}_{ram}_{storage}
    
    Only generates keys for products with sufficient information to avoid false matches.
    Requires at minimum: brand + model OR brand + cpu + ram + storage
    
    Args:
        specs: Dictionary with extracted specifications
        
    Returns:
        Product key string (e.g., "dell_vostro_3520_i5_1335u_8_512")
        Returns empty string if insufficient data for reliable matching
    """
    brand = specs.get('brand')
    model = specs.get('model')
    cpu = specs.get('cpu')
    ram = specs.get('ram')
    storage = specs.get('storage')
    
    # Require brand at minimum
    if not brand:
        return ''
    
    parts = [brand]
    
    # Strategy 1: Brand + Model + Specs (most reliable)
    # Good for: Dell Vostro 3520 i5-1335U 8Go 512Go
    if model and cpu:
        parts.append(model)
        parts.append(cpu)
        if ram:
            parts.append(str(ram))
        if storage:
            parts.append(str(storage))
        return '_'.join(parts)
    
    # Strategy 2: Brand + Model only (for unique models like HP 15-fd0421nk)
    # Only if model is specific enough (contains numbers/dashes)
    if model and (any(c.isdigit() for c in model) or '-' in model):
        parts.append(model)
        if cpu:
            parts.append(cpu)
        if ram:
            parts.append(str(ram))
        if storage:
            parts.append(str(storage))
        # Only return if we have model + at least 2 more specs
        if len(parts) >= 4:
            return '_'.join(parts)
    
    # Strategy 3: Brand + CPU + RAM + Storage (for generic models)
    # Only if we have ALL specs (otherwise too generic)
    if cpu and ram and storage:
        parts.append(cpu)
        parts.append(str(ram))
        parts.append(str(storage))
        return '_'.join(parts)
    
    # Not enough info for reliable matching - return empty
    # This prevents false matches like "dell_8_512" matching all Dell laptops with 8GB/512GB
    return ''


def standardize_fields(raw_product: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Map different source formats to unified schema
    
    Args:
        raw_product: Raw product data from scraper
        source: Source name ('mytek', 'tunisianet', 'spacenet')
        
    Returns:
        Standardized product dictionary
    """
    # Get name from source
    name = raw_product.get('name', '')
    clean_name = normalize_product_name(name)
    
    # Extract specs
    specs = extract_specs(name)
    
    # Product image: accept whichever key the spider used, but never fall back
    # to `brand_image` - that is the manufacturer logo, not the product photo.
    image = None
    for key in ('image', 'image_url', 'img', 'thumbnail'):
        image = clean_image_url(raw_product.get(key))
        if image:
            break

    # Base standardized product
    standardized = {
        'name': clean_name,
        'original_name': name,
        'source': source,
        'product_key': generate_product_key(specs),
        'specs': specs,
        'link': raw_product.get('link', ''),
        'image': image,
        'brand_image': raw_product.get('brand_image') or None,
    }
    
    # Price handling based on source
    if source == 'mytek':
        standardized['final_price'] = normalize_price(raw_product.get('final_price', ''))
        standardized['original_price'] = normalize_price(raw_product.get('original_price', ''))
        standardized['sku'] = raw_product.get('sku', '').strip('[]')
        standardized['availability'] = raw_product.get('availability', '')
        standardized['brand'] = raw_product.get('brand', specs.get('brand', ''))
        
    elif source == 'tunisianet':
        standardized['final_price'] = normalize_price(raw_product.get('price', ''))
        standardized['original_price'] = normalize_price(raw_product.get('original_price', ''))
        standardized['reference'] = raw_product.get('reference', '')
        standardized['availability'] = raw_product.get('availability', '')
        standardized['brand'] = raw_product.get('brand', specs.get('brand', ''))
        # Ensure Tunisianet links always use the correct domain
        link = raw_product.get('link', '')
        if link and not link.startswith('http'):
            link = 'https://www.tunisianet.com.tn' + (link if link.startswith('/') else '/' + link)
        elif link and 'tunisianet' in link:
            # Replace any wrong domain with the correct one
            link = re.sub(r'https?://[^/]*tunisianet[^/]*', 'https://www.tunisianet.com.tn', link)
        standardized['link'] = link
        standardized['product_url'] = link
    elif source == 'spacenet':
        standardized['final_price'] = normalize_price(raw_product.get('final_price', ''))
        standardized['original_price'] = normalize_price(raw_product.get('original_price', ''))
        standardized['discount'] = raw_product.get('discount', '')
    
    # Calculate discount percentage if both prices available
    if standardized.get('final_price') and standardized.get('original_price'):
        final = standardized['final_price']
        original = standardized['original_price']
        if original > 0:
            standardized['discount_percentage'] = round(((original - final) / original) * 100, 2)
        else:
            standardized['discount_percentage'] = 0
    else:
        standardized['discount_percentage'] = 0
    
    return standardized


def normalize_scraped_data(json_file: str, source: str, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Complete normalization pipeline for a JSON file
    
    Args:
        json_file: Path to input JSON file
        source: Source name ('mytek', 'tunisianet', 'spacenet')
        output_file: Optional path to save normalized data
        
    Returns:
        List of normalized products
    """
    # Read raw data
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Normalize each product
    normalized_data = []
    for product in raw_data:
        try:
            normalized = standardize_fields(product, source)
            normalized_data.append(normalized)
        except Exception as e:
            print(f"Error normalizing product {product.get('name', 'Unknown')}: {e}")
            continue
    
    # Save if output file specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(normalized_data)} normalized products to {output_file}")
    
    return normalized_data


def analyze_matches(normalized_files: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Find matching products across multiple sources
    
    Args:
        normalized_files: List of paths to normalized JSON files
        
    Returns:
        Dictionary mapping product_key to list of matching products from different sources
    """
    all_products = []
    
    # Load all normalized data
    for file in normalized_files:
        with open(file, 'r', encoding='utf-8') as f:
            products = json.load(f)
            all_products.extend(products)
    
    # Group by product_key
    matches = {}
    for product in all_products:
        key = product.get('product_key', '')
        if key and key != '':
            if key not in matches:
                matches[key] = []
            matches[key].append(product)
    
    # Filter to only multi-source matches
    multi_source_matches = {k: v for k, v in matches.items() if len(v) > 1}
    
    return multi_source_matches


if __name__ == "__main__":
    # Example usage
    print("PromoChecker Data Normalization Module")
    print("=" * 50)
    
    # Test with sample products
    test_products = [
        "Pc Portable Dell Vostro 3520 i5 12Gén 8Go 512Go SSD en Tunisie",
        "PC Portable LENOVO IdeaPad 1 15IJL7 Intel Celeron N4500 8Go 256Go SSD",
        "Pc Portable HP 15-fd0421nk / N100 / 4 Go / 256 Go SSD / Noir",
    ]
    
    for product in test_products:
        print(f"\nProduct: {product}")
        specs = extract_specs(product)
        key = generate_product_key(specs)
        print(f"Specs: {specs}")
        print(f"Product Key: {key}")
