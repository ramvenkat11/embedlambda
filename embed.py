import os
import time
from typing import Any

from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

class Embed:
    embedder: TextEmbedding | None = None

    @classmethod
    def init_embedder(cls) -> None:
        # print(TextEmbedding.list_supported_models())
        # if cls.embedder is None:
        #     TextEmbedding.add_custom_model(
        #         model="intfloat/multilingual-e5-large3",
        #         pooling=PoolingType.MEAN,
        #         normalization=True,
        #         dim=1024,
        #         license="mit",
        #         model_file="model.onnx",
        #         additional_files=["model.onnx_data"],
        #         sources=ModelSource(
        #             hf="qdrant/multilingual-e5-large-onnx",
        #             url="https://storage.googleapis.com/qdrant-fastembed/fast-multilingual-e5-large.tar.gz",
        #             _deprecated_tar_struct=True,
        #         )
        #     )
        model_dir = None
        for d in ("/opt/models/fast-multilingual-e5-large", "./models/fast-multilingual-e5-large"):
            if os.path.exists(d):
                model_dir = d
                break
        if model_dir is not None:
            cls.embedder = TextEmbedding(model_name="intfloat/multilingual-e5-large", specific_model_path=model_dir)


    @classmethod
    def get_vectors(cls, texts: list[str]) -> list[list[float]]:
        if cls.embedder is not None:
            embeddings = list(cls.embedder.embed(texts))
            return [e.tolist() for e in embeddings]
        else:
            return []

Embed.init_embedder()


def lambda_handler(event: dict[str, Any], context) -> list[list[float]]:
    return Embed.get_vectors(event.get("texts", []))

