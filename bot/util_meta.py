import httpx


async def get_gh_discuss(issue_number: int) -> str:
    def extract_content(res: dict) -> str:
        user = res["user"]["login"]
        body = res["body"]
        return f"{user} said '{body}'"

    async with httpx.AsyncClient() as client:
        root_target = (
            f"https://api.github.com/repos/python/cpython/issues/{issue_number}"
        )
        comment_target = f"https://api.github.com/repos/python/cpython/issues/{issue_number}/comments"
        root = await client.get(root_target)
        root = root.json()
        texts = []
        text = extract_content(root)
        texts.append(text)
        comments = await client.get(comment_target)
        comments = comments.json()
        for comment in comments:
            text = extract_content(comment)
            texts.append(text)

        return "\n\n".join(texts)


async def get_pep_text(target_pep: str) -> str:
    async with httpx.AsyncClient() as client:
        target = f"https://raw.githubusercontent.com/python/peps/main/{target_pep}.rst"
        res = await client.get(target)
        if res.status_code != 200:
            # fallback
            target = (
                f"https://raw.githubusercontent.com/python/peps/main/{target_pep}.txt"
            )
            res = await client.get(target)
            if res.status_code != 200:
                raise RuntimeError("Not found")
        return res.text
