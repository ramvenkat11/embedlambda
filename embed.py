import os
from typing import Any
import time

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
        start = time.time_ns()
        mem1 = _rss_bytes_linux_procfs()
        for e in cls.embedder.embed(texts[:-1]):
            out.append(e.tolist())
        after_most = (time.time_ns() - start) // 1_000_000
        mem_questions = _rss_bytes_linux_procfs()
        for e in cls.embedder.embed(texts[-1:]):
            out.append(e.tolist())
        after_all = (time.time_ns() - start) // 1_000_000
        mem2 = _rss_bytes_linux_procfs()
        print(f"Memory:  before: {mem1},  questions: {mem_questions}, after: {mem2};  Time: After questions: {after_most} ms, After all: {after_all} ms")
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
    print(f"Number of texts: {len(texts)}, Memory before: {_rss_bytes_linux_procfs()}, Length of last text: {len(texts[-1])}")
    vectors = Embed.get_vectors(texts)
    return vectors

