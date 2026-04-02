"""ILIN entry point — starts the FastAPI server."""

import uvicorn

from ilin.config import settings


def main():
    """Run the ILIN server."""
    uvicorn.run(
        "ilin.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
