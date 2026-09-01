"""
Image extraction helpers for PromoChecker

The stores serve product photos in different ways (lazy-loading attributes,
srcset, PrestaShop thumbnails) and every listing page also contains images that
are *not* the product: manufacturer logos, sprites, placeholders. Picking the
wrong one is what made cards show a brand logo instead of the laptop.

Everything here is deliberately source-agnostic so the three spiders and the
normalization step apply exactly the same rules.
"""
import re
from typing import Any, Iterable, List, Optional
from urllib.parse import urljoin, urlparse

# Attributes that can hold an image URL, most reliable first.
# Lazy-loaded pages keep the real URL in a data-* attribute while `src` still
# holds a 1x1 gif or a base64 blur, so data-* wins over src.
IMAGE_ATTRIBUTES = (
    "data-full-size-image-url",  # PrestaShop (Tunisianet, Spacenet)
    "data-zoom-image",
    "data-large_image",
    "data-original",
    "data-lazy-src",
    "data-lazy",
    "data-src",
    "srcset",
    "data-srcset",
    "src",
)

# URL fragments that mean "this is a logo / icon / chrome", not a product photo.
NON_PRODUCT_PATTERNS = (
    "/wysiwyg/marque/",       # Mytek brand logos
    "/wysiwyg/",              # Mytek CMS assets (banners, payment icons, ...)
    "/img/m/",                # PrestaShop manufacturer logos
    "/img/c/",                # PrestaShop category images
    "/img/cms/",              # PrestaShop CMS banners
    "/media/catalog/category/",
    "manufacturer",
    "/logo",
    "logo.",
    "sprite",
    "/icon",
    "icon-",
    "/flags/",
    "payment",
)

# URL fragments that mean "this is a placeholder waiting for lazy-loading".
PLACEHOLDER_PATTERNS = (
    "placeholder",
    "no_selection",
    "default_image",
    "blank.gif",
    "blank.png",
    "spacer.gif",
    "loader",
    "loading.",
    "lazy.gif",
    "grey.gif",
    "transparent.",
    "1x1.",
    "dummy",
)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")


def _first_from_srcset(value: str) -> str:
    """Return the largest candidate of a srcset attribute."""
    candidates = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split()
        url = bits[0]
        # Width descriptor ("640w") or pixel density ("2x"); default 0 so a bare
        # URL still participates.
        width = 0
        if len(bits) > 1:
            match = re.match(r"^(\d+(?:\.\d+)?)([wx])$", bits[1])
            if match:
                width = float(match.group(1))
                if match.group(2) == "x":
                    width *= 1000  # density: treat 2x as bigger than 1x
        candidates.append((width, url))
    if not candidates:
        return ""
    return max(candidates, key=lambda c: c[0])[1]


def is_product_image(url: Optional[str]) -> bool:
    """
    True when the URL plausibly points at a real product photo.

    Rejects empty values, inline data URIs, lazy-loading placeholders and
    brand/category/CMS artwork.
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url or url.startswith("data:"):
        return False

    lowered = url.lower()
    if any(pattern in lowered for pattern in PLACEHOLDER_PATTERNS):
        return False
    if any(pattern in lowered for pattern in NON_PRODUCT_PATTERNS):
        return False

    # Must look like an image file (query strings allowed).
    path = urlparse(lowered).path
    if path and not path.endswith(IMAGE_EXTENSIONS):
        return False

    return True


def clean_image_url(url: Optional[str], response: Any = None) -> Optional[str]:
    """
    Normalize a raw image URL: strip whitespace, resolve relative URLs against
    the page, force https, and drop it entirely if it is not a product photo.
    """
    if not url or not isinstance(url, str):
        return None

    url = url.strip().replace("\n", "").replace("\t", "")
    if not url:
        return None

    if url.startswith("//"):
        url = "https:" + url
    elif response is not None and not url.startswith(("http://", "https://", "data:")):
        url = response.urljoin(url)
    elif not url.startswith(("http://", "https://", "data:")):
        return None

    if not is_product_image(url):
        return None

    # Stores are https-only; http URLs would be blocked as mixed content.
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]

    return url


def extract_image_url(node: Any, response: Any = None,
                      selectors: Optional[Iterable[str]] = None) -> Optional[str]:
    """
    Find the product image inside a product card.

    Args:
        node: Scrapy selector for a single product block.
        response: The page response, used to resolve relative URLs.
        selectors: Optional CSS selectors tried first (most specific first).
                   Falls back to every <img> inside the card.

    Returns:
        Absolute image URL, or None when the card has no usable product image.
    """
    candidates: List[str] = []

    for selector in (selectors or ()):
        for attribute in IMAGE_ATTRIBUTES:
            for raw in node.css(f"{selector}::attr({attribute})").getall():
                candidates.append(
                    _first_from_srcset(raw) if "srcset" in attribute else raw
                )

    # Fallback: scan every image in the card, still in attribute priority order
    # so a lazy-loaded data-src beats a placeholder src.
    for attribute in IMAGE_ATTRIBUTES:
        for raw in node.css(f"img::attr({attribute})").getall():
            candidates.append(
                _first_from_srcset(raw) if "srcset" in attribute else raw
            )

    for candidate in candidates:
        cleaned = clean_image_url(candidate, response)
        if cleaned:
            return cleaned

    return None
