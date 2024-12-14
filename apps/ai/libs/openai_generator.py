import openai
import os
import json, time
from django.core.exceptions import ObjectDoesNotExist
from .openai_schema import SCHEMA
import jsonschema

class AIGenerator:
    def __init__(self, product):
        """
        Initialize the Roadmap Generator with the attempt ID and schema.
        """
        if not product:
            raise ValueError("product must be set before generating the response.")

        
        self.schema = SCHEMA
        self.product = product
        self.response_content = {}
        self.client = openai.Client(
            api_key=os.environ["api_key"]
        )


    def _validate_response(self, response):
        """
        Validate the AI response against the defined schema.

        :param response: The AI-generated response content as a Python object.
        :return: True if valid, raises ValueError if invalid.
        """
        from jsonschema import validate, ValidationError

        try:
            validate(instance=response, schema=self.schema)
            return True
        except ValidationError as e:
            raise ValueError(f"Invalid AI response: {e.message}")


    def _generate_prompt(self):
        """
        Generate the AI prompt based on the quiz data and serialized product information.
        
        :param serialized_products: A list of products with minimal details to include in the prompt.
        :return: The formatted prompt string.
        """

        prompt = f"""
            Please generate SEO-optimized content for the following 3D printable product model using the provided product details. The goal is to enhance the visibility and appeal of the 3D model on online marketplaces that specialize in 3D models by creating content that is both user-friendly and optimized for search engines.

            **Product Details:**
            - Title: {self.product.title}
            - Description: {self.product.description}
            - Category: {self.product.category}
            - Source Website: {self.product.source_website.name}

            ### Content Requirements:
            1. **SEO-Optimized Title**: 
            - Generate a clear, concise title that summarizes the 3D model's key features, design elements, or intended use in a way that is optimized for search engines. The title should attract users, be keyword-rich, and accurately reflect the 3D model's characteristics.

            2. **Expanded Product Description**: 
            - Write a detailed and engaging description of the 3D model. Highlight its design, intended use (e.g., for 3D printing, prototyping, etc.), technical specifications (such as file types, dimensions, and scale), and any unique selling points. Ensure the description is informative and optimized for SEO, focusing on how the 3D model meets the needs of potential buyers.

            3. **Short Product Description**: 
            - Create a brief and compelling summary that emphasizes the most important features or benefits of the 3D model. This short description should be suitable for quick views or search engine snippets.

            4. **Meta Description**: 
            - Write a short, SEO-focused description (under 255 characters) for search engine result previews. The meta description should include relevant keywords about the 3D model, its applications, and a call-to-action.

            5. **Focus Keyphrase**: 
            - Identify and provide the primary keyword or keyphrase that best represents the 3D model and is likely to drive search traffic. Ensure the keyphrase is relevant to the model’s design, its category (e.g., "3D printed model," "3D printable design"), and intended use.

            ### General Guidelines:
            - Ensure all content is **SEO-optimized** with the proper use of keywords relevant to 3D models and 3D printing.
            - The descriptions should be **engaging**, **clear**, and **informative** to help users understand the value of the 3D model.
            - Focus on **benefits over features** to help users visualize how the 3D model can be used or applied in 3D printing projects or other applications.
            - Use the **product category** and **source website** to inform your SEO strategy and content choices.

            **End Goal:** This optimized content will be used to re-upload the 3D model to online marketplaces and stores, improving its discoverability and increasing the likelihood of conversions from potential buyers.

        """
        return prompt
    

    def _handle_incomplete_response(self, response):
        """
        Handle cases where the AI response does not conform to the schema.

        :param response: The partially valid AI response content.
        :return: A fallback response or default values.
        """
        fallback_response = {
            "title": "Something went wrong.",
            "expanded_description": "Something went wrong.",
            "short_description": "Something went wrong.",
            "meta_description": "Something went wrong.",
            "focus_keyphrase": "Something went wrong."
        }

        # Log details for debugging in production
        print("Invalid or incomplete AI response detected. Returning fallback.")
        return {**fallback_response, **response}


    def generate_ai_response(self):
        """
        Generate the roadmap using OpenAI and validate the response.

        :return: Validated AI response content or fallback content.
        """

        prompt = self._generate_prompt()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in generating SEO rich product copies."},
                    {"role": "user", "content": prompt},
                ],
                functions=[
                    {
                        "name": "generate_seo_rich_product_copy",
                        "description": "Generates a structured detail for given product",
                        "parameters": self.schema,
                    }
                ],
                function_call={"name": "generate_seo_rich_product_copy"},
            )

            response_content = json.loads(response.choices[0].message.function_call.arguments)
            self._validate_response(response_content)
            self.response_content = response_content
            return self.response_content

        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return self._handle_incomplete_response({})  # Pass fallback response in case of validation errors

        except jsonschema.exceptions.ValidationError as e:
            print(f"Validation Error: {e}")
            return self._handle_incomplete_response({}) 

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return self._handle_incomplete_response({})  # Pass fallback response for unexpected errors

    def get_response_content(self):
        """
        Get the validated AI response content.

        :return: AI-generated roadmap content or None if not available.
        """
        if not self.response_content:
            raise ValueError("AI response has not been generated yet.")

        return self.response_content
