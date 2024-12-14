SCHEMA = {
    "type": "object",
    "description": "This schema is used to generate SEO-optimized content for a 3D printable product model. Based on the provided product information (title, description, category, and source website) of a 3D model, the AI will regenerate SEO-focused content including a title, expanded description, short description, meta description, and focus keyphrase. This process is designed to ensure that 3D model listings are optimized for search engines to maximize visibility and appeal to potential buyers on online marketplaces that specialize in 3D models.",
    "properties": {
        "title": {
            "type": "string",
            "description": "The AI-generated title for the 3D model, summarizing the model's key features, design elements, or use cases in a concise, SEO-optimized manner. The title should highlight the main attributes of the 3D model, ensuring it captures both user attention and search engine relevance for 3D model buyers."
        },
        "expanded_description": {
            "type": "string",
            "description": "A detailed and informative description of the 3D model. This field provides in-depth information about the model’s design, intended use, technical specifications (e.g., file types, dimensions, scale, etc.), and its suitability for various 3D printing applications. The description should also highlight any unique features that set this model apart from others in the marketplace, while being optimized for SEO to help the listing rank higher on search engines."
        },
        "short_description": {
            "type": "string",
            "description": "A concise summary of the 3D model, focusing on its key features or unique selling points. This short description is ideal for quick reference by users browsing search results or product listings on online platforms, emphasizing the most compelling aspects of the model."
        },
        "meta_description": {
            "type": "string",
            "description": "A brief, SEO-focused description (under 255 characters) of the 3D model, designed to appear in search engine result previews. The meta description should contain key information about the model, its uses, and a call-to-action to encourage users to click through to the product page. The description should be highly relevant to search queries related to 3D models and printing."
        },
        "focus_keyphrase": {
            "type": "string",
            "description": "The main keyword or keyphrase for the 3D model, used to optimize its SEO performance. This keyphrase should be a term that prospective buyers are likely to search for when looking for 3D models like this one. It should accurately represent the model's design, category, and intended use for 3D printing."
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
