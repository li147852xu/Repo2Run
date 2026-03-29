# Copyright (2025) Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from typing import Any, Dict, List, Optional, Tuple

from utils.llm_providers import (
    ProviderName,
    chat_anthropic,
    chat_openai_compatible,
)


def get_llm_response(
    model: str,
    messages: List[Dict[str, Any]],
    llm_provider: ProviderName = "openai_compatible",
    temperature: float = 0.0,
    n: int = 1,
    max_tokens: int = 4096,
) -> Tuple[List[Optional[str]], Optional[Dict[str, int]]]:
    """
    Call the configured LLM backend. Returns (list of choice texts, usage dict).

    usage dict always includes total_tokens when present (for token accounting).
    """
    max_retry = 5
    count = 0
    while count < max_retry:
        try:
            if llm_provider == "anthropic":
                return chat_anthropic(
                    model, messages, temperature=temperature, n=n, max_tokens=max_tokens
                )
            return chat_openai_compatible(
                model, messages, temperature=temperature, n=n, max_tokens=max_tokens
            )
        except Exception as e:
            print(f"Error: {e}")
            count += 1
            time.sleep(3)
    return [None], None
