import time

from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

class Embed:
    embedder: TextEmbedding | None = None

    @classmethod
    def init_embedder(cls) -> None:
        # print(TextEmbedding.list_supported_models())
        # os.environ["FASTEMBED_CACHE_PATH"] = Path("./models")
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
        cls.embedder = TextEmbedding(model_name="intfloat/multilingual-e5-large", specific_model_path="./models/fast-multilingual-e5-large")

    @classmethod
    def get_vector(cls, text: str) -> list[float]:
        embeddings = list(cls.embedder.embed([text]))
        return embeddings[0].tolist()

    @classmethod
    def get_vectors(cls, texts: list[str]) -> list[list[float]]:
        embeddings = list(cls.embedder.embed(texts))
        return [e.tolist() for e in embeddings]

Embed.init_embedder()

if __name__ == "__main__":
    s = time.time_ns()
    v = Embed.get_vectors(["hello"])
    print(len(v[0]))
    print((time.time_ns() - s) / 1_000_000)
    # print(Embed.get_vector("hello"))