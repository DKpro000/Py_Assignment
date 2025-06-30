import json

def load(filepath):
    with open(filepath, 'r', encoding='cp037') as f:
        return json.load(f)

def write(data, filepath):
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    with open(filepath, 'w', encoding='cp037') as f:
        f.write(json_str)

def str_to_json(s):
    return eval(s)

class datasets:
    def __init__(self):
        self.users = load('datasets/users.txt')
        self.menu = load('datasets/menu.txt')
        self.ingredients = load('datasets/ingredients.txt')
        self.ingredient_order = load('datasets/ingredient_order.txt')
        self.orders = load('datasets/orders.txt')
        self.finance = load('datasets/finance.txt')
        self.feedbacks = load('datasets/feedbacks.txt')
        self.threshold = load('datasets/threshold.txt')
        self.equipment = load('datasets/equipments.txt')

    def get_users(self):
        return self.users

    def get_menu(self):
        return self.menu

    def get_iventory(self):
        return self.ingredients

    def get_ingredient_order(self):
        return self.ingredient_order

    def get_orders(self):
        return self.orders

    def get_finance(self):
        return self.finance

    def get_feedback(self):
        return self.feedbacks

    def get_threshold(self):
        return self.threshold

    def get_eqp(self):
        return self.equipment