#!/usr/bin/env python3
"""
Agent workflow for processing test emails in .md format and placing orders.

This script reads test email files in markdown format, parses their content,
and uses the agent framework to process orders based on the email content.
"""

import asyncio
import logging

from typing import Tuple
from utils.OpenAIClient import OpenAIClient
from MCP.client import MCPClient
from utils.Executor import Executor
from agents.PlannerAgent import PlannerAgent
from utils.prompts import PLANNER_AGENT_PROMPT
from utils.schemas import Plan
import os
from dotenv import load_dotenv

load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def initialize_agent_service() -> Tuple[Executor, PlannerAgent, MCPClient]:
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
        # openai_client = OpenAI(os.getenv("OPENAI_API_KEY"))
        llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")).get_client()

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

            orechestrator = Executor(
                mcp_client=mcp_client,
            )

            logger.info("Successfully initialized Executor")
            planner = PlannerAgent(
                dev_prompt=PLANNER_AGENT_PROMPT,
                llm=llm,
                messages=[],
                tools=agent_tools,
                model_name="gpt-4.1-mini",
            )
            logger.info("Successfully initialized PlannerAgent")
            return orechestrator, planner, mcp_client

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


async def process(executor: Executor, planer: PlannerAgent, content: str) -> bool:
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
        print("first")
        plan = planer.plan(content)
        plan_parsed: Plan = plan.output_parsed
        print(f"plan: {plan}")
        print(f"plan.type: {type(plan)}")
        res = await executor.execute_plan(plan_parsed)
        print(f"RES: {res}")

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
    content = "write an essay on the culture impact of the internet"
    try:
        orchestrator, planner, mcp_client = await initialize_agent_service()
        print(orchestrator.tools)
        # Process only the oldest unprocessed email
        # email_to_process = unprocessed_emails[0]
        # logger.info(f"Processing email: {email_to_process.name}")

        # Process the email (success is a bool)
        success = await process(orchestrator, planner, content)

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
