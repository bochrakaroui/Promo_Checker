import scrapy


class TunisianetLaptopsSpider(scrapy.Spider):
    name = "tunisianet_laptops"
    allowed_domains = ["tunisianet.com.tn"]
    start_urls = [
        "https://www.tunisianet.com.tn/702-ordinateur-portable?order=product.price.asc",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},  # comme pour Mytek
                callback=self.parse,
            )

    def parse(self, response):
        # Chaque bloc produit
        for product in response.css("div.thumbnail-container"):
            link = product.css(
                "a.thumbnail.product-thumbnail.first-img::attr(href)"
            ).get()

            image = product.css(
                "a.thumbnail.product-thumbnail.first-img img::attr(src)"
            ).get()

            title = product.css(
                "h2.product-title a::text"
            ).get()

            reference = product.css(
                "span.product-reference::text"
            ).get()

            # Description courte : on récupère tout le texte du bloc
            short_desc_parts = product.xpath(
                './/div[contains(@class, "listds")]//text()'
            ).getall()
            short_desc = " ".join(
                t.strip() for t in short_desc_parts if t.strip()
            )

            price = product.css(
                "div.product-price-and-shipping span.price::text"
            ).get()

            regular_price = product.css(
                "div.product-price-and-shipping span.regular-price::text"
            ).get()

            availability = product.css(
                "#stock_availability span::text"
            ).get()

            brand = product.css(
                "div.product-manufacturer img::attr(alt)"
            ).get()

            brand_image = product.css(
                "div.product-manufacturer img::attr(src)"
            ).get()

            yield {
                "name": (title or "").strip(),
                "link": response.urljoin(link) if link else None,
                "image": response.urljoin(image) if image else None,
                "reference": reference.strip("[]") if reference else None,
                "description": short_desc,
                "price": price.strip() if price else None,
                "original_price": regular_price.strip() if regular_price else None,
                "availability": availability.strip() if availability else None,
                "brand": brand.strip() if brand else None,
                "brand_image": response.urljoin(brand_image) if brand_image else None,
            }

        # Pagination (à adapter si besoin)
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                meta={"playwright": True},
                callback=self.parse,
            )
