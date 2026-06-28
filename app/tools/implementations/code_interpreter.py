import asyncio
import tempfile
import os
import structlog
from typing import Any
from app.tools.base import BaseInternalTool

logger = structlog.get_logger(__name__)

class CodeInterpreterTool(BaseInternalTool):
    name = "code_interpreter"
    description = "Executes Python code in an isolated temporary directory. Use this to run scripts, crunch data, or verify logic."

    async def execute(self, code: str, timeout: int = 10) -> str:
        logger.info("tool_execution_start", tool=self.name)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "script.py")
            with open(file_path, "w") as f:
                f.write(code)

            try:
                process = await asyncio.create_subprocess_exec(
                    "python3", file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                except asyncio.TimeoutError:
                    process.kill()
                    logger.warning("tool_execution_timeout", tool=self.name)
                    return f"Execution timed out after {timeout} seconds."

                out = stdout.decode().strip()
                err = stderr.decode().strip()

                result = ""
                if out:
                    result += f"STDOUT:\n{out}\n"
                if err:
                    result += f"STDERR:\n{err}\n"

                logger.info("tool_execution_success", tool=self.name)
                return result if result else "Execution completed successfully with no output."

            except Exception as e:
                logger.error("tool_execution_error", tool=self.name, error=str(e))
                return f"Execution failed: {str(e)}"
