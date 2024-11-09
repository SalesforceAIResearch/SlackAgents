import random
from enum import Enum

from slackagents.tools.function_tool import FunctionTool

class OrderStatus(Enum):
    PLACED = "Placed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

# Simulated order database
order_database = {
    "ORD001": {"status": OrderStatus.SHIPPED, "product": "Air Max 90", "size": 8},
}

def check_order_status(order_id: str):
    """
    Check the status of an order and provide possible modifications.

    :param order_id: The unique identifier for the order
    :type order_id: str
    :return: Dictionary with order status and possible modifications
    :rtype: Dict
    """
    if order_id not in order_database:
        return {"error": f"Order '{order_id}' not found."}

    order = order_database[order_id]
    status = order["status"]
    possible_modifications = []

    if status == OrderStatus.PLACED:
        possible_modifications = "YES"
    elif status == OrderStatus.PROCESSING:
        possible_modifications = "YES"
    elif status == OrderStatus.SHIPPED:
        possible_modifications = "YES"
    elif status == OrderStatus.OUT_FOR_DELIVERY:
        possible_modifications = ["Modify order"]
    elif status == OrderStatus.DELIVERED:
        possible_modifications = ["Return item", "Exchange item"]
    elif status == OrderStatus.CANCELLED:
        possible_modifications = ["Reorder item"]

    return {
        "order_id": order_id,
        "status": status.value,
        "product": order["product"],
        "size": order["size"],
        "possible_modifications": possible_modifications
    }

check_order_status_tool = FunctionTool.from_function(check_order_status)

# Example usage
if __name__ == "__main__":
    # ... (previous examples remain unchanged)
    print(check_order_status("ORD001"))
    print(check_order_status("ORD002"))
    print(check_order_status("ORD003"))