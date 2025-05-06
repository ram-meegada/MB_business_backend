def quantity_verbose(product, quantity):
    if product.unit == 'gm':
        if quantity < 1000:
            return f"{quantity} gm"
        else:
            return f"{quantity/1000} kg"
    
    elif product.unit == 'lt':
        if quantity < 1000:
            return f"{quantity} ml"
        else:
            return f"{quantity/1000} Lt"
