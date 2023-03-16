import os
from typing import Generator

import openai_async

OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")


def text_to_chunks(
    encoding, text: str, chunk_size: int = 2000, overlap: int = 100
) -> Generator[list[int], None, None]:
    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i : i + chunk_size]
        yield chunk


async def get_pep_text(client, target_pep: str) -> str:
    target = f"https://raw.githubusercontent.com/python/peps/main/{target_pep}.rst"
    res = await client.get(target)
    if res.status_code == 404:
        # fallback
        target = f"https://raw.githubusercontent.com/python/peps/main/{target_pep}.txt"
        res = await client.get(target)
        if res.status_code == 404:
            raise RuntimeError("Not found")
    return res.text


async def send_partial_text(text: str, target_pep: str) -> str:
    prompt_request = f"Summarize this documentation: {text})"
    messages = [
        {"role": "system", "content": f"This is text summarization for {target_pep}"}
    ]
    messages.append({"role": "user", "content": prompt_request})
    response = await openai_async.chat_complete(
        OPEN_AI_API_KEY,
        timeout=60,
        payload={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 1,
        },
    )
    res = response.json()
    return res["choices"][0]["message"]["content"].strip()


async def summarize(pep: str, texts: list[str]) -> str:
    text = "\n".join(texts)
    link = f"https://peps.python.org/{pep}"
    prompt_request = f"Please summarize the text with bullet points: {text}"
    response = await openai_async.complete(
        OPEN_AI_API_KEY,
        timeout=60,
        payload={
            "model": "text-davinci-003",
            "prompt": prompt_request,
            "temperature": 0.3,
            "max_tokens": 150,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 1,
        },
    )
    res = response.json()
    content = res["choices"][0]["text"].strip()
    summary = f"Summary for {pep}:\n{content}\n\nFor more information: {link}"
    return summary
