import time

from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from philoagents.application.data.extract import get_extraction_generator
from philoagents.domain import prompts
from philoagents.domain.evaluation import EvaluationDataset, EvaluationDatasetSample
from philoagents.domain.philosopher import PhilosopherExtract
from philoagents.settings import settings


class EvaluationDatasetGenerator:
    def __init__(self, temperature: float = 0.8, max_samples: int = 30) -> None:
        self.temperature = temperature
        self.max_samples = max_samples

        self.__chain = self.__build_chain()
        self.__splitter = self.__build_splitter()

    def __call__(self, philosophers: list[PhilosopherExtract]) -> EvaluationDataset:
        dataset_samples = []
        extraction_generator = get_extraction_generator(philosophers)
        for philosopher, doc in extraction_generator:
            chunks = self.__splitter.split_documents([doc])
            for chunk in chunks:
                dataset_sample: EvaluationDatasetSample = self.__chain.invoke(
                    {"philosopher": philosopher, "document": chunk.page_content}
                )
                dataset_sample.philosopher_id = philosopher.id

                if self.__validate_sample(dataset_sample):
                    dataset_samples.append(dataset_sample)

                time.sleep(1)  # To avoid rate limiting

                if len(dataset_samples) >= self.max_samples:
                    break

            if len(dataset_samples) >= self.max_samples:
                    logger.warning(
                        f"Reached maximum number of samples ({self.max_samples}). Stopping."
                    )

                    break

        logger.info(f"Generated {len(dataset_samples)} evaluation sample(s).")
        logger.info(f"Saving to '{settings.EVALUATION_DATASET_FILE_PATH}'")

        evaluation_dataset = EvaluationDataset(samples=dataset_samples)
        evaluation_dataset.save_to_json(file_path=settings.EVALUATION_DATASET_FILE_PATH)

        return evaluation_dataset

    def __build_chain(self):
        model = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_LLM_MODEL,
            temperature=self.temperature,
        )
        model = model.with_structured_output(EvaluationDatasetSample)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompts.EVALUATION_DATASET_GENERATION_PROMPT),
            ],
            template_format="jinja2",
        )

        return prompt | model

    def __build_splitter(
        self, max_token_limit: int = 6000
    ) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=int(max_token_limit * 0.25),
            chunk_overlap=0,
        )

    def __validate_sample(self, sample: EvaluationDatasetSample) -> bool:
        return (
            len(sample.messages) >= 2
            and sample.messages[0].role == "user"
            and sample.messages[1].role == "assistant"
        )
