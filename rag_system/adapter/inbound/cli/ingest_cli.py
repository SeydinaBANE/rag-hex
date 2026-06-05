import asyncio
import pathlib

import typer

from rag_system.config.container import Container
from rag_system.config.settings import Settings
from rag_system.domain.model.document import Document
from rag_system.domain.model.query import Query

app = typer.Typer(name="rag")


@app.command()
def ingest(file: str, document_id: str | None = None) -> None:
    path = pathlib.Path(file)
    if not path.exists():
        typer.echo(f"Error: file {file} not found", err=True)
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    doc_id = document_id or path.stem

    settings = Settings()
    container = Container(settings)
    doc = Document(
        id=doc_id,
        content=content,
        metadata={"source": str(path), "filename": path.name},
    )

    asyncio.run(container.ingestion_service.ingest(doc))
    typer.echo(f"Ingested {doc_id} ({len(content)} chars)")


@app.command()
def query(text: str, top_k: int = 5) -> None:
    settings = Settings()
    container = Container(settings)

    result = asyncio.run(container.query_service.query(Query(text=text, top_k=top_k)))

    typer.echo(f"Answer: {result.answer}")
    typer.echo(f"Results: {len(result.results)}")
    for r in result.results:
        typer.echo(f"  [{r.score:.3f}] {r.content[:100]}...")


if __name__ == "__main__":
    app()
