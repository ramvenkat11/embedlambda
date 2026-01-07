import os
from typing import Any
from fastembed import TextEmbedding


class Embed:
    embedder: TextEmbedding | None = None

    @classmethod
    def init_embedder(cls) -> None:
        model_dir = None
        for d in ("/opt/models/fast-multilingual-e5-large", "./models/fast-multilingual-e5-large"):
            if os.path.exists(d):
                model_dir = d
                break
        if model_dir is not None:
            cls.embedder = TextEmbedding(model_name="intfloat/multilingual-e5-large", specific_model_path=model_dir)

    @classmethod
    def get_vectors(cls, texts: list[str]) -> list[list[float]]:
        if cls.embedder is None:
            return []
        out: list[list[float]] = []
        i = 0
        for e in cls.embedder.embed(texts[:-1]):
            out.append(e.tolist())
            # print(f"{i + 1}: text: {texts[i]}, Memory: {_rss_bytes_linux_procfs()}")
            i += 1
        print(f"Memory after questions: {_rss_bytes_linux_procfs()}")
        for e in cls.embedder.embed(texts[-1:]):
            out.append(e.tolist())
        # print(f"text: Whole passage, Memory: {_rss_bytes_linux_procfs()}")
        return out


def _rss_bytes_linux_procfs() -> str:
    with open("/proc/self/statm", "r", encoding="utf-8") as f:
        resident_pages = int(f.read().split()[1])
    page_size = os.sysconf("SC_PAGE_SIZE")
    b = resident_pages * page_size
    return f"{b / (1024 * 1024):,.1f} MB"

Embed.init_embedder()

def lambda_handler(event: dict[str, Any], context) -> list[list[float]]:
    texts = event.get("texts", [])
    print(f"Number of texts: {len(texts)}, Memory before: {_rss_bytes_linux_procfs()}")
    vectors = Embed.get_vectors(texts)
    print(f"Memory before returning: {_rss_bytes_linux_procfs()}")
    return vectors

