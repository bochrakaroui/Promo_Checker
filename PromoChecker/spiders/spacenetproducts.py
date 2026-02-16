import scrapy


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
            link_elem = product.css("div.left-product a")
            product_name = link_elem.css("::attr(title)").get(default="").strip()
            
            yield {
                "name": product_name,
                "link": response.urljoin(
                    product.css(
                        "div.left-product a::attr(href)"
                    ).get(default="")
                ),
                "image": response.urljoin(
                    product.css(
                        "div.left-product img::attr(src)"
                    ).get(default="")
                ),
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