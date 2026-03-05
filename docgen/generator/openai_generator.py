import os
import json
from openai import AsyncOpenAI
from typing import List

from docgen.scanner.base import UndocumentedItem, GeneratedDoc
from docgen.generator.templates import get_prompt

class OpenAIGenerator:
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_docstring(self, item: UndocumentedItem, format: str, model: str) -> GeneratedDoc:
        prompt = get_prompt(item, format)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior developer writing docstrings. Infer param types from usage and naming. Keep descriptions concise (1-2 lines per param). Do not hallucinate behavior not present in source. Return ONLY raw docstring text (no quotes, no fences) and a confidence score in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        raw = response.choices[0].message.content
        try:
            data = json.loads(raw)
            docstring = data.get("docstring", "")
            confidence = data.get("confidence", 1.0)
        except Exception:
            docstring = raw
            confidence = 0.5
            
        return GeneratedDoc(
            item=item,
            docstring=docstring.strip(),
            format=format,
            confidence=confidence
        )
