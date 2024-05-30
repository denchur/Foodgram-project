def download_card(cart_data):
    short_name = "recipe__ingredients_recipe__ingredient__measurement_unit"
    print_cart_data = (
        '\n'.join([
            f'{item["recipe__ingredients_recipe__ingredient__name"]},'
            f' {item["total_amount"]} - '
            f'{item[short_name]}'
            for item in cart_data
        ])
    )
    return print_cart_data
