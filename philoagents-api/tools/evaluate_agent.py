from pathlib import Path

import click

from philoagents.application.evaluation import evaluate_agent, upload_dataset
from philoagents.config import settings


@click.command()
@click.option(
    "--name", default="philoagents_evaluation_dataset", help="Name of the dataset"
)
@click.option(
    "--data-path",
    type=click.Path(exists=True, path_type=Path),
    default=settings.EVALUATION_DATASET_FILE_PATH,
    help="Path to the dataset file",
)
@click.option("--workers", default=1, type=int, help="Number of workers")
@click.option(
    "--nb-samples", default=20, type=int, help="Number of samples to evaluate"
)
def main(name: str, data_path: Path, workers: int, nb_samples: int) -> None:
    """
    Evaluate an agent on a dataset.

    Args:
        name: Name of the dataset
        data_path: Path to the dataset file
        workers: Number of workers to use for evaluation
        nb_samples: Number of samples to evaluate
    """

    dataset = upload_dataset(name=name, data_path=data_path)
    evaluate_agent(dataset, workers=workers, nb_samples=nb_samples)


if __name__ == "__main__":
    main()
