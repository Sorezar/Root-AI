class Items:
    def __init__(self):
        self.available_items = {
            "bag": 2,
            "boot": 2,
            "crossbow": 1,
            "hammer": 1,
            "sword": 2,
            "teapot": 2,
            "gold": 2
        }

    def get_items(self):
        return self.available_items

    def remove_item(self, item):
        if self.available_items.get(item, 0) > 0:
            self.available_items[item] -= 1
        else:
            raise ValueError(f"Item {item} not available")

    def add_item(self, item):
        self.available_items[item] += 1