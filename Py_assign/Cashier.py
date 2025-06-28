from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import os
from collections import Counter, defaultdict
from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption
from AES import KeyExchange, pseudo_encrypt, pseudo_decrypt
from DataBase import load, write, str_to_json

class Cashier():
    def __init__(self, system=None, panel=None):
        self.system = system
        self.panel = panel
        self.kex = KeyExchange()
        self.shared_key = None

        self.dish_quantities = {}
        self.image_refs = []
        self.total = 0
        self.total_label = None
        self.cart = []
        self.as_tuples = [tuple(item) for item in self.cart]
        self.CRow = 0
        self.label_widgets = {}
        self.CWindow = None
        self.category_frames = {}
        self.totalIngredients = {}

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



    def PrintOut(self):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        self.orders = f_data['order']

        try:
            name_list = [tuple(item) for item in self.cart]
            counts = Counter(name_list)

            totalOrderIDs = [item["order_id"] for item in self.orders["orders"]]
            orderID = max(totalOrderIDs, default=5000) + 1

            customerID_num = len(self.orders["orders"]) + 201
            customerID = f"C{customerID_num}"

            order_items = []
            total = 0.0

            for (name, price), quantity in counts.items():
                dish = next((item for item in self.menu["menu_items"] if item["name"] == name), None)
                if not dish:
                    continue

                dish_id = dish["dish_id"]
                order_items.append({
                    "order_id": orderID,
                    "dish_id": dish_id,
                    "quantity": quantity,
                    "unit_price": price
                })

                total += quantity * price

            self.orders["orders"].append({
                "order_id": orderID,
                "customer_id": customerID,
                "order_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "In progress",
                "total": round(total, 2)
            })

            self.orders["order_items"].extend(order_items)
            new_dish_ids = [[item["dish_id"], item["quantity"]] for item in order_items]

            messagebox.showinfo(message=f"Receipt\norder_id:{orderID}\ncustomer id:{customerID}\norder time:{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}\ntotal:{round(total, 2)}")
            self.system.write_chs_orders(self, self.orders, new_dish_ids)

        except Exception as e:
            messagebox.showerror(message=f"Order submission failed:\n{e}")

    def Adding(self, addingTextBox, addingPrice, addingCategory, addingImg):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        try:
            foodName = addingTextBox.get().title()
            foodPrice = float(addingPrice.get())
            foodCategory = addingCategory.get().title()
            foodImg = addingImg.get()

            menuIDs = [item["dish_id"] for item in self.menu["menu_items"]]
            foodID = max(menuIDs, default=1000) + 1

            self.menu["menu_items"].append({
                "dish_id": foodID,
                "name": foodName,
                "image": foodImg,
                "category": foodCategory,
                "price": foodPrice,
                "available": True
            })

            self.system.write_menu(self, self.menu)
            self.refresh_all_tab()

            if foodCategory in self.category_frames:
                self.refresh_category_tab(foodCategory)
                messagebox.showinfo(message="Item added successfully!")
            else:
                messagebox.showinfo(message=f"Item added to '{foodCategory}', but tab does not exist (may need restart).")
        except Exception as e:
            messagebox.showerror(message=f"Failed to add item.\nError: {e}")

    def refresh_cart(self, CWindow):
        try:
            for widget in self.label_widgets.values():
                widget.destroy()
            self.label_widgets = {}

            name_list = [item[0] for item in self.cart]
            name_counts = Counter(name_list)
            name_to_price = {item[0]: item[1] for item in self.cart}

            for row_index, (item_name, count) in enumerate(name_counts.items()):
                item_price = name_to_price[item_name]
                self.label_widgets[(row_index, 0)] = Label(CWindow, text=item_name, font=("Arial", 14, "bold"))
                self.label_widgets[(row_index, 1)] = Label(CWindow, text=str(count), font=("Arial", 14, "bold"))
                self.label_widgets[(row_index, 2)] = Label(CWindow, text=f"{item_price:.2f}", font=("Arial", 14, "bold"))

                self.label_widgets[(row_index, 0)].grid(row=row_index, column=0)
                self.label_widgets[(row_index, 1)].grid(row=row_index, column=1)
                self.label_widgets[(row_index, 2)].grid(row=row_index, column=2)

            if self.total_label is None:
                self.total_label = Label(CWindow, font=("Arial", 14, "bold"))

            self.total_label.grid(row=row_index + 1, column=0, columnspan=3, sticky="w", pady=(10, 0))
            self.total_label.config(text=f"Total: ${self.total:.2f}")
        except:
            self.total_label.config(text=f"Total: $0")

    def openFile(self, imagePathVar):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if path:
            imagePathVar.set(path)
            messagebox.showinfo(message="Picture added successfully")

    def deletingItem(self, DelName, Delcategory):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        try:
            name = DelName.get().title()
            category = Delcategory.get().title()

            itemIndex = next(
                i for i, item in enumerate(self.menu["menu_items"])
                if item["name"] == name and item["category"] == category
            )

            removed_item = self.menu["menu_items"].pop(itemIndex)

            messagebox.showinfo(message=f"Item '{removed_item['name']}' deleted successfully.")
            self.refresh_all_tab()
            self.refresh_category_tab(category)
            self.system.write_menu(self, self.menu)
        except StopIteration:
            messagebox.showerror(message="Item not found. Please check the name and category.")
        except Exception as e:
            messagebox.showerror(message=f"An unexpected error occurred:\n{e}")

    def UpdateIncrease(self, UpdateName, Updatecategory, UpdatePercentage):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        try:
            name = UpdateName.get().title()
            category = Updatecategory.get().title()
            percentage = (100 + float(UpdatePercentage.get())) / 100

            found = False
            for item in self.menu["menu_items"]:
                if item["name"] == name and item["category"] == category:
                    old_price = item["price"]
                    item["price"] = round(old_price * percentage, 2)
                    found = True
                    break

            if found:
                messagebox.showinfo(message=f"Item '{name}' updated successfully.")
                self.refresh_all_tab()
                self.refresh_category_tab(category)
                self.system.write_menu(self, self.menu)
            else:
                messagebox.showerror(message="Item not found. Please check the name and category.")
        except ValueError:
            messagebox.showerror(message="Invalid percentage value.")
        except Exception as e:
            messagebox.showerror(message=f"An unexpected error occurred:\n{e}")

    def UpdateDecrease(self, UpdateName, Updatecategory, UpdatePercentage):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        try:
            name = UpdateName.get().title()
            category = Updatecategory.get().title()
            percentage = (100 - float(UpdatePercentage.get())) / 100

            found = False
            for item in self.menu["menu_items"]:
                if item["name"] == name and item["category"] == category:
                    old_price = item["price"]
                    item["price"] = round(old_price * percentage, 2)
                    found = True
                    break

            if found:
                messagebox.showinfo(message=f"Item '{name}' updated successfully.")
                self.refresh_all_tab()
                self.refresh_category_tab(category)
                self.system.write_menu(self, self.menu)
            else:
                messagebox.showerror(message="Item not found. Please check the name and category.")
        except ValueError:
            messagebox.showerror(message="Invalid percentage value.")
        except Exception as e:
            messagebox.showerror(message=f"An unexpected error occurred:\n{e}")

    def draw_rounded_border(self, event, canvas):
        canvas.delete("border")

        w = event.width
        h = event.height
        r = 20          
        margin = 10    
        stroke_width = 3
        fill_color = "#fff5ec"
        border_color = "#e4791c"

        canvas.create_arc(margin, margin, margin+2*r, margin+2*r,
                          start=90, extent=90, style=PIESLICE,
                          fill=fill_color, outline=fill_color, tags="border")
        canvas.create_arc(w - margin - 2*r, margin, w - margin, margin + 2*r,
                          start=0, extent=90, style=PIESLICE,
                          fill=fill_color, outline=fill_color, tags="border")
        canvas.create_arc(w - margin - 2*r, h - margin - 2*r, w - margin, h - margin,
                          start=270, extent=90, style=PIESLICE,
                          fill=fill_color, outline=fill_color, tags="border")
        canvas.create_arc(margin, h - margin - 2*r, margin + 2*r, h - margin,
                          start=180, extent=90, style=PIESLICE,
                          fill=fill_color, outline=fill_color, tags="border")

        canvas.create_rectangle(margin + r, margin, w - margin - r, margin + r,
                                fill=fill_color, outline=fill_color, tags="border")
        canvas.create_rectangle(margin + r, h - margin - r, w - margin - r, h - margin,
                                fill=fill_color, outline=fill_color, tags="border")
        canvas.create_rectangle(margin, margin + r, margin + r, h - margin - r,
                                fill=fill_color, outline=fill_color, tags="border")
        canvas.create_rectangle(w - margin - r, margin + r, w - margin, h - margin - r,
                                fill=fill_color, outline=fill_color, tags="border")
        canvas.create_rectangle(margin + r, margin + r, w - margin - r, h - margin - r,
                                fill=fill_color, outline=fill_color, tags="border")

        canvas.create_arc(margin, margin, margin+2*r, margin+2*r,
                          start=90, extent=90, style=ARC,
                          width=stroke_width, outline=border_color, tags="border")
        canvas.create_arc(w - margin - 2*r, margin, w - margin, margin + 2*r,
                          start=0, extent=90, style=ARC,
                          width=stroke_width, outline=border_color, tags="border")
        canvas.create_arc(w - margin - 2*r, h - margin - 2*r, w - margin, h - margin,
                          start=270, extent=90, style=ARC,
                          width=stroke_width, outline=border_color, tags="border")
        canvas.create_arc(margin, h - margin - 2*r, margin + 2*r, h - margin,
                          start=180, extent=90, style=ARC,
                          width=stroke_width, outline=border_color, tags="border")

        canvas.create_line(margin + r, margin, w - margin - r, margin,
                           width=stroke_width, fill=border_color, tags="border")
        canvas.create_line(w - margin, margin + r, w - margin, h - margin - r,
                           width=stroke_width, fill=border_color, tags="border")
        canvas.create_line(w - margin - r, h - margin, margin + r, h - margin,
                           width=stroke_width, fill=border_color, tags="border")
        canvas.create_line(margin, h - margin - r, margin, margin + r,
                           width=stroke_width, fill=border_color, tags="border")

    def AddItems(self, SettingsNotebook):
        AddTab = Frame(SettingsNotebook)
        SettingsNotebook.add(AddTab, text="ADD ITEMS")
        AddTab.configure(bg="#387647")

        canvas = Canvas(AddTab, bg="#387647", highlightthickness=0, bd=0)
        canvas.place(relx=0, rely=0, relwidth=1, height=350)
        canvas.bind("<Configure>", lambda event: self.draw_rounded_border(event, canvas))

        addOuter = Frame(AddTab, bg="#fff5ec")
        addOuter.place(relx=0.5, y=150, relwidth=0.9, anchor="center")

        addOuter.grid_columnconfigure(0, weight=1)
        addOuter.grid_columnconfigure(1, weight=1)
        addOuter.grid_columnconfigure(2, weight=1)

        Label(addOuter, text="ADD ITEM", font=("Showcard Gothic", 20, "bold"), bg="#fff5ec").grid(row=0, column=0, columnspan=3)

        Label(addOuter, text="Name", bg="#fff5ec").grid(row=1, column=0)
        addingName = Entry(addOuter, font=("Arial", 25))
        addingName.grid(row=1, column=1, columnspan=2, sticky="ew")

        Label(addOuter, text="Price", bg="#fff5ec").grid(row=2, column=0)
        addingPrice = Entry(addOuter, font=("Arial", 25))
        addingPrice.grid(row=2, column=1, columnspan=2, sticky="ew")

        Label(addOuter, text="Category", bg="#fff5ec").grid(row=3, column=0)
        addingCategory = Entry(addOuter, font=("Arial", 25))
        addingCategory.grid(row=3, column=1, columnspan=2, sticky="ew")

        imagePathVar = StringVar()
        Label(addOuter, text="Image", bg="#fff5ec").grid(row=4, column=0)
        Button(addOuter, text="Insert", command=lambda: self.openFile(imagePathVar)).grid(row=4, column=1, columnspan=2, sticky="ew")

        Label(addOuter, text="", bg="#fff5ec").grid(row=5, column=0)

        Button(addOuter, text="Add", bg="#f7cf93", font=("Arial", 10), command=lambda: self.Adding(addingName, addingPrice, addingCategory, imagePathVar)).grid(row=6, column=0, columnspan=3)

    def DeletingItems(self, SettingsNotebook):
        DelTab = Frame(SettingsNotebook)
        SettingsNotebook.add(DelTab, text="DELETE ITEMS")
        DelTab.configure(bg="#387647")

        canvas = Canvas(DelTab, bg="#387647", highlightthickness=0, bd=0)
        canvas.place(relx=0, rely=0, relwidth=1, height=350)
        canvas.bind("<Configure>", lambda event: self.draw_rounded_border(event, canvas))

        DelOuter = Frame(DelTab, bg="#fff5ec")
        DelOuter.place(relx=0.5, y=150, relwidth=0.9, anchor="center")

        DelOuter.grid_columnconfigure(0, weight=1)
        DelOuter.grid_columnconfigure(1, weight=1)
        DelOuter.grid_columnconfigure(2, weight=1)

        Label(DelOuter, text="Delete a dish", font=("Showcard Gothic", 20, "bold"), bg="#fff5ec").grid(row=0, column=0, columnspan=3)
        Label(DelOuter, bg="#fff5ec").grid(row=1, column=0)

        Label(DelOuter, text="Name", bg="#fff5ec").grid(row=2, column=0)
        DelName = Entry(DelOuter, font=("Arial", 25))
        DelName.grid(row=2, column=1, columnspan=2, sticky="ew")

        Label(DelOuter, text="Category", bg="#fff5ec").grid(row=3, column=0)
        Delcategory = Entry(DelOuter, font=("Arial", 25))
        Delcategory.grid(row=3, column=1, columnspan=2, sticky="ew")

        Label(DelOuter, bg="#fff5ec").grid(row=4, column=0)
        Button(DelOuter, text="Delete", bg="#f7cf93", font=("Arial", 10), command=lambda: self.deletingItem(DelName, Delcategory)).grid(row=5, column=0, columnspan=3)

    def UpdateItems(self, SettingsNotebook):
        UpdateTab = Frame(SettingsNotebook)
        SettingsNotebook.add(UpdateTab, text="UPDATE ITEMS")
        UpdateTab.configure(bg="#387647")

        canvas = Canvas(UpdateTab, bg="#387647", highlightthickness=0, bd=0)
        canvas.place(relx=0, rely=0, relwidth=1, height=350)
        canvas.bind("<Configure>", lambda event: self.draw_rounded_border(event, canvas))

        UpdateOuter = Frame(UpdateTab, bg="#fff5ec")
        UpdateOuter.place(relx=0.5, y=150, relwidth=0.9, anchor="center")

        UpdateOuter.grid_columnconfigure(0, weight=1)
        UpdateOuter.grid_columnconfigure(1, weight=1)
        UpdateOuter.grid_columnconfigure(2, weight=1)

        Label(UpdateOuter, text="Update a dish", font=("Showcard Gothic", 20, "bold"), bg="#fff5ec").grid(row=0, column=0, columnspan=3)
        Label(UpdateOuter, text="", bg="#fff5ec").grid(row=1, column=0)

        Label(UpdateOuter, text="Name", bg="#fff5ec").grid(row=2, column=0)
        UpdateName = Entry(UpdateOuter, font=("Arial", 25))
        UpdateName.grid(row=2, column=1, columnspan=2, sticky="ew")

        Label(UpdateOuter, text="", bg="#fff5ec").grid(row=3, column=0)

        Label(UpdateOuter, text="Category", bg="#fff5ec").grid(row=4, column=0)
        Updatecategory = Entry(UpdateOuter, font=("Arial", 25))
        Updatecategory.grid(row=4, column=1, columnspan=2, sticky="ew")

        Label(UpdateOuter, text="", bg="#fff5ec").grid(row=5, column=0)

        Label(UpdateOuter, text="Amount (percentage)", bg="#fff5ec").grid(row=6, column=0)
        UpdatePercentage = Entry(UpdateOuter, font=("Arial", 25))
        UpdatePercentage.grid(row=6, column=1, columnspan=2, sticky="ew")

        Label(UpdateOuter, text="", bg="#fff5ec").grid(row=7, column=0)

        Button(UpdateOuter, text="Increase", font=("Arial", 10), bg="#f7cf93", command=lambda: self.UpdateIncrease(UpdateName, Updatecategory, UpdatePercentage)).grid(row=8, column=0, columnspan=2)
        Button(UpdateOuter, text="Decrease", font=("Arial", 10), bg="#f7cf93", command=lambda: self.UpdateDecrease(UpdateName, Updatecategory, UpdatePercentage)).grid(row=8, column=1, columnspan=2)

    def PrintReceipt(self, notebook):
        printTab = ttk.Frame(notebook)
        notebook.add(printTab, text="Complete")
        printOuter = Frame(printTab, bg="#387647")
        printOuter.pack(expand=True, fill="both")

        Button(printOuter, text="Finalize Order", height=20, width=40, command=self.PrintOut).pack()

    def Quit(self, notebook, cashierWindow):
        QuitTab = ttk.Frame(notebook)
        notebook.add(QuitTab, text="Leave")
        QuitOuter = Frame(QuitTab, bg="#387647")
        QuitOuter.pack(expand=True, fill="both")

        def exit():
            cashierWindow.destroy()

        Button(QuitOuter, text="Leave?", height=20, width=40, command=exit).pack()

    def Settings(self, notebook):
        settingsTab = ttk.Frame(notebook)
        notebook.add(settingsTab, text="Menu Settings")
        settingsOuter = Frame(settingsTab, bg="green")
        settingsOuter.pack(expand=True, fill="both")

        SettingsNotebook = ttk.Notebook(settingsOuter)
        SettingsNotebook.pack(expand=True, fill="both")

        self.AddItems(SettingsNotebook)
        self.DeletingItems(SettingsNotebook)
        self.UpdateItems(SettingsNotebook)

    def checkIngredientRollback(self, name):
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

                    if ing_id in ingredient_lookup:
                        ingredient_lookup[ing_id]['stock'] += qty

                    if ing_id in self.totalIngredients:
                        self.totalIngredients[ing_id] -= qty
                        if self.totalIngredients[ing_id] < 0:
                            self.totalIngredients[ing_id] = 0  
                    else:
                        self.totalIngredients[ing_id] = 0
                break
        else:
            print(f"No recipe found for dish ID {dishID}.")
            return False

        print("Updated total ingredients used after rollback:")
        for ing_id, qty in self.totalIngredients.items():
            ing_name = ingredient_lookup.get(ing_id, {}).get('name', f'ID {ing_id}')
            print(f"- {ing_name}: {qty}")

        return True
    def checkIngredientRequired(self, name):

        f_data = self.get_item()

        self.menu = f_data['menu']
        inventory = f_data['inventory']
        ingredients = inventory['ingredients']
        recipes = inventory['recipes']

        dishID = next((item['dish_id'] for item in self.menu["menu_items"] if item['name'] == name), None)
        if dishID is None:
            print(f"Dish '{name}' not found in menu.")
            return False

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
        return True

    def printCols(self, CWindow, innerFrame, image_path, dish, price):
        if dish not in self.dish_quantities:
            self.dish_quantities[dish] = 0

        frame = Frame(innerFrame, bg="#fff5ec")
        frame.pack(fill="both", expand=True)

        if os.path.exists(image_path):
            try:
                img = PhotoImage(file=image_path)
                self.image_refs.append(img)
                Label(frame, image=img, bg="#fff5ec").pack()
            except Exception:
                Label(frame, text="Error loading image", bg="#fff5ec").pack()
        else:
            Label(frame, text="Image not found", bg="#fff5ec").pack()

        Label(frame, text=f"{dish}\n${price:.2f}", font=("Times New Roman", 10, "bold"), bg="#fff5ec").pack()

        qty_frame = Frame(frame, bg="#fff5ec")
        qty_frame.pack()

        qty_var = StringVar(value=str(self.dish_quantities[dish]))
        qty_label = Label(qty_frame, textvariable=qty_var, width=3, bg="#fff5ec", font=("Arial", 12))
        qty_label.pack(side="left")

        def increase():
            if not self.checkIngredientRequired(dish):
                return 
            self.dish_quantities[dish] += 1
            qty_var.set(str(self.dish_quantities[dish]))
            self.cart.append([dish, price])
            self.total += price
            self.refresh_cart(CWindow)

        def decrease():
            if self.dish_quantities[dish] > 0:
                self.dish_quantities[dish] -= 1
                qty_var.set(str(self.dish_quantities[dish]))

                for i in range(len(self.cart)):
                    if self.cart[i][0] == dish:
                        self.total -= self.cart[i][1]
                        del self.cart[i]
                        break

                self.checkIngredientRollback(dish)
                self.refresh_cart(CWindow)


        Button(qty_frame, text="-", command=decrease, width=2).pack(side="left", padx=2)
        Button(qty_frame, text="+", command=increase, width=2).pack(side="left", padx=2)

    def refresh_all_tab(self):
        f_data = self.get_item()
        self.menu =  f_data['menu']
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        cols = 3
        row_index = 0

        menu_by_category = defaultdict(list)
        for item in self.menu["menu_items"]:
            menu_by_category[item["category"]].append((item["name"], item["image"], item["price"]))

        for category, items_list in menu_by_category.items():
            category_label = Label(self.scrollable_frame, text=category, font=("Showcard Gothic", 20, "bold"),
                                   anchor="w", bg="#387647", fg="#fff5ec")
            category_label.grid(row=row_index, column=0, columnspan=cols, sticky="w", pady=(10, 0))
            row_index += 1

            for i, (food, image_path, price) in enumerate(items_list):
                col = i % cols
                sub_row = i // cols

                innerFrame = Frame(self.scrollable_frame, bg="#fff5ec", bd=2, relief=GROOVE)
                innerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

                self.printCols(self.CWindow, innerFrame, image_path, food, price)

            row_index += (len(items_list) + cols - 1) // cols

        for i in range(cols):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)

    def refresh_category_tab(self, category):
        f_data = self.get_item()
        self.menu =  f_data['menu']

        frame = self.category_frames[category]

        for widget in frame.winfo_children():
            widget.destroy()

        items_list = [
            (item["name"], item["image"], item["price"])
            for item in self.menu["menu_items"]
            if item["category"] == category
        ]

        subCols = 3
        row_index = 0

        for i, (food, image_path, price) in enumerate(items_list):
            col = i % subCols
            sub_row = i // subCols

            subinnerFrame = Frame(frame, bg="#fff5ec", bd=2, relief=GROOVE)
            subinnerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

            self.printCols(self.CWindow, subinnerFrame, image_path, food, price)

        for i in range(subCols):
            frame.grid_columnconfigure(i, weight=1)

    def scrollBar(self, my_canvas, tab):
        my_scrollbar = Scrollbar(tab, orient=VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill=Y)
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_scrollbar.config(command=my_canvas.yview)

    def report(self, notebook):
        f_data = self.get_item()
        self.orders = f_data['order']

        reportTab = ttk.Frame(notebook)
        notebook.add(reportTab, text="report")
        reportOuter = Frame(reportTab, bg="green")
        reportOuter.pack(expand=True, fill="both")

        reportcanvas = Canvas(reportOuter, bg="#387647", highlightthickness=0)
        reportcanvas.pack(side=LEFT, fill="both", expand=True)
        self.scrollBar(reportcanvas, reportOuter)

        report_scrollable_frame = Frame(reportcanvas, bg="#387647")
        reportcanvas.create_window((0, 0), window=report_scrollable_frame, anchor="nw", tags="frame")
        report_scrollable_frame.bind("<Configure>", lambda e: reportcanvas.configure(scrollregion=reportcanvas.bbox("all")))

        def resize_scrollable_frame(event):
            canvas_width = event.width
            reportcanvas.itemconfig("frame", width=canvas_width)

        reportcanvas.bind("<Configure>", resize_scrollable_frame)

        insideCanvas = Canvas(report_scrollable_frame, width=320, height=320, bg="#387647", highlightthickness=0, bd=0)
        combined_results = {}

        for item in self.orders["order_items"]:
            dish_id = item["dish_id"]
            quantity = item["quantity"]
            unit_price = item["unit_price"]

            if dish_id in combined_results:
                combined_results[dish_id][0] += quantity
            else:
                combined_results[dish_id] = [int(quantity), float(unit_price)]

        totalAmountSold = 0

        for dish_id, (quantity, unit_price) in combined_results.items():
            totalAmountSold += (unit_price * quantity)

        colors = ["#b9752f", "#4a2311", "#d13837", "#339c48", "#566a0e", "#702e09", "#b23a20", "#f89f3f", "#cd752b", "#6b9835"]
        totaldegree = 0
        Label(report_scrollable_frame, text="MOST MONEY MADE", font=("Helvetica", 14, "underline"), bg="#387647", fg="white").grid(row=0, column=0)
        insideCanvas.grid(row=1, column=0, rowspan=7)
        Label(report_scrollable_frame, text="Ranking", font=("Helvetica", 14, "underline"), bg="#387647", fg="white").grid(row=0, column=1, columnspan=12)

        ranking_list = sorted(
            combined_results.items(),
            key=lambda item: item[1][0] * item[1][1],
            reverse=True
        )

        columns_per_row = 3
        cols_per_dish = 4
        num = 1
        for y, (dish_id, (quantity, unit_price)) in enumerate(ranking_list):
            degree = (quantity * unit_price / totalAmountSold) * 360
            color = colors[y % len(colors)]
            bgColor = "#f6d7d9"
            insideCanvas.create_arc(20, 20, 300, 300,
                                    start=totaldegree, extent=degree, style=PIESLICE,
                                    fill=color, outline="black")
            totaldegree += degree

            row = (y // columns_per_row) + 1
            base_col = ((y % columns_per_row) * cols_per_dish) + 1

            Label(report_scrollable_frame, text=f"NO.{num}", font=("Helvetica", 14),
                  bg=bgColor, fg=color).grid(row=row, column=base_col, sticky="nsew")

            Label(report_scrollable_frame, text=f"ID:{dish_id}", font=("Helvetica", 14),
                  bg=bgColor, fg=color).grid(row=row, column=base_col + 1, sticky="nsew")

            Label(report_scrollable_frame, text=f"quantity:{quantity}", font=("Helvetica", 14),
                  bg=bgColor, fg=color).grid(row=row, column=base_col + 2, sticky="nsew")

            Label(report_scrollable_frame, text=f"${quantity * unit_price:.2f}", font=("Helvetica", 14),
                  bg=bgColor, fg=color).grid(row=row, column=base_col + 3, sticky="nsew")

            num += 1

        for i in range(columns_per_row * cols_per_dish):
            if i % 4 in [1, 3]:
                report_scrollable_frame.grid_columnconfigure(i, weight=1)
            else:
                report_scrollable_frame.grid_columnconfigure(i, weight=0)

def cashier_interface(app,MainWindow):
    f_data = app.get_item()
    menu =  f_data['menu']

    app.window = Toplevel(MainWindow)
    app.notebook = ttk.Notebook(app.window)
    tab = Frame(app.notebook)
    app.my_canvas = Canvas(tab)
    app.my_canvas.pack(side=LEFT, fill="both", expand=True)
    app.scrollBar(app.my_canvas, tab)

    app.CWindow = Toplevel(app.window)

    app.scrollable_frame = Frame(app.my_canvas, bg="#387647")
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
    for category, items_list in menu_by_category.items():
        category_label = Label(app.scrollable_frame, text=category, font=("Showcard Gothic", 20, "bold"),
                               anchor="w", bg="#387647", fg="#fff5ec")
        category_label.grid(row=row_index, column=0, columnspan=cols, sticky="w", pady=(10, 0))
        row_index += 1

        for i, (food, image_path, price) in enumerate(items_list):
            col = i % cols
            sub_row = i // cols

            innerFrame = Frame(app.scrollable_frame, bg="#fff5ec", bd=2, relief=GROOVE)
            innerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

            app.printCols(app.CWindow, innerFrame, image_path, food, price)

        row_index += (len(items_list) + cols - 1) // cols

    for i in range(cols):
        app.scrollable_frame.grid_columnconfigure(i, weight=1)
    subCols = 3
    for category, items_list in menu_by_category.items():
        subTab = ttk.Frame(app.notebook)
        app.notebook.add(subTab, text=category)
        subOuter = Frame(subTab, bg="#387647")
        subOuter.pack(expand=True, fill="both")
        app.category_frames[category] = subOuter

        for i, (food, image_path, price) in enumerate(items_list):
            col = i % cols
            sub_row = i // cols

            innerFrame = Frame(subOuter, bg="#fff5ec", bd=2, relief=GROOVE)
            innerFrame.grid(row=row_index + sub_row, column=col, padx=5, pady=5, sticky="nsew")

            app.printCols(app.CWindow, innerFrame, image_path, food, price)

        row_index += (len(items_list) + cols - 1) // cols

        for i in range(subCols):
            subOuter.grid_columnconfigure(i, weight=1)
    app.Settings(app.notebook)
    app.PrintReceipt(app.notebook)
    app.report(app.notebook)
    app.Quit(app.notebook, app.window)