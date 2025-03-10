from pathlib import Path

import click
from loguru import logger

from philoagents.application.evaluation import EvaluationDatasetGenerator
from philoagents.config import settings
from philoagents.domain.philosopher import PhilosopherExtract


@click.command()
@click.option(
    "--metadata-file",
    type=click.Path(exists=True, path_type=Path),
    default=settings.EXTRACTION_METADATA_FILE_PATH,
    help="Path to the metadata file containing philosopher extracts",
)
@click.option(
    "--temperature",
    type=float,
    default=0.9,
    help="Temperature parameter for generation",
)
@click.option(
    "--max-samples",
    type=int,
    default=40,
    help="Maximum number of samples to generate",
)
def main(metadata_file: Path, temperature: float, max_samples: int) -> None:
    """
    Generate an evaluation dataset from philosopher extracts.

    Args:
        metadata_file: Path to the metadata file containing philosopher extracts
        temperature: Temperature parameter for generation
        max_samples: Maximum number of samples to generate
    """
    philosophers = PhilosopherExtract.from_json(metadata_file)

    logger.info(
        f"Generating evaluation dataset with temperature {temperature} and {max_samples} samples."
    )
    logger.info(f"Total philosophers: {len(philosophers)}")

    evaluation_dataset_generator = EvaluationDatasetGenerator(
        temperature=temperature, max_samples=max_samples
    )
    evaluation_dataset_generator(philosophers)


if __name__ == "__main__":
    main()
