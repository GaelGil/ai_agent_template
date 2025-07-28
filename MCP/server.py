from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)


mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="add_to_cart",
    description="Add a part to the cart given the part id. Requires an existing order/cart (create one first if needed). Use this as the primary way to fulfill an order. Only use find_inventory if add_to_cart fails for a specific item.",
)
def add_to_cart(stock_item_id: str | int, quantity: int, cart) -> str:
    """"""
    pass


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
