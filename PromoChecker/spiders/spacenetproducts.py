import scrapy

from PromoChecker.images import extract_image_url


class SpacenetProductsSpider(scrapy.Spider):
    name = "spacenetproducts"
    allowed_domains = ["spacenet.tn"]
    start_urls = [
        "https://spacenet.tn/promotions?categories=ordinateur-portable",
        "https://spacenet.tn/promotions?categories=composants-informatique-processeur-core-i7-tunisie",
        "https://spacenet.tn/promotions?categories=accessoires-ordinateurs-tunisie",
        "https://spacenet.tn/promotions?categories=tablette-tunisie",
        "https://spacenet.tn/promotions?categories=ordinateur-bureau-tunisie",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
                callback=self.parse,
            )

    def parse(self, response):
        for product in response.css("div.field-product-item"):
            # Get name from the link title attribute
            # The name used to live on the link's title attribute; it now sits
            # on the product image, so try both before giving up.
            link_elem = product.css("div.left-product a")
            product_name = (
                link_elem.css("::attr(title)").get(default="").strip()
                or product.css("img.product_image::attr(title)").get(default="").strip()
                or product.css("img.product_image::attr(alt)").get(default="").strip()
                or " ".join(product.css("div.right-product a::text").getall()).strip()
            )

            # img.product_image is the laptop; the card also holds a
            # .manufacturer-logo image that must never be used.
            image = extract_image_url(
                product,
                response,
                selectors=[
                    "div.left-product img.product_image",
                    "div.left-product img:not(.manufacturer-logo)",
                ],
            )

            if not image:
                self.logger.warning(
                    "No product image found for %s", product_name[:60]
                )

            yield {
                "name": product_name,
                "link": response.urljoin(
                    product.css(
                        "div.left-product a::attr(href)"
                    ).get(default="")
                ),
                "image": image,
                "final_price": product.css(
                    "span.price::text"
                ).get(default="").strip(),
                "original_price": product.css(
                    "span.regular-price::text"
                ).get(default="").strip(),
                "discount": product.css(
                    "span.discount-percentage::text"
                ).get(default="").strip(),
            }

        # Pagination
        next_page = response.css("li.pagination_next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={"playwright": True},
                callback=self.parse,
            )