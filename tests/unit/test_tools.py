import pytest
import os
from app.tools.implementations.code_interpreter import CodeInterpreterTool
from app.tools.implementations.web_scraper import WebScraperTool

@pytest.mark.asyncio
async def test_code_interpreter():
    tool = CodeInterpreterTool()
    code = "print('Hello, OmniBrain!')"
    result = await tool.execute(code)
    assert "STDOUT:" in result
    assert "Hello, OmniBrain!" in result

@pytest.mark.asyncio
async def test_web_scraper(monkeypatch):
    tool = WebScraperTool()
    
    # Mock httpx response
    class MockResponse:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self): pass
            
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url):
            return MockResponse("<html><body><h1>Test Title</h1><p>Test paragraph.</p></body></html>")
            
    monkeypatch.setattr("httpx.AsyncClient", MockAsyncClient)
    
    result = await tool.execute("http://fake.url")
    assert "Test Title" in result
    assert "Test paragraph." in result
