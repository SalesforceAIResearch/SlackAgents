import random
from check_inventory import nike_inventory, check_inventory, get_low_stock_products
from slackagents.tools.function_tool import FunctionTool
def recommend_product(size: str):
    """
    Recommend a Nike product based on customer preferences and inventory availability.
    
    :param size: The size of the product to recommend
    :type size: int
    :return: Dictionary with recommended product information
    :rtype: Dict
    """
    size = int(size)
    available_products = list(nike_inventory.keys())
    
    if not size:
        # If no preferences are provided, recommend a random product
        recommended_product = random.choice(available_products)
    else:
        # Filter products based on customer preferences
        filtered_products = available_products
        filtered_products = [p for p in filtered_products if size in nike_inventory[p]["sizes"] and nike_inventory[p]["stock"][size] > 0]
        if not filtered_products:
            return {"error": "No products match the given preferences."}
        
        recommended_product = random.choice(filtered_products)
    
    return {
        "product": recommended_product,
        "recommended_size": size
    }

recommend_product_tool = FunctionTool.from_function(recommend_product)
# Example usage
if __name__ == "__main__":
    # print(recommend_product())
    print(recommend_product(size=9))
    # print(recommend_product({"size": "15"}))  # This should return an error

