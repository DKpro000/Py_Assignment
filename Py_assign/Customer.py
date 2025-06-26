import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import os
from collections import Counter, defaultdict
from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption
from AES import KeyExchange, pseudo_encrypt, pseudo_decrypt
from DataBase import load, write, str_to_json



class Customer():
    def __init__(self, system=None, panel=None):
        self.system = system
        self.panel = panel
        self.kex = KeyExchange()
        self.shared_key = None

        self.image_refs = []
        self.dish_quantities = {}
        self.qty_vars = {}
        self.totalIngredients = {}
        self.cart = []
        self.total = 0
        self.total_label = None
        self.label_widgets = {}
        self.category_frames = {}
        self.acc = ""
        self.pas = ""
        self.cart_window = None
        self.does_window_exist = False


    def retrieve_data(self):
        encrypted = self.system.get_data(self)
        return encrypted

    def exchange_public_key(self):
        return self.kex.public

    def receive_public_key(self, other_pub):
        self.shared_key = self.kex.generate_shared_key(other_pub)

    def get_item(self):
        encrypted_message = self.retrieve_data()
        decrypted = pseudo_decrypt(encrypted_message, self.shared_key)
        decrypted = str_to_json(decrypted)
        return decrypted

    def reviews(self,ReviewFrame):
        popup = Toplevel(ReviewFrame)
        popup.title("Add New Review")

        Label(popup, text="Dish Name:").grid(row=2, column=0)
        dish_name_entry = Entry(popup)
        dish_name_entry.grid(row=2, column=1)

        Label(popup, text="Rating (1-5):").grid(row=3, column=0)
        rating_entry = Spinbox(popup, from_=1, to=5)
        rating_entry.grid(row=3, column=1)

        Label(popup, text="Comment:").grid(row=4, column=0)
        comment_entry = Text(popup, height=4, width=30)
        comment_entry.grid(row=4, column=1)

        #opening the feedback file
        f_data = self.get_item()
        fk = f_data['feedback']

        #inserting the review
        def addNewComment():
            try:
                dish_name = dish_name_entry.get().title()
                rating = int(rating_entry.get())
                comment = comment_entry.get("1.0", END).strip()
                dish_id = ""
                # for dish_id we need to use dis_name to find it
                self.menu = f_data['menu']
                for items in self.menu["menu_items"]:
                    if items["name"] == dish_name:
                        dish_id = items["dish_id"]

                feedbackIDs = [item["feedback_id"] for item in fk["feedback"]]
                feedbackID = max(feedbackIDs, default=7000) + 1

                fk["feedback"].append({
                    "feedback_id": feedbackID,
                    "customer_id": self.acc,
                    "dish_id": dish_id,
                    "rating": rating,
                    "comment": comment,
                    "time": datetime.datetime.now().isoformat()
                })
                self.system.write_feedback(self, fk)

                messagebox.showinfo("Success", "Comment added successfully!")
            except Exception as e:
                messagebox.showerror(message=f"Failed to add comment.\nError: {e}")

        #submit button
        Button(popup, text="Add New Comment", command=addNewComment).grid(row=5, column=1, pady=10)



    def userProfile(self, customer_window,app,MainWindow):
        # Destroy all widgets
        for widget in customer_window.winfo_children():
            widget.destroy()

        ProfileFrame = Frame(customer_window,bg="#729cd4")
        ProfileFrame.pack(fill='both', expand=True)

        Label(ProfileFrame, text='Username:', anchor="w",bg="#729cd4").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        username_label = Label(ProfileFrame, text=self.acc)
        username_label.grid(row=0, column=1, sticky="nsew")



        def editName():
            username_label.destroy()
            username_entry = Entry(ProfileFrame)
            username_entry.insert(0, self.acc)
            username_entry.grid(row=0, column=1)

            def saveName():
                new_name = username_entry.get()
                f_data = self.get_item()
                users_available = f_data['user']
                for user in users_available['users']:
                    if user['accID'] == self.acc:
                        if new_name:
                            user['accID'] = new_name
                        self.system.write_users(self, users_available)
                        messagebox.showinfo(message=f"password updated")
                        self.acc = new_name
                        customer_interface(app,MainWindow,self.acc, self.pas)

            Button(ProfileFrame, text='Save', command=saveName).grid(row=0, column=2)

        Button(ProfileFrame, text='Edit', command=editName).grid(row=0, column=3)

        Label(ProfileFrame, text='Password:', anchor="w",bg="#729cd4").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        password_label = Label(ProfileFrame, text='*' * len(self.pas))
        password_label.grid(row=1, column=1, sticky="nsew")

        def editpassword():
            password_label.destroy()
            password_entry = Entry(ProfileFrame, show='*')
            password_entry.insert(0, self.pas)
            password_entry.grid(row=1, column=1)

            def savePass():
                new_pass = password_entry.get()
                f_data = self.get_item()
                users_available = f_data['user']
                for user in users_available['users']:
                    if user['accID'] == self.acc:
                        if new_pass:
                            user['pass'] = new_pass
                        self.system.write_users(self, users_available)
                        messagebox.showinfo(message=f"password updated")
                        self.pas = new_pass
                        customer_interface(app,MainWindow,self.acc, self.pas)

            Button(ProfileFrame, text='Save', command=savePass).grid(row=1, column=2)

        Button(ProfileFrame, text='Edit', command=editpassword).grid(row=1, column=3)
        for i in range(3):
            ProfileFrame.grid_columnconfigure(i, weight=1)

        #creating the review tabs
        ReviewFrame = Frame(customer_window,bg="#729cd4")
        ReviewFrame.pack(fill="both", expand=True)
        Button(ReviewFrame, text="add new review", command=lambda:self.reviews(ReviewFrame)).pack()

        tempFeedbackList = []
        f_data = self.get_item()
        fk = f_data['feedback']
        for fb in fk.get('feedback', []):
            if fb['customer_id'] == self.acc:
                tempFeedbackList.append(fb['feedback_id'])
                tempFeedbackList.append(fb['customer_id'])
                #converting the dish id into name
                menu = f_data['menu']
                for item in menu["menu_items"]:
                    if item['dish_id'] == fb['dish_id']:
                        tempFeedbackList.append(item['name'])
                tempFeedbackList.append(fb['rating'])
                tempFeedbackList.append(fb['comment'])
                tempFeedbackList.append(fb.get('time') or fb.get('Time', 'N/A'))
        TableCreator(ReviewFrame, "Feedbacks", ("ID", "CustomerID", "DishID", "Rating", "Comment", "Time"),
                     tempFeedbackList)
        #back button
        bottom_btn_frame = Frame(ReviewFrame,bg="#729cd4")
        bottom_btn_frame.pack(pady=10)

        Button(bottom_btn_frame, text='Back', width=20,
               command=lambda: customer_interface(app, MainWindow, self.acc, self.pas)).grid(row=0, column=0, padx=10)
        Button(bottom_btn_frame, text='Log Out', width=20, command=lambda: app.window.destroy()).grid(row=0, column=1,
                                                                                                      padx=10)


    def checkIngredientRequired(self, name):

        # Get required datasets
        f_data = self.get_item()  # From menu.txt

        self.menu = f_data['menu']
        inventory = f_data['inventory']
        ingredients = inventory['ingredients']
        recipes = inventory['recipes']

        # Step 1: Find the dish ID by name
        dishID = next((item['dish_id'] for item in self.menu["menu_items"] if item['name'] == name), None)
        if dishID is None:
            print(f"Dish '{name}' not found in menu.")
            return False

        # Step 2: Get required ingredients for the dish
        for recipe in recipes:
            if recipe['dish_id'] == dishID:
                for ing in recipe['ingredients']:
                    ing_id = ing['ingredient_id']
                    qty = ing['quantity']
                    self.totalIngredients[ing_id] = self.totalIngredients.get(ing_id, 0) + qty
                break
        else:
            print(f"No recipe found for dish ID {dishID}.")
            return False

        # Step 3: Check stock levels
        ingredient_lookup = {ing['ingredient_id']: ing for ing in ingredients}
        for ing_id, required_qty in self.totalIngredients.items():
            if ing_id not in ingredient_lookup:
                print(f"Ingredient ID {ing_id} not found in inventory.")
                return False

            available = ingredient_lookup[ing_id]['stock']
            if available < required_qty:
                ingredient_name = ingredient_lookup[ing_id]['name']
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Not enough {ingredient_name}.\nRequired: {required_qty}, Available: {available}"
                )
                return False
        print("Total ingredients used so far:")
        for ing_id, qty in self.totalIngredients.items():
            name = ingredient_lookup[ing_id]['name']
            print(f"- {name}: {qty}")
        return True  # All ingredients are available

    def shoppingCart(self, customer_window, app, MainWindow):
        # Destroy all widgets in customer window first
        for widget in customer_window.winfo_children():
            widget.destroy()

        row_index = 1
        self.total_label = None  # Reset reference to destroyed label

        # Full-size shopping frame
        shoppingFrame = Frame(customer_window,bg="#729cd3")
        shoppingFrame.pack(fill="both", expand=True)

        name_list = [item[0] for item in self.cart]
        name_counts = Counter(name_list)
        name_to_price = {item[0]: item[1] for item in self.cart}

        if not name_counts:
            # ❗️Show centered "Cart is empty"
            empty_label = Label(
                shoppingFrame,
                text="Cart is empty.",
                font=("Arial", 20, "bold"),bg="#729cd4"
            )
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
            # ⬅️ Back button at bottom right
            Button(
                shoppingFrame,
                text='Back',
                command=lambda: customer_interface(app, MainWindow, self.acc, self.pas)
            ).place(relx=1, rely=1, anchor="se", x=-10, y=-10)
        else:
            # 🧾 Table headers
            headers = ["Item Name", "Quantity", "Price per Unit"]
            for i, header in enumerate(headers):
                Label(shoppingFrame, text=header, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=10, pady=5,
                                                                                   sticky="nsew")

            # 🧾 Colors for alternating rows
            row_colors = ["#FFFFFF", "#F0F0F0"]

            # 🧾 Items
            for row_index, (item_name, count) in enumerate(name_counts.items(), start=1):
                item_price = name_to_price[item_name]
                bg_color = row_colors[row_index % 2]

                Label(shoppingFrame, text=item_name, bg=bg_color).grid(row=row_index, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
                Label(shoppingFrame, text=str(count), bg=bg_color).grid(row=row_index, column=1, padx=10, pady=5,
                                                                        sticky="nsew")
                Label(shoppingFrame, text=f"${item_price:.2f}", bg=bg_color).grid(row=row_index, column=2, padx=10,
                                                                                  pady=5, sticky="nsew")

            # 💰 Total
            total = sum(name_to_price[name] * count for name, count in name_counts.items())
            self.total_label = Label(shoppingFrame, text=f"Total: ${total:.2f}", font=("Arial", 14, "bold"))
            self.total_label.grid(row=row_index + 1, column=0, columnspan=3, sticky="e", padx=10, pady=(10, 0))

            # 🧱 Grid column weight for expansion
            for col in range(3):
                shoppingFrame.grid_columnconfigure(col, weight=1)
            for r in range(row_index + 2):
                shoppingFrame.grid_rowconfigure(r, weight=1)

            row_index += 2  # Adjust for button

            # ⬅️ Back button at bottom right
            Button(
                shoppingFrame,
                text='Back',
                command=lambda: customer_interface(app, MainWindow, self.acc, self.pas)
            ).grid(row=row_index + 1, column=2, sticky="e", padx=10, pady=15)


    def checkIngredientRollback(self, name):
        # Use the existing in-memory menu and inventory
        f_data = self.get_item()
        menu_items = f_data['menu']['menu_items']
        ingredients = f_data['inventory']['ingredients']
        recipes = f_data['inventory']['recipes']

        dishID = next((item['dish_id'] for item in menu_items if item['name'] == name), None)
        if dishID is None:
            print(f"Dish '{name}' not found in menu.")
            return False

        ingredient_lookup = {ing['ingredient_id']: ing for ing in ingredients}

        for recipe in recipes:
            if recipe['dish_id'] == dishID:
                for ing in recipe['ingredients']:
                    ing_id = ing['ingredient_id']
                    qty = ing['quantity']

                    # Add back to stock (if you're using this)
                    if ing_id in ingredient_lookup:
                        ingredient_lookup[ing_id]['stock'] += qty

                    # Subtract from total used
                    if ing_id in self.totalIngredients:
                        self.totalIngredients[ing_id] -= qty
                        if self.totalIngredients[ing_id] < 0:
                            self.totalIngredients[ing_id] = 0  # Avoid negative values
                    else:
                        # Should not happen, but guard against it
                        self.totalIngredients[ing_id] = 0
                break
        else:
            print(f"No recipe found for dish ID {dishID}.")
            return False

        # Print updated ingredient usage
        print("Updated total ingredients used after rollback:")
        for ing_id, qty in self.totalIngredients.items():
            ing_name = ingredient_lookup.get(ing_id, {}).get('name', f'ID {ing_id}')
            print(f"- {ing_name}: {qty}")

        return True

    def print_customer_Cols(self,innerFrame, image_path, dish, price):
        if dish not in self.dish_quantities:
            self.dish_quantities[dish] = 0

        frame = Frame(innerFrame, bg="#fff5ec")
        frame.pack(fill="both", expand=True)

        # Load image
        if os.path.exists(image_path):
            try:
                img = PhotoImage(file=image_path)
                self.image_refs.append(img)
                Label(frame, image=img, bg="#fff5ec").pack()
            except Exception:
                Label(frame, text="Error loading image", bg="#fff5ec").pack()
        else:
            Label(frame, text="Image not found", bg="#fff5ec").pack()

        # Dish label
        Label(frame, text=f"{dish}\n${price:.2f}", font=("Times New Roman", 10, "bold"), bg="#fff5ec").pack()

        # Quantity controls
        qty_frame = Frame(frame, bg="#fff5ec")
        qty_frame.pack()

        qty_var = StringVar(value=str(self.dish_quantities[dish]))
        qty_label = Label(qty_frame, textvariable=qty_var, width=3, bg="#fff5ec", font=("Arial", 12))
        qty_label.pack(side="left")

        def increase():
            print("increasing")
            if not self.checkIngredientRequired(dish):
                return  # Do not proceed if ingredients are insufficient
            self.dish_quantities[dish] += 1
            qty_var.set(str(self.dish_quantities[dish]))
            self.cart.append([dish, price])
            self.total += price

        def decrease():
            if self.dish_quantities[dish] > 0:
                self.dish_quantities[dish] -= 1
                qty_var.set(str(self.dish_quantities[dish]))

                for i in range(len(self.cart)):
                    if self.cart[i][0] == dish:
                        self.total -= self.cart[i][1]
                        del self.cart[i]
                        break

                # Restore ingredients
                self.checkIngredientRollback(dish)

        Button(qty_frame, text="-", command=decrease, width=2).pack(side="left", padx=2)
        Button(qty_frame, text="+", command=increase, width=2).pack(side="left", padx=2)

    def scrollBar(self, my_canvas, tab):
        my_scrollbar = Scrollbar(tab, orient=VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill=Y)
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_scrollbar.config(command=my_canvas.yview)


def customer_interface(app,MainWindow,acc, pas):
    #creating window


    f_data = app.get_item()
    menu = f_data['menu']

    app.acc = acc
    app.pas = pas

    #main menu
    # creating header
    if app.does_window_exist == False:
        app.window = Toplevel(MainWindow)
        app.window.attributes('-fullscreen', True)
        app.does_window_exist = True

    for widget in app.window.winfo_children():
        widget.destroy()

    header_frame = Frame(app.window, bg="#ccc")
    header_frame.pack(fill="x")

    # Configure columns: 0 = Home, 1 = spacer, 2 = Cart, 3 = Profile
    header_frame.grid_columnconfigure(0, weight=1)  # Home takes most space
    header_frame.grid_columnconfigure(1, weight=1)
    header_frame.grid_columnconfigure(2, weight=0)
    header_frame.grid_columnconfigure(3, weight=0)

    Label(header_frame, text="Home", font=("Arial", 20, "bold"), bg="#ccc").grid(row=0, column=0, sticky="w", padx=10,
                                                                                 pady=10)

    Button(header_frame, text="Shopping Cart", command=lambda: app.shoppingCart(app.window, app, MainWindow)).grid(
        row=0, column=2, sticky="e", padx=5, pady=10
    )

    Button(header_frame, text="Profile", command=lambda: app.userProfile(app.window, app, MainWindow)).grid(
        row=0, column=3, sticky="e", padx=5, pady=10
    )

    app.notebook = ttk.Notebook(app.window)
    tab = Frame(app.notebook)
    # making a scollbar
    app.my_canvas = Canvas(tab)
    app.my_canvas.pack(side=LEFT, fill="both", expand=True)
    app.scrollBar(app.my_canvas, tab)

    app.scrollable_frame = Frame(app.my_canvas, bg="#729cd4")
    app.my_canvas.create_window((0, 0), window=app.scrollable_frame, anchor="nw", tags="frame")
    app.scrollable_frame.bind("<Configure>", lambda e: app.my_canvas.configure(scrollregion=app.my_canvas.bbox("all")))

    def resize_scrollable_frame(event):
        canvas_width = event.width
        app.my_canvas.itemconfig("frame", width=canvas_width)

    app.my_canvas.bind("<Configure>", resize_scrollable_frame)

    app.notebook.add(tab, text="ALL")
    app.notebook.pack(expand=True, fill="both")

    cols = 3
    row_index = 0

    menu_by_category = defaultdict(list)
    for item in menu["menu_items"]:
        menu_by_category[item.get("category", "Unknown")].append(
            (item.get("name", "Unknown"), item.get("image", ""), item.get("price", 0))
        )
    # printing out the main menu
    for category, items_list in menu_by_category.items():
        category_label = Label(app.scrollable_frame, text=category, font=("Showcard Gothic", 20, "bold"),
                               anchor="w", bg="#729cd4", fg="#fff5ec")
        category_label.grid(row=row_index, column=0, columnspan=cols, sticky="w", pady=(10, 0))
        row_index += 1

        for i, (food, image_path, price) in enumerate(items_list):
            col = i % cols
            sub_row = i // cols

            innerFrame = Frame(app.scrollable_frame, bg="#fff5ec", bd=2, relief=GROOVE)
            innerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

            app.print_customer_Cols(innerFrame, image_path, food, price)

        row_index += (len(items_list) + cols - 1) // cols

    for i in range(cols):
        app.scrollable_frame.grid_columnconfigure(i, weight=1)
    # now to make tabs that only contains the items of a certain category
    subCols = 3
    for category, items_list in menu_by_category.items():
        subTab = ttk.Frame(app.notebook)
        app.notebook.add(subTab, text=category)
        subOuter = Frame(subTab, bg="#729cd4")
        subOuter.pack(expand=True, fill="both")
        app.category_frames[category] = subOuter

        for i, (food, image_path, price) in enumerate(items_list):
            col = i % cols
            sub_row = i // cols

            innerFrame = Frame(subOuter, bg="#fff5ec", bd=2, relief=GROOVE)
            innerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

            app.print_customer_Cols(innerFrame, image_path, food, price)

        row_index += (len(items_list) + cols - 1) // cols

        for i in range(subCols):
            subOuter.grid_columnconfigure(i, weight=1)

