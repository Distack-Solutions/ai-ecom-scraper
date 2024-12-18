import requests
import json

# GraphQL endpoint
url = "https://api.printables.com/graphql/"

# query
QUERY = """
query SearchModels(
  $query: String!,
  $limit: Int,
  $cursor: Int,
  $categoryId: ID,
  $materialIds: [Int],
  $printerIds: [Int],
  $featured: Boolean,
  $printDuration: IntervalObject,
  $weight: IntervalObject,
  $nozzleDiameters: [Float],
  $filesType: [FilterPrintFilesTypeEnum],
  $usedMaterial: IntervalObject,
  $licenses: [ID],
  $hasMake: Boolean,
  $publishedDateLimitDays: Int,
  $competitionAwarded: Boolean,
  $exclusiveFromClubs: Boolean,
  $paid: PaidEnum,
  $downloadable: Boolean,
  $price: IntervalObject,
  $ordering: SearchChoicesEnum
) {
  result: searchPrints2(
    query: $query
    printType: print
    limit: $limit
    offset: $cursor
    categoryId: $categoryId
    materialIds: $materialIds
    printerIds: $printerIds
    featured: $featured
    printDuration: $printDuration
    weight: $weight
    nozzleDiameters: $nozzleDiameters
    filesType: $filesType
    usedMaterial: $usedMaterial
    licenses: $licenses
    hasMake: $hasMake
    publishedDateLimitDays: $publishedDateLimitDays
    competitionAwarded: $competitionAwarded
    exclusiveFromClubs: $exclusiveFromClubs
    downloadablePremium: $downloadable
    paid: $paid
    price: $price
    ordering: $ordering
  ) {
    items {
      ...Model
      __typename
    }
    __typename
  }
}

fragment Model on PrintType {
  id
  name
  slug
  description
  ratingAvg
  likesCount
  liked
  datePublished
  dateFeatured
  firstPublish
  downloadCount
  mmu
  category {
    id
    path {
      id
      name
      nameEn
      __typename
    }
    __typename
  }
  modified
  image {
    ...SimpleImage
    __typename
  }
  images {
    ...SimpleImage
    __typename
  }
  nsfw
  club: premium
  price
  user {
    ...AvatarUser
    __typename
  }
  ...LatestContestResult
  previewFile {
    ...PreviewFile
    __typename
  }
  license {
    id
    name
    abbreviation
    content
    disallowRemixing
    freeModels
    storeModels
    allowedLicensesAfterRemixing {
      id
      __typename
    }
    __typename
  }
  __typename
}

fragment PreviewFile on PreviewFileUnionType {
  ... on STLType {
    id
    filePreviewPath
    __typename
  }
  ... on SLAType {
    id
    filePreviewPath
    __typename
  }
  ... on GCodeType {
    id
    filePreviewPath
    __typename
  }
  __typename
}

fragment AvatarUser on UserType {
  id
  handle
  verified
  dateVerified
  publicUsername
  avatarFilePath
  badgesProfileLevel {
    profileLevel
    __typename
  }
  __typename
}

fragment LatestContestResult on PrintType {
  latestContestResult: latestCompetitionResult {
    ranking: placement
    competitionId
    __typename
  }
  __typename
}

fragment SimpleImage on PrintImageType {
  id
  filePath
  rotation
  imageHash
  imageWidth
  imageHeight
  __typename
}

        """


MAIN_QUERY = """
query SearchModels(
  $query: String!,
  $limit: Int,
  $cursor: Int,
  $categoryId: ID,
  $licenses: [ID],
  $ordering: SearchChoicesEnum
) {
  result: searchPrints2(
    query: $query
    printType: print
    limit: $limit
    offset: $cursor
    categoryId: $categoryId
    licenses: $licenses
    ordering: $ordering
  ) {
    items {
      id
      name
      description
      pdfFilePath
      category {
        id
        name
        nameEn
        __typename
      }
      license {
        id
        name
        abbreviation
        content
        disallowRemixing
        freeModels
        storeModels
        __typename
      }
      image {
        filePath
        __typename
      }
      images {
        id
        filePath
        __typename
      }
      previewFile {
        ...PreviewFile
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment PreviewFile on PreviewFileUnionType {
  ... on STLType {
    id
    filePreviewPath
    __typename
  }
  ... on SLAType {
    id
    filePreviewPath
    __typename
  }
  ... on GCodeType {
    id
    filePreviewPath
    __typename
  }
  __typename
}

"""

# HTTP headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ),
    "Content-Type": "application/json",
    "Cookie": (
        "Cookie_1=value; Cookie_2=value; Cookie_3=value; "
        "csrftoken=E7hV5lTXu67DdQploe0KTGkMEpZL68vw"
    ),
}


class PrintablesProductScrap:
    def __init__(self, query: str, limit: int):
        self.query = query
        self.limit = limit
        self.media_url = "https://media.printables.com/"
        self.results = []
        self.key = "printable"

    def __hit_query(self):
        # GraphQL query payload
        payload = json.dumps(
            {
                "query": MAIN_QUERY,
                "variables": {
                    "categoryId": None,
                    "competitionAwarded": False,
                    "cursor": 0,
                    "featured": False,
                    "hasMake": False,
                    "limit": self.limit,
                    "ordering": "best_match",
                    "publishedDateLimitDays": None,
                    "query": self.query,
                },
            }
        )

        # Make the POST request
        response = requests.post(url, headers=HEADERS, data=payload)

        # Parse and print the response
        data = response.json().get("data")
        if not data:
            raise Exception("Something went wrong.")

        if data.get("result") and data.get("result").get("items"):
            self.results = data.get("result").get("items")
        else:
            raise Exception("No results for this query.")

    def get_products(self):
        self.__hit_query()
        return self.results

    def get_thumnail(self, product):
        thumbnail = product.get("image")
        if not thumbnail:
            return None
        return self.get_image_path(thumbnail)

    def get_gallery_images(self, product):
        gallery_images = []
        images = product.get("images")
        if images:
            for image in images:
                gallery_image = self.get_image_path(image)
                if gallery_image:
                    gallery_images.append(gallery_image)

        return gallery_images

    def get_image_path(self, imageObject):
        if not imageObject:
            return None

        imagePath = imageObject.get("filePath")

        if not imagePath:
            return None

        return f"{self.media_url}{imagePath}"

    def get_media_url(self, uri):
        if uri:
            return f"{self.media_url}{uri}"

        raise Exception("URI required")

    def add_media_domain(self):
        for product in self.results:
            if product.get("image"):
                existingImageFilePath = product["image"]["filePath"]
                product["image"]["filePath"] = f"{self.media_url}{existingImageFilePath}"

            if product.get("images"):
                for gallery_image in product["images"]:
                    existingImageFilePath = gallery_image["filePath"]
                    gallery_image["filePath"] = f"{self.media_url}{existingImageFilePath}"

    def save_file(self):
        with open("data.json", "w") as f:
            json.dump(self.results, f, indent=4)

    def to_model_data(self):
        """
        Convert scraped data into structured format for model creation.

        Returns:
            list[dict]: A list of dictionaries representing product data.
        """
        structured_data = []
        for product in self.results:
            try:
                # Extract category name
                category = product.get("category", {}).get("name")

                # Extract license details
                license_data = product.get("license")

                # Construct the product data
                product_data = {
                    "sku": f'{self.key}-{product.get("id")}',
                    "title": product.get("name"),
                    "description": product.get("description") or "No description available",
                    "category": category,
                    "thumbnail_url": self.get_thumnail(product),
                    "images": self.get_gallery_images(product),
                    "license": license_data,
                    "pdf_file_url": self.get_media_url(product.get("pdfFilePath"))
                    if product.get("pdfFilePath")
                    else None,
                }

                structured_data.append(product_data)
            except Exception as e:
                print(f"Error processing product {product.get('id')}: {e}")
                continue

        return structured_data


if __name__ == "__main__":
    x = PrintablesProductScrap("apple", 10)
    x.get_products()
    products = x.to_model_data()
    print(products)
    x.save_file()