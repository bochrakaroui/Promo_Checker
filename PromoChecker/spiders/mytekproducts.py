import scrapy


class MytekProductsSpider(scrapy.Spider):
    name = "mytekproducts"
    allowed_domains = ["mytek.tn"]
    start_urls = [
        "https://www.mytek.tn/informatique/ordinateurs-portables.html",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
                callback=self.parse,
            )

    def parse(self, response):
        # Wait for product images to load
        for product in response.css("div.product-container"):
            # Try multiple selectors for image URL
            img_url = (
                product.css("img.product-image-photo::attr(src)").get() or
                product.css("img.product-image-photo::attr(data-src)").get() or
                product.css("a.product-item-photo img::attr(src)").get() or
                product.css("span.product-image-container img::attr(src)").get()
            )
            
            yield {
                "name": product.css(
                    "h1.product-item-name a.product-item-link::text"
                ).get(default="").strip(),
                "link": response.urljoin(
                    product.css(
                        "h1.product-item-name a.product-item-link::attr(href)"
                    ).get()
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
                "image_url": response.urljoin(img_url) if img_url else None,
                "brand_image": response.urljoin(
                    product.css("div.brand img::attr(src)").get("")
                ),
            }

        # Pagination "Next"
        next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={"playwright": True},
                callback=self.parse,
            )
