SCHEMA = {
    "type": "object",
    "description": "This schema is used to generate SEO-optimized content for given product. Based on the provided product information (title, description, category, and source website) of a product, the AI will regenerate SEO-focused content including a title, expanded description, short description, meta description, and focus keyphrase. This process is designed to ensure that product listings on WooCommerce store are optimized for search engines to maximize visibility and appeal to potential buyers on online marketplaces and stores.",
    "properties": {
        "title": {
            "type": "string",
            "description": "The AI-generated title for the product, summarizing its key features, design elements, or use cases in a concise, SEO-optimized manner. The title should highlight the main attributes of the product, ensuring it captures both user attention and search engine relevance for buyers."
        },
        "expanded_description": {
            "type": "string",
            "description": "A detailed and informative description of the product. This field provides in-depth information about the product’s design, intended use, technical specifications, and its suitability for various applications. The description should also highlight any unique features that set this product apart from others in the marketplace, while being optimized for SEO to help the listing rank higher on search engines."
        },
        "short_description": {
            "type": "string",
            "description": "A concise summary of the product, focusing on its key features or unique selling points. This short description is ideal for quick reference by users browsing search results or product listings on online platforms, emphasizing the most compelling aspects of the product."
        },
        "meta_description": {
            "type": "string",
            "description": "A brief, SEO-focused description (under 255 characters) of the product, designed to appear in search engine result previews. The meta description should contain key information about the product, its uses, and a call-to-action to encourage users to click through to the product page. The description should be highly relevant to search queries related to the product."
        },
        "focus_keyphrase": {
            "type": "string",
            "description": "The main keyword or keyphrase for the product, used to optimize its SEO performance. This keyphrase should be a term that prospective buyers are likely to search for when looking for products like this one. It should accurately represent the product's design, category, and intended use."
        }
    },
    "required": [
        "title",
        "expanded_description",
        "short_description",
        "meta_description",
        "focus_keyphrase"
    ]
}
