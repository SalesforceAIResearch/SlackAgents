import random

from slackagents.tools.function_tool import FunctionTool

# Simulated local data for Nike products inventory
nike_inventory = {
    "Air Max 90": {"sizes": [7, 8, 9, 10, 11], "stock": {7: 5, 8: 3, 9: 0, 10: 2, 11: 1}},
    "Air Force 1": {"sizes": [6, 7, 8, 9, 10, 11, 12], "stock": {6: 2, 7: 4, 8: 6, 9: 1, 10: 0, 11: 3, 12: 2}}
}

def check_inventory(product_name: str, size: int = None):
    """
    Check inventory for a given Nike product and optionally a specific size.
    
    :param product_name: Name of the Nike product
    :type product_name: str
    :param size: Optional size to check (if None, returns inventory for all sizes)
    :type size: int
    :return: Dictionary with inventory information
    :rtype: Dict
    """
    if product_name not in nike_inventory:
        return {"error": f"Product '{product_name}' not found in inventory."}
    
    product_info = nike_inventory[product_name]
    
    if size is not None:
        if size not in product_info["sizes"]:
            return {"error": f"Size {size} is not available for '{product_name}'."}
        
        stock = product_info["stock"].get(size, 0)
        return {
            "product": product_name,
            "size": size,
            "in_stock": stock > 0,
            "stock_count": stock
        }
    else:
        return {
            "product": product_name,
            "sizes_available": product_info["sizes"],
            "stock_by_size": product_info["stock"]
        }

def get_low_stock_products(threshold: int = 3):
    """
    Get a list of products with low stock (below the given threshold).
    
    :param threshold: Stock count threshold to consider as low
    :type threshold: int
    """
    low_stock = []
    for product, info in nike_inventory.items():
        for size, count in info["stock"].items():
            if count > 0 and count <= threshold:
                low_stock.append({
                    "product": product,
                    "size": size,
                    "stock_count": count
                })
    return low_stock

check_inventory_tool = FunctionTool.from_function(check_inventory)
get_low_stock_products_tool = FunctionTool.from_function(get_low_stock_products)
# Example usage
if __name__ == "__main__":
    print(check_inventory("Air Max 90"))
    print(check_inventory("Air Force 1", 8))
    print(check_inventory("React Element 55", 10))
    print(get_low_stock_products(2))
