SCHEMA = {
    "type": "object",
    "description": (
        "This schema generates SEO-optimized content for a finished product. All content must describe the product "
        "as a ready-to-use item. STRICTLY avoid terms like '3D models,' 'printables,' 'files,' 'downloads,' or 'STL.'"
    ),
    "properties": {
        "title": {
            "type": "string",
            "description": (
                "SEO-optimized product title (40-60 characters). Must exclude terms like '3D models,' 'printables,' "
                "'files,' 'downloads,' or 'STL.'"
            )
        },
        "expanded_description": {
            "type": "string",
            "description": (
                "Detailed product description (300+ words). Highlight features, uses, and benefits of the finished product. Don't include HTML tags, it must be simple text."
                "Strictly avoid terms like '3D models,' 'printables,' 'files,' 'downloads,' or 'STL.'"
            )
        },
        "short_description": {
            "type": "string",
            "description": (
                "Concise summary of product features (WooCommerce-ready). Avoid terms like '3D models,' 'printables,' "
                "'files,' 'downloads,' or 'STL.'"
            )
        },
        "meta_description": {
            "type": "string",
            "description": (
                "SEO-friendly meta description (120-160 characters). Exclude terms like '3D models,' 'printables,' "
                "'files,' 'downloads,' or 'STL.'"
            )
        },
        "focus_keyphrase": {
            "type": "string",
            "description": (
                "Main keyword for the product. Avoid terms like '3D models,' 'printables,' 'files,' 'downloads,' or 'STL.'"
            )
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
