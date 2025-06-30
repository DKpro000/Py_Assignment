FUNCTION load(filepath)
    OPEN file at 'filepath' FOR reading WITH encoding "cp037"
    parsed_json ← JSON_PARSE( file_contents )
    CLOSE file
    RETURN parsed_json
END FUNCTION

FUNCTION write(data, filepath)
    json_str ← JSON_STRINGIFY(data, pretty = TRUE, ascii_safe = FALSE)   // indent = 2
    OPEN file at 'filepath' FOR writing WITH encoding "cp037"
    WRITE json_str TO file
    CLOSE file
END FUNCTION

FUNCTION str_to_json(s)
    // WARNING: uses direct code evaluation (unsafe for untrusted input)
    RETURN EVAL(s)
END FUNCTION

CLASS datasets

    PROCEDURE __init__()
        // Load every table from its corresponding text file
        self.users ← load("datasets/users.txt")
        self.menu ← load("datasets/menu.txt")
        self.ingredients ← load("datasets/ingredients.txt")
        self.ingredient_order ← load("datasets/ingredient_order.txt")
        self.orders ← load("datasets/orders.txt")
        self.finance ← load("datasets/finance.txt")
        self.feedbacks ← load("datasets/feedbacks.txt")
        self.threshold ← load("datasets/threshold.txt")
        self.equipment ← load("datasets/equipments.txt")
    END PROCEDURE

    FUNCTION get_users() → RETURN self.users
    FUNCTION get_menu() → RETURN self.menu
    FUNCTION get_iventory() → RETURN self.ingredients
    FUNCTION get_ingredient_order() → RETURN self.ingredient_order
    FUNCTION get_orders() → RETURN self.orders
    FUNCTION get_finance() → RETURN self.finance
    FUNCTION get_feedback() → RETURN self.feedbacks
    FUNCTION get_threshold() → RETURN self.threshold
    FUNCTION get_eqp() → RETURN self.equipment

END CLASS
