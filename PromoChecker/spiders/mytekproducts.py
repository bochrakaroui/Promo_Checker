import scrapy
from scrapy_playwright.page import PageMethod

from PromoChecker.images import extract_image_url


class MytekProductsSpider(scrapy.Spider):
    name = "mytekproducts"
    allowed_domains = ["mytek.tn"]
    start_urls = [
        "https://www.mytek.tn/informatique/ordinateurs-portables.html",
    ]

    # Real cards carry a product id; the page also ships empty "shimmer"
    # placeholder cards that share the .product-container class.
    CARDS_SELECTOR = "#product-cards-row .product-container[data-product-id]"

    def _request(self, url):
        return scrapy.Request(
            url,
            meta={
                "playwright": True,
                # The grid is rendered client-side: without waiting for a real
                # card we only see the skeleton and scrape nothing.
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_selector", self.CARDS_SELECTOR, timeout=60000
                    ),
                ],
            },
            callback=self.parse,
            errback=self.errback,
        )

    def start_requests(self):
        for url in self.start_urls:
            yield self._request(url)

    def parse(self, response):
        products = response.css(self.CARDS_SELECTOR)
        if not products:
            products = response.css(".product-container[data-product-id]")

        for product in products:
            image_url = extract_image_url(
                product,
                response,
                selectors=[
                    "div.product-item-photo img",
                    "a img",
                ],
            )

            if not image_url:
                self.logger.warning(
                    "No product image found for %s",
                    product.css("a.product-item-link::text").get(default="").strip()[:60],
                )

            yield {
                "name": product.css(
                    "h1.product-item-name a.product-item-link::text"
                ).get(default="").strip(),
                "link": response.urljoin(
                    product.css(
                        "h1.product-item-name a.product-item-link::attr(href)"
                    ).get(default="")
                ),
                "sku": product.css("div.sku::text").get(default="").strip(),
                "description": product.css(
                    "div.search-short-description::text"
                ).get(default="").strip(),
                "final_price": product.css(
                    "span.final-price::text"
                ).get(default="").strip(),
                "original_price": product.css(
                    "span.original-price::text"
                ).get(default="").strip(),
                "availability": product.css(
                    "div.availability span::text"
                ).get(default="").strip(),
                "brand": product.css(
                    "div.brand a::attr(title)"
                ).get(default="").strip(),
                "image": image_url,
                "brand_image": response.urljoin(
                    product.css("div.brand img::attr(src)").get("")
                ),
            }

        # Pagination: the old 'a[aria-label="Next"]' link is gone, the grid now
        # renders a numbered pager (?categoryId=..&p=N). Follow every page link
        # and let Scrapy's duplicate filter drop the ones already visited.
        page_links = response.css(
            "nav.custom-pagination a.page-link::attr(href)"
        ).getall()
        for href in page_links:
            yield self._request(response.urljoin(href))

    def errback(self, failure):
        self.logger.error("Request failed: %s", failure.value)
