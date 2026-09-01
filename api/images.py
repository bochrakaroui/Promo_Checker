"""
Shared image-selection rules for the API.

A product can be listed by several stores, each with its own picture, and some
of those rows may still hold a brand logo or a placeholder from an older scrape.
These helpers make every endpoint pick the same image for a product: a real
product photo, from the most recent scrape.
"""

# SQL predicate: the listing holds a usable product photo.
# Mirrors PromoChecker.images.is_product_image so the API never surfaces a
# brand logo that slipped into the database before the scrapers were fixed.
PRODUCT_IMAGE_PREDICATE = """
    pl.image_url IS NOT NULL
    AND pl.image_url <> ''
    AND pl.image_url NOT LIKE 'data:%%'
    AND pl.image_url NOT ILIKE '%%/wysiwyg/%%'
    AND pl.image_url NOT ILIKE '%%/img/m/%%'
    AND pl.image_url NOT ILIKE '%%/img/cms/%%'
    AND pl.image_url NOT ILIKE '%%/media/catalog/category/%%'
    AND pl.image_url NOT ILIKE '%%manufacturer%%'
    AND pl.image_url NOT ILIKE '%%placeholder%%'
    AND pl.image_url NOT ILIKE '%%no_selection%%'
"""

# CTE exposing one image per product: newest scrape wins, listing_id breaks ties
# so the result is stable between requests.
PRODUCT_IMAGES_CTE = f"""
    product_images AS (
        SELECT DISTINCT ON (pl.product_key)
            pl.product_key,
            pl.image_url
        FROM product_listings pl
        WHERE {PRODUCT_IMAGE_PREDICATE}
        ORDER BY pl.product_key, pl.last_scraped_at DESC NULLS LAST, pl.listing_id
    )
"""


def product_image_subquery(product_key_expr: str) -> str:
    """
    Correlated scalar subquery returning the best image for a product.

    Use where a CTE cannot be joined (e.g. inside an aggregated SELECT).

    Args:
        product_key_expr: SQL expression for the product key, e.g. "p.product_key"
    """
    return f"""(
        SELECT pl.image_url
        FROM product_listings pl
        WHERE pl.product_key = {product_key_expr}
          AND {PRODUCT_IMAGE_PREDICATE}
        ORDER BY pl.last_scraped_at DESC NULLS LAST, pl.listing_id
        LIMIT 1
    )"""
