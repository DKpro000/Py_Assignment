CLASS Model
    PROCEDURE __init__()
        orders_data ← JSON_READ_FILE("datasets/generated_orders.json")
        ingredients_data ← LOAD_TEXT("datasets/ingredients.txt")   // via DataBase.load

        completed ← [ o ∈ orders_data.orders  WHERE o.status = "Completed" ]
        order_time_map ← { o.order_id : o.order_time  FOR o ∈ completed }

        daily_dish ← EMPTY_MAP      // KEY = (date, dish_id) : INTEGER qty
        FOR item ∈ orders_data.order_items DO
            IF item.order_id ∉ order_time_map THEN CONTINUE
            date_str ← SUBSTRING(order_time_map[item.order_id], 0, 10)  // "YYYY-MM-DD"
            key ← (date_str, item.dish_id)
            daily_dish[key] ← daily_dish.get(key, 0) + item.quantity
        END FOR

        recipe_of ← { r.dish_id : [ (ing.ingredient_id, ing.quantity)  FOR ing ∈ r.ingredients ]
                      FOR r ∈ ingredients_data.recipes }

        daily_ing ← EMPTY_MAP
        FOR (date_str, dish_id), dish_qty IN daily_dish DO
            IF dish_id ∉ recipe_of THEN CONTINUE
            FOR (ing_id, per_dish) IN recipe_of[dish_id] DO
                key ← (date_str, ing_id)
                daily_ing[key] ← daily_ing.get(key, 0) + dish_qty * per_dish
            END FOR
        END FOR

        dates ← SORT( UNIQUE( date  FOR (date, _) IN daily_ing ) )
        date_index ← { date : idx  FOR idx, date IN ENUMERATE(dates) }
        ing_ids ← UNIQUE( ing  FOR (_, ing) IN daily_ing )

        series_of ← { ing : [0.0] * LENGTH(dates)  FOR ing IN ing_ids }
        FOR (date, ing), qty IN daily_ing DO
            idx ← date_index[date]
            series_of[ing][idx] ← qty
        END FOR

        weekly_results ← EMPTY_MAP
        FOR ing_id IN ing_ids DO
            x ← [0 … LENGTH(dates)−1]
            y ← series_of[ing_id]
            (a, b) ← gradient_descent_linear_regression(x, y)
            total   ← Σ_{i=1}^{7}  MAX( a*(LENGTH(dates)−1+i) + b , 0 )
            weekly_results[ing_id] ← total
        END FOR

        self.orders_data        ← orders_data
        self.ingredients_data   ← ingredients_data
        self.weekly_results     ← weekly_results
    END PROCEDURE

    FUNCTION gradient_descent_linear_regression(x_list, y_list, lr = 0.01, epochs = 1000) → (FLOAT m, FLOAT c)
        m ← 0.0
        c ← 0.0
        n ← LENGTH(x_list)

        FOR epoch ← 1 TO epochs DO
            dm ← Σ_{(x,y) ∈ (x_list,y_list)}  (−2*x*y + 2*m*x^2 + 2*c*x)
            dc ← Σ_{(x,y) ∈ (x_list,y_list)}  (−2*y   + 2*m*x   + 2*c)
            m ← m − lr * dm
            c ← c − lr * dc
        END FOR
        RETURN (m, c)
    END FUNCTION

    FUNCTION print_output(ManagerWindow) → TABLE
        name_of ← { ing.ingredient_id : ing.name  FOR ing ∈ ingredients_data.ingredients }
        unit_of ← { ing.ingredient_id : ing.get("unit", "unit")
                    FOR ing ∈ ingredients_data.ingredients }

        // Flatten into sequential list expected by GUI helper
        rows ← []
        FOR (ing_id, qty) IN SORT_DESCENDING(weekly_results, BY value) DO
            rows.APPEND( name_of.get(ing_id, ing_id) )
            rows.APPEND( FORMAT(qty, 2) )          // two-decimal string
            rows.APPEND( unit_of.get(ing_id) )
        END FOR

        RETURN TableCreator(
            ManagerWindow,
            "Prediction of total demand for each ingredient in the next week (7 days):",
            ("name", "quantity", "unit"),
            rows
        )
    END FUNCTION

END CLASS
