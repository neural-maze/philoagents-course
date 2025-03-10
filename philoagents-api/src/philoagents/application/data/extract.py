from typing import Generator

from langchain_community.document_loaders import WebBaseLoader, WikipediaLoader
from langchain_core.documents import Document
from tqdm import tqdm

from philoagents.domain.philosopher import Philosopher, PhilosopherExtract
from philoagents.domain.philosopher_factory import PhilosopherFactory


def get_extraction_generator(
    philosophers: list[PhilosopherExtract],
) -> Generator[tuple[Philosopher, list[Document]], None, None]:
    """Extract documents for a list of philosophers, yielding one at a time.

    Args:
        philosophers: A list of PhilosopherExtract objects containing philosopher information.

    Yields:
        tuple[Philosopher, list[Document]]: A tuple containing the philosopher object and a list of
            documents extracted for that philosopher.
    """

    progress_bar = tqdm(
        philosophers,
        desc="Extracting docs",
        unit="philosopher",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        ncols=100,
        position=0,
        leave=True,
    )

    philosophers_factory = PhilosopherFactory()
    for philosopher_extract in progress_bar:
        philosopher = philosophers_factory.get_philosopher(philosopher_extract.id)
        progress_bar.set_postfix_str(f"Philosopher: {philosopher.name}")

        philosopher_docs = extract(philosopher, philosopher_extract.urls)

        yield (philosopher, philosopher_docs)


def extract(philosopher: Philosopher, extract_urls: list[str]) -> list[Document]:
    """Extract documents for a single philosopher from all sources and deduplicate them.

    Args:
        philosopher: Philosopher object containing philosopher information.
        extract_urls: List of URLs to extract content from.

    Returns:
        list[Document]: List of deduplicated documents extracted for the philosopher.
    """

    docs = []

    docs.extend(extract_wikipedia(philosopher))
    docs.extend(extract_stanford_encyclopedia_of_philosophy(philosopher, extract_urls))

    return docs


def extract_wikipedia(philosopher: Philosopher) -> list[Document]:
    """Extract documents for a single philosopher from Wikipedia.

    Args:
        philosopher: Philosopher object containing philosopher information.

    Returns:
        list[Document]: List of documents extracted from Wikipedia for the philosopher.
    """

    loader = WikipediaLoader(
        query=philosopher.name,
        lang="en",
        load_max_docs=1,
        doc_content_chars_max=1000000,
    )
    docs = loader.load()

    for doc in docs:
        doc.metadata["philosopher_id"] = philosopher.id
        doc.metadata["philosopher_name"] = philosopher.name

    return docs


def extract_stanford_encyclopedia_of_philosophy(
    philosopher: Philosopher, urls: list[str]
) -> list[Document]:
    """Extract documents for a single philosopher from Stanford Encyclopedia of Philosophy.

    Args:
        philosopher: Philosopher object containing philosopher information.
        urls: List of URLs to extract content from.

    Returns:
        list[Document]: List of documents extracted from Stanford Encyclopedia for the philosopher.
    """

    def extract_paragraphs_and_headers(soup) -> str:
        # List of class/id names specific to the Stanford Encyclopedia of Philosophy that we want to exclude.
        excluded_sections = [
            "bibliography",
            "academic-tools",
            "other-internet-resources",
            "related-entries",
            "acknowledgments",
            "article-copyright",
            "article-banner",
            "footer",
        ]

        # Find and remove elements within excluded sections
        for section_name in excluded_sections:
            for section in soup.find_all(id=section_name):
                section.decompose()

            for section in soup.find_all(class_=section_name):
                section.decompose()

            for section in soup.find_all(
                lambda tag: tag.has_attr("id") and section_name in tag["id"].lower()
            ):
                section.decompose()

            for section in soup.find_all(
                lambda tag: tag.has_attr("class")
                and any(section_name in cls.lower() for cls in tag["class"])
            ):
                section.decompose()

        # Extract remaining paragraphs and headers
        content = []
        for element in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
            content.append(element.get_text())

        return "\n\n".join(content)

    if len(urls) == 0:
        return []

    loader = WebBaseLoader(show_progress=False)
    soups = loader.scrape_all(urls)

    documents = []
    for url, soup in zip(urls, soups):
        text = extract_paragraphs_and_headers(soup)
        metadata = {
            "source": url,
            "philosopher_id": philosopher.id,
            "philosopher_name": philosopher.name,
        }

        if title := soup.find("title"):
            metadata["title"] = title.get_text().strip(" \n")

        documents.append(Document(page_content=text, metadata=metadata))

    return documents


if __name__ == "__main__":
    aristotle = PhilosopherFactory().get_philosopher("aristotle")
    docs = extract_stanford_encyclopedia_of_philosophy(
        aristotle,
        [
            "https://plato.stanford.edu/entries/aristotle/",
            "https://plato.stanford.edu/entries/aristotle/",
        ],
    )
    print(docs)
