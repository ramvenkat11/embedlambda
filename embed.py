from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

class Embed:
    embedder: TextEmbedding | None = None

    @classmethod
    def init_embedder(cls) -> None:
        if cls.embedder is None:
            TextEmbedding.add_custom_model(
                model="e5-base",
                pooling=PoolingType.MEAN,
                normalization=True,
                dim=768,
                sources=ModelSource(hf="intfloat/multilingual-e5-base")
            )
        cls.embedder = TextEmbedding(model_name="e5-base")

    @classmethod
    def get_vector(cls, text: str) -> list[float]:
        embeddings = list(cls.embedder.embed([text]))
        return embeddings[0].tolist()

    @classmethod
    def get_vectors(cls, texts: list[str]) -> list[list[float]]:
        embeddings = list(cls.embedder.embed(texts))
        return [e.tolist() for e in embeddings]

Embed.init_embedder()
_ = Embed.get_vector("hello")
