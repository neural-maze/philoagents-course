from langchain_huggingface import HuggingFaceEmbeddings

EmbeddingsModel = HuggingFaceEmbeddings


def get_embedding_model(
    model_id: str,
    device: str = "cpu",
) -> EmbeddingsModel:
    """Gets an instance of a HuggingFace embedding model.

    Args:
        model_id (str): The ID/name of the HuggingFace embedding model to use
        device (str): The compute device to run the model on (e.g. "cpu", "cuda").
            Defaults to "cpu"

    Returns:
        EmbeddingsModel: A configured HuggingFace embeddings model instance
    """
    return get_huggingface_embedding_model(model_id, device)


def get_huggingface_embedding_model(
    model_id: str, device: str
) -> HuggingFaceEmbeddings:
    """Gets a HuggingFace embedding model instance.

    Args:
        model_id (str): The ID/name of the HuggingFace embedding model to use
        device (str): The compute device to run the model on (e.g. "cpu", "cuda")

    Returns:
        HuggingFaceEmbeddings: A configured HuggingFace embeddings model instance
            with remote code trust enabled and embedding normalization disabled
    """
    return HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs={"device": device, "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": False},
    )
