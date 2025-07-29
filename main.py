#!/usr/bin/env python3
"""
Agent workflow for processing test emails in .md format and placing orders.

This script reads test email files in markdown format, parses their content,
and uses the agent framework to process orders based on the email content.
"""

import asyncio
import logging

from pathlib import Path
from typing import Tuple
from openai import OpenAI
from MCP.client import MCPClient
from OrchestratorAgent import OrchestratorAgent
from utils.prompts import SYSTEM_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default directories
BASE_DIR = Path(__file__).parent.parent.parent.parent
TEST_EMAILS_DIR = BASE_DIR / "test_emails"
PROCESSED_EMAILS_FILE = BASE_DIR / "processed_emails.json"


async def initialize_agent_service() -> Tuple[OrchestratorAgent, MCPClient]:
    """Initialize and return the OrchestratorAgent with MCP client integration.

    Returns:
        Tuple[OrchestratorAgent, MCPClient]: A tuple containing the initialized OrchestratorAgent and MCPClient.
    """
    try:
        logger.info("Initializing MCP client...")
        mcp_client = MCPClient()
        await mcp_client.connect()

        logger.info("Getting tools from MCP...")
        tools = await mcp_client.get_tools()
        logger.info(f"Loaded {len(tools)} tools from MCP")

        logger.info("Initializing OpenAI client...")
        openai_client = OpenAI()

        # Initialize messages with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Ensure tools is a list and log its structure
        if not isinstance(tools, list):
            logger.warning(
                f"Tools is not a list, converting to list. Type: {type(tools)}"
            )
            tools = [tools] if tools is not None else []

        logger.info("Initializing OrchestratorAgent...")
        logger.info(f"Number of tools: {len(tools)}")

        try:
            # Create a copy of tools to avoid modifying the original
            agent_tools = [
                tool.copy() if hasattr(tool, "copy") else tool for tool in tools
            ]

            agent = OrchestratorAgent(
                dev_prompt=SYSTEM_PROMPT,
                mcp_client=mcp_client,
                llm=openai_client,
                messages=messages.copy(),
                tools=agent_tools,
                model_name="gpt-4.1-mini",
            )
            logger.info("Successfully initialized OrchestratorAgent")
            return agent, mcp_client

        except Exception as agent_init_error:
            logger.error(
                f"Error initializing OrchestratorAgent: {str(agent_init_error)}"
            )
            logger.error(
                f"Agent initialization error type: {type(agent_init_error).__name__}"
            )
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"Failed to initialize agent service: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


async def process_(agent: OrchestratorAgent, content: str) -> bool:
    """
    Process a single email file and place orders based on its content using the agentic workflow.
    Args:
        agent: Initialized OrchestratorAgent
        mcp_client: Initialized MCPClient
        file_path: Path to the email file to process
    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Try to process the email using agent
    try:
        # Use the agentic workflow: pass the full email to the agent's stream method
        result = None  # set result to None
        # Stream the LLM's response
        async for chunk in agent.stream(content):
            # Print the LLM's response
            if "content" in chunk and chunk["content"]:
                print(chunk["content"], end="\n", flush=True)
            # Check if the task is complete
            if chunk.get("is_task_complete", False):
                result = chunk  # set result to the last chunk
                logger.info("Agentic workflow complete.")
                break
            # if result is not None and "content" in result and "order" in result["content"].lower():
            if (
                result
                and result.get("content")
                and "order" in result.get("content").lower()
            ):
                # makr the email as processed

                print(f"\n{'=' * 80}\nSuccessfully processed: \n{'=' * 80}")
                return True  # Return True
            else:
                logger.warning("Agentic workflow did not complete successfully for:")
                return False
    except Exception as process_error:  # Exception as process_error
        logger.error(
            f"Error in agentic email processing: {str(process_error)}", exc_info=True
        )
        return False


async def process_emails() -> None:
    """
    Process .md files in the specified directory as test emails, one at a time.

    Args:
        directory: Directory containing test email files. Defaults to TEST_EMAILS_DIR.
    """

    # Initialize agent service
    content = "..."
    try:
        agent, mcp_client = await initialize_agent_service()

        # Process only the oldest unprocessed email
        # email_to_process = unprocessed_emails[0]
        # logger.info(f"Processing email: {email_to_process.name}")

        # Process the email (success is a bool)
        success = await process_(agent, content)

        if success:
            logger.info(f"Successfully processed content: {content}")
        else:
            logger.warning(f"Failed to process content: {content}")

    except Exception as e:
        logger.error(f"Error in email processing workflow: {str(e)}")
    finally:
        # Clean up
        if "mcp_client" in locals():
            await mcp_client.disconnect()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(process_emails())
