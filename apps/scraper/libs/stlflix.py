import requests
import json
from datetime import datetime

# GraphQL endpoint
url = "https://k8s.stlflix.com/graphql"

QUERY = """
query GET_PRODUCTS($filters: ProductFiltersInput, $productsPage: Int, $productsPageSize: Int, $sort: [String]) {
  products(
    filters: $filters
    pagination: { page: $productsPage, pageSize: $productsPageSize }
    sort: $sort
  ) {
    data {
      id
      attributes {
        name
        slug
        description
        iframe
        updatedAt
        release_date
        technical_overview_url
        assemble_tutorial_url
        change_log
        bambu_file {
          data {
            id
            __typename
          }
          __typename
        }
        stl_file {
          data {
            id
            __typename
          }
          __typename
        }
        prusa_file
        stl_preview {
          ...mediaData
          __typename
        }
        thumbnail {
          ...mediaData
          __typename
        }
        hover {
          ...mediaData
          __typename
        }
        gallery(pagination: {pageSize: 50}) {
          data {
            id
            attributes {
              alternativeText
              url
              __typename
            }
            __typename
          }
          __typename
        }
        keywords
        files(pagination: {pageSize: 50}) {
          text
          commercial_only
          file {
            data {
              id
              __typename
            }
            __typename
          }
          __typename
        }
        filaments {
          data {
            attributes {
              url_pt_br
              name_pt_br
              price_pt_br
              store_id_pt_br
              hex_color
              thumbnail_url
              __typename
            }
            __typename
          }
          __typename
        }
        parent_categories {
          data {
            id
            attributes {
              slug
              name
              __typename
            }
            __typename
          }
          __typename
        }
        sub_categories {
          data {
            id
            attributes {
              slug
              name
              __typename
            }
            __typename
          }
          __typename
        }
        categories {
          data {
            id
            attributes {
              name
              slug
              __typename
            }
            __typename
          }
          __typename
        }
        tags {
          data {
            attributes {
              name
              parent_tag {
                data {
                  attributes {
                    name
                    __typename
                  }
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        original {
          data {
            id
            attributes {
              slug
              name
              __typename
            }
            __typename
          }
          __typename
        }
        modified_items {
          data {
            id
            attributes {
              name
              slug
              thumbnail {
                ...mediaData
                __typename
              }
              hover {
                ...mediaData
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        drop {
          data {
            id
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    meta {
      pagination {
        page
        pageSize
        pageCount
        total
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment mediaData on UploadFileEntityResponse {
  data {
    attributes {
      alternativeText
      url
      __typename
    }
    __typename
  }
  __typename
}
"""

HEADERS = {"Content-Type": "application/json"}


class StlflixProductScrap:
    def __init__(self, query: str, limit: int):
        self.query = query
        self.limit = limit
        self.results = []
        self.key = "stlflix"

    def _apply_limit(self):
        self.results = self.results[:self.limit]

    def __hit_query(self):
        payload = json.dumps(
            {
                "query": QUERY,
                "variables": {
                    "filters": {
                        "or": [
                            {"keywords": {"containsi": self.query}},
                            {"slug": {"containsi": self.query}},
                            {"name": {"containsi": self.query}},
                            {"tags": {"slug": {"containsi": self.query}}},
                            {"categories": {"slug": {"containsi": self.query}}},
                        ],
                        "release_date": {
                            "lte": datetime.utcnow().isoformat() + "Z"
                        },
                    },
                    "productsPage": 1,
                    "productsPageSize": self.limit,
                    "sort": "release_date:DESC",
                },
            }
        )

        response = requests.post(url, headers=HEADERS, data=payload)
        data = response.json().get("data")
        if data and data.get("products"):
            self.results = data.get("products").get("data")

    def get_products(self):
        self.__hit_query()
        self._apply_limit()
        return self.results

    def save_file(self, is_to_model=True):
        modeled_data = self.results
        if is_to_model:
            modeled_data = self.to_model_data()       
        with open("data.json", "w") as f:
            json.dump(modeled_data, f, indent=4)

    def to_model_data(self):
        """
        Convert raw GraphQL product data into a structured format suitable for
        creating `Product`, `ThumbnailImage`, and `Image` instances.

        Returns a list of dictionaries, each containing product data:
        {
            'sku': str or None,
            'title': str or None,
            'description': str or None,
            'category': comma-separated string or None,
            'thumbnail_url': str or None,
            'images': list of image URLs,
            'is_commercial_allowed': bool
        }
        """
        products_model_data = []
        for product in self.results:
            attr = product.get("attributes", {})

            # Basic product details
            title = attr.get('name')
            description = attr.get('description')
            slug = attr.get('slug')  # We'll use slug as a unique identifier if needed
            
            # Thumbnail
            thumbnail_url = None
            thumbnail_data = attr.get('thumbnail', {}).get('data')
            if thumbnail_data and thumbnail_data.get('attributes'):
                thumbnail_url = thumbnail_data['attributes'].get('url')

            # Categories (combine parent_categories, sub_categories, categories)
            categories = []
            # Normal categories
            cat_data = attr.get('categories', {}).get('data', [])
            for c in cat_data:
                if c.get('attributes'):
                    categories.append(c['attributes'].get('name'))
            # Parent categories
            parent_categories = attr.get('parent_categories', {})
            parent_cat_data = []
            if parent_categories:
              parent_cat_data = parent_categories.get('data', [])
            
            for pc in parent_cat_data:
                if pc and pc.get('attributes'):
                    categories.append(pc['attributes'].get('name'))

            # Sub categories
            sub_categories = attr.get('sub_categories', {})
            sub_cat_data = []

            if sub_categories:
              sub_cat_data = sub_categories.get('data', [])

            for sc in sub_cat_data:
                if sc and sc.get('attributes'):
                    categories.append(sc['attributes'].get('name'))

            category_str = ",".join(filter(None, categories)) if categories else ""

            # Gallery images
            images = []
            gallery_data = attr.get('gallery', {}).get('data', [])
            for g in gallery_data:
                if g.get('attributes'):
                    img_url = g['attributes'].get('url')
                    if img_url:
                        images.append(img_url)

            # Determine if commercial use is allowed
            # We'll set `is_commercial_allowed=True` if we find at least one file with commercial_only=False
            is_commercial_allowed = False
            files = attr.get('files', [])
            for f in files:
                if f.get('commercial_only') is False:
                    is_commercial_allowed = True
                    break

            # Build a dictionary that aligns with your Product model fields
            product_data = {
                'sku': f'{self.key}-{slug}',  
                'title': title or None,
                'description': description or None,
                'category': category_str,  # comma-separated categories or None
                'thumbnail_url': thumbnail_url,  # This can be used to create a ThumbnailImage object later
                'images': images,  # List of URLs for Image model creation
                'is_commercial_allowed': is_commercial_allowed,
            }

            products_model_data.append(product_data)

        return products_model_data


if __name__ == "__main__":
    x = StlflixProductScrap('apple', 5)
    x.get_products()
    x.save_file(False)

