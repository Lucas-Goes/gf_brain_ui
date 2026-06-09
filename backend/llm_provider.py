import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt, temperature=0.0, max_tokens=500, system_prompt=""):
        ...


class OpenAIProvider(LLMProvider):

    def __init__(self, api_key, base_url, model):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0, max_retries=1)
        self.model = model

    def generate(self, prompt, temperature=0.0, max_tokens=500, system_prompt=""):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class BedrockProvider(LLMProvider):

    def __init__(self, profile_name, region, model_id):
        import boto3
        session = boto3.Session(profile_name=profile_name)
        self.client = session.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    def generate(self, prompt, temperature=0.0, max_tokens=500, system_prompt=""):
        system = [{"text": system_prompt}] if system_prompt else []

        response = self.client.converse(
            modelId=self.model_id,
            system=system,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        )
        return response["output"]["message"]["content"][0]["text"]


def create_provider(config):
    provider_name = config.get("LLM_PROVIDER", "openai")

    if provider_name == "bedrock":
        ca_bundle = config.get("AWS_CA_BUNDLE")
        if ca_bundle:
            os.environ["AWS_CA_BUNDLE"] = ca_bundle

        http_proxy = config.get("HTTP_PROXY")
        if http_proxy:
            os.environ["HTTP_PROXY"] = http_proxy

        https_proxy = config.get("HTTPS_PROXY")
        if https_proxy:
            os.environ["HTTPS_PROXY"] = https_proxy

        return BedrockProvider(
            profile_name=config["AWS_PROFILE"],
            region=config["AWS_REGION"],
            model_id=config["BEDROCK_MODEL_ID"],
        )

    return OpenAIProvider(
        api_key=config["NVIDIA_API_KEY"],
        base_url=config["LLM_BASE_URL"],
        model=config["LLM_MODEL"],
    )
