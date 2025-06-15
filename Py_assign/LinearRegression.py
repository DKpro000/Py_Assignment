from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption
from DataBase import datasets, load, write, str_to_json
from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption

class Model:
    def __init__(self):
        with open('datasets/generated_orders.json', 'r', encoding='utf-8') as f:
            self.orders_data = json.load(f)

        self.ingredients_data = load('datasets/ingredients.txt')

        completed_orders = [o for o in self.orders_data['orders'] if o['status'] == 'Completed']
        order_time_map = {o['order_id']: o['order_time'] for o in completed_orders}

        daily_dish_sales = {}
        for item in self.orders_data['order_items']:
            oid = item['order_id']
            if oid not in order_time_map:
                continue
            date_str = order_time_map[oid][:10]
            dish_id = item['dish_id']
            qty = item['quantity']
            key = (date_str, dish_id)
            daily_dish_sales[key] = daily_dish_sales.get(key, 0) + qty

        recipe_dict = {}
        for r in self.ingredients_data['recipes']:
            recipe_dict[r['dish_id']] = [(ing['ingredient_id'], ing['quantity']) for ing in r['ingredients']]

        daily_ingredient_sales = {}
        for (date_str, dish_id), dish_qty in daily_dish_sales.items():
            if dish_id not in recipe_dict:
                continue
            for ing_id, ing_qty_per_dish in recipe_dict[dish_id]:
                key = (date_str, ing_id)
                daily_ingredient_sales[key] = daily_ingredient_sales.get(key, 0) + dish_qty * ing_qty_per_dish

        dates = sorted(list(set(date for date, _ in daily_ingredient_sales.keys())))
        date_to_num = {date: i for i, date in enumerate(dates)}
        ingredient_ids = list(set(ing_id for _, ing_id in daily_ingredient_sales.keys()))

        ingredient_time_series = {ing_id: [0.0] * len(dates) for ing_id in ingredient_ids}
        for (date, ing_id), qty in daily_ingredient_sales.items():
            idx = date_to_num[date]
            ingredient_time_series[ing_id][idx] = qty

        self.weekly_results = {}
        for ing_id in ingredient_ids:
            y = ingredient_time_series[ing_id]
            x = list(range(len(y)))
            a, b = self.gradient_descent_linear_regression(x, y)
            total_pred_qty = sum(max(a * (len(dates) - 1 + i) + b, 0) for i in range(1, 8))
            self.weekly_results[ing_id] = total_pred_qty

    def gradient_descent_linear_regression(self, x_list, y_list, lr=0.01, epochs=5000):
        a, b = 0.0, 0.0
        n = len(x_list)
        if n == 0:
            return 0.0, 0.0
        for _ in range(epochs):
            da = sum((a * x + b - y) * x for x, y in zip(x_list, y_list)) * 2 / n
            db = sum((a * x + b - y) for x, y in zip(x_list, y_list)) * 2 / n
            a -= lr * da
            b -= lr * db
        return a, b

    def print_output(self,ManagerWindow):
        name_map = {i['ingredient_id']: i['name'] for i in self.ingredients_data['ingredients']}
        unit_map = {i['ingredient_id']: i.get('unit', 'unit') for i in self.ingredients_data['ingredients']}
        print("Prediction of total demand for each ingredient in the next week (7 days):")
        OutputList = []
        for ing_id, qty in sorted(self.weekly_results.items(), key=lambda x: -x[1]):
            tempQ = f"{qty:.2f}"
            OutputList.append(name_map.get(ing_id, ing_id))
            OutputList.append(tempQ)
            OutputList.append(unit_map.get(ing_id))
        return TableCreator(ManagerWindow,"",("name","quantity","unit"),OutputList)