import httpx
from bs4 import BeautifulSoup
import structlog
from app.tools.base import BaseInternalTool

logger = structlog.get_logger(__name__)

class WebScraperTool(BaseInternalTool):
    name = "web_scraper"
    description = "Fetches and parses text content from a given URL."

    async def execute(self, url: str) -> str:
        logger.info("tool_execution_start", tool=self.name, url=url)
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            logger.info("tool_execution_success", tool=self.name, url=url)
            return text[:5000]  # Limit returned text to prevent token overflow

        except Exception as e:
            logger.error("tool_execution_error", tool=self.name, error=str(e), url=url)
            return f"Failed to scrape URL {url}: {str(e)}"
