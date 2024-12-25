import openai
import os
import json, time
from django.core.exceptions import ObjectDoesNotExist
from .openai_schema import SCHEMA
import jsonschema
from collections import defaultdict
from django.core.cache import cache
from apps.ai.models import OpenAIAPIUsage
from datetime import datetime

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
        self.api_key, self.prompt = self.load_config()
        self.client = openai.Client(api_key=self.api_key)

    @staticmethod
    def _read_config():
        CONFIG_FILE = "config.json"
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as file:
                raise FileNotFoundError(f"Configuration file not found.")

        with open(CONFIG_FILE, "r") as file:
            return json.load(file)

    def load_config(self):
        """
        Load the API key and prompt from config.json into Django cache if not already present.
        If present in the cache, use the cached values.
        """
        api_key = cache.get('api_key')
        prompt = cache.get('prompt')

        if not api_key or not prompt:
            print("Reading from config file")
            config = self._read_config()
            api_key = config.get('api_key', '')
            prompt = config.get('prompt', '')

            # Save to Django cache
            cache.set('api_key', api_key, timeout=None)  # Cache indefinitely
            cache.set('prompt', prompt, timeout=None)
        else:
            print("Reading from cache")

        return api_key, prompt

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

    def _populate_prompt(self, prompt):
        data = defaultdict(str, {
            "product_title": self.product.title,
            "product_description": self.product.description,
            "category": self.product.category,
            "source_website_name": self.product.source_website.name,
        })
        
        return prompt.format_map(data)


    def _generate_prompt(self):
        """
        Generate the AI prompt based on the quiz data and serialized product information.
        
        :param serialized_products: A list of products with minimal details to include in the prompt.
        :return: The formatted prompt string.
        """
        return self._populate_prompt(self.prompt)
    

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
            start_time = datetime.now()  # Record the start time for response time calculation
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
            end_time = datetime.now()  # Record the end time for response time calculation
            response_time = (end_time - start_time).total_seconds()
            response_content = json.loads(response.choices[0].message.function_call.arguments)
            
            # Create an OpenAIAPIUsage object to log API usage
            openaiusage_object = OpenAIAPIUsage.objects.create(
                endpoint="gpt-4o-mini",  # or extract from the response if dynamic
                total_tokens=response.usage.total_tokens,  # Ensure usage data is included in the response
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                response_time=response_time,
            )
        
            
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
