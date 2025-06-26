import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
import json
import os
from AES import KeyExchange, pseudo_encrypt, pseudo_decrypt
from DataBase import load, write, str_to_json 

class Chef:
    def __init__(self, system, panel):
        self.system = system
        self.panel = panel
        self.kex = KeyExchange()
        self.shared_key = None

    """Atbash Decryption Function"""
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

    def recipe_management(self):
        window_recipe = tk.Toplevel()
        window_recipe.title("Recipe Management")
        window_recipe.geometry("400x500")
        
        button1 = tk.Button(window_recipe, text="Create Recipe", command=lambda: self.create_rcp1())
        button1.grid(row=0, column=0)
        button2 = tk.Button(window_recipe, text="Update Recipe", command=lambda: self.update_rcp())
        button2.grid(row=0, column=1)
        button3 = tk.Button(window_recipe, text="Delete Recipe", command=lambda: self.delete_rcp1())
        button3.grid(row=0, column=2)

    def create_rcp1(self):
        window = tk.Toplevel()
        window.title("Create Recipe")

        ing = self.get_item()["ingr"]
        new_id = ing["recipes"][-1]["dish_id"]+1

        label1 = tk.Label(window, text="Dish Name: ")
        label1.grid(row=0, column=0)
        name = tk.Entry(window)
        name.grid(row=0, column=1)
        
        label2 = tk.Label(window, text="Category: ")
        label2.grid(row=1, column=0)
        category = tk.Entry(window)
        category.grid(row=1, column=1)

        label3 = tk.Label(window, text="Price: ")
        label3.grid(row=2, column=0)
        price = tk.Entry(window)
        price.grid(row=2, column=1)

        label4 = tk.Label(window, text="Enter Number of Ingredient Required: ")
        label4.grid(row=3, column=0)
        num = tk.Entry(window)
        num.grid(row=3, column=1)
        button1 = tk.Button(window, text="Next", command=lambda: self.create_rcp2(new_id, name.get(), category.get(), round(float(price.get()), 2), int(num.get())))
        button1.grid(row=4)

    def create_rcp2(self, new_id, name, category, price, num):
        menu = self.get_item()["menu"]

        new_menu = {"dish_id": new_id, "name": name, "image": None, "category": category, "price": price}
        menu["menu_items"].append(new_menu)

        self.system.chf_write_menu(self, menu)
        
        window = tk.Toplevel()
        window.title("Create Recipe")
        
        title = tk.Label(window, text=name)
        title.grid(row=0, column=0)
        
        entry_ls = []
        quantity_ls = []
        for i in range(1, int(num)+1):
            
            label1 = tk.Label(window, text=f"Ingredient {i}: ")
            label1.grid(row=i, column=0)
            entry1 = tk.Entry(window)
            entry1.grid(row=i, column=1)
            entry_ls.append(entry1)

            label2 = tk.Label(window, text="Quantity: ")
            label2.grid(row=i, column=2)
            entry2 = tk.Entry(window)
            entry2.grid(row=i, column=3)
            quantity_ls.append(entry2)

        button1 = tk.Button(window, text="Record", command=lambda: self.get_ing(name, entry_ls, quantity_ls, window))
        button1.grid()

    def get_ing(self, name, entry_ls, quantity_ls, window):
        ing = self.get_item()["ingr"]
        
        new_id = ing["recipes"][-1]["dish_id"]+1
        new_ing = []

        for i in range(len(entry_ls)):
            temp_ing = {}

            valid = False
            for j in ing["ingredients"]:
                if j["name"] == entry_ls[i].get():
                    id = j["ingredient_id"]
                    valid = True
                    break
            
            if valid == False:
                messagebox.showerror("Not Found", f"{entry_ls[i].get()} is not found.")
                return

            temp_ing["ingredient_id"] = id
            temp_ing["quantity"] = quantity_ls[i].get()
            new_ing.append(temp_ing)
        
        new_rcp = {"dish_id": new_id, "ingredients": new_ing}
        ing["recipes"].append(new_rcp)

        self.system.chf_write_ing(self, ing)
        messagebox.showinfo("Recorded", f"{name} is recorded.")
        window.destroy()

    def update_rcp(self):
        window = tk.Toplevel()
        window.title("Update Recipe")

        label1 = tk.Label(window, text="Dish Name: ")
        label1.grid(row=0, column=0)
        name = tk.Entry(window)
        name.grid(row=0, column=1)

        label2 = tk.Label(window, text="Enter Number of Ingredient Required : ")
        label2.grid(row=1, column=0)
        num = tk.Entry(window)
        num.grid(row=1, column=1)
        
        button = tk.Button(window, text="Next", command=lambda: self.check_rcp(name.get(), num.get(), window))
        button.grid(row=2, column=0)

    def check_rcp(self, name, num, window):
        menu = self.get_item()["menu"]
        
        valid = False
        for i in menu["menu_items"]:
            if name == i["name"]:
                valid = True
                break

        if valid == False:
            messagebox.showerror("Not Found", f"{name} is not found.")
        else:
            title = tk.Label(window, text=name)
            title.grid(row=3, column=0)
            
            entry_ls = []
            quantity_ls = []
            for i in range(1, int(num)+1):
                
                label1 = tk.Label(window, text=f"Ingredient {i}: ")
                label1.grid(row=i+3, column=0)
                entry1 = tk.Entry(window)
                entry1.grid(row=i+3, column=1)
                entry_ls.append(entry1)

                label2 = tk.Label(window, text="Quantity: ")
                label2.grid(row=i+3, column=2)
                entry2 = tk.Entry(window)
                entry2.grid(row=i+3, column=3)
                quantity_ls.append(entry2)

            button1 = tk.Button(window, text="Record", command=lambda: self.del_get_ing(name, entry_ls, quantity_ls, window))
            button1.grid(row=int(num)+4, column=0)

    def del_get_ing(self, name, entry_ls, quantity_ls, window):
        self.delete_rcp2(name)
        menu = self.get_item()["menu"]
        dish_id = None
        for item in menu["menu_items"]:
            if item["name"] == name:
                dish_id = item["dish_id"]
                break
        
        if dish_id:
            self.create_recipe_ingredients(dish_id, name, entry_ls, quantity_ls, window)

    def create_recipe_ingredients(self, dish_id, name, entry_ls, quantity_ls, window):
        ing = self.get_item()["ingr"]
        new_ing = []

        for i in range(len(entry_ls)):
            temp_ing = {}

            valid = False
            for j in ing["ingredients"]:
                if j["name"] == entry_ls[i].get():
                    id = j["ingredient_id"]
                    valid = True
                    break
            
            if valid == False:
                messagebox.showerror("Not Found", f"{entry_ls[i].get()} is not found.")
                return

            temp_ing["ingredient_id"] = id
            temp_ing["quantity"] = quantity_ls[i].get()
            new_ing.append(temp_ing)
        
        new_rcp = {"dish_id": dish_id, "ingredients": new_ing}
        ing["recipes"].append(new_rcp)

        self.system.chf_write_ing(self, ing)
        messagebox.showinfo("Updated", f"{name} has been updated.")
        window.destroy()

    def delete_rcp1(self):
        window = tk.Toplevel()
        window.title("Delete Recipe")

        label = tk.Label(window, text="Enter Recipe Name: ")
        label.grid(row=0, column=0)
        entry = tk.Entry(window)
        entry.grid(row=0, column=1)

        button = tk.Button(window, text="Delete", command=lambda: self.delete_rcp2(entry.get()))
        button.grid(row=1)

    def delete_rcp2(self, name):
        menu = self.get_item()["menu"]

        valid = False
        dish_id = None
        for i in range(len(menu["menu_items"])):
            if name == menu["menu_items"][i]["name"]:
                dish_id = menu["menu_items"][i]["dish_id"]
                del menu["menu_items"][i]
                valid = True
                break
            
        if valid == False:
            messagebox.showerror("Not Found", f"{name} is not found.")
            return
        else:
            messagebox.showinfo("Deleted", f"{name} has been deleted.")
                
        self.system.chf_write_menu(self, menu)
        
        ing = self.get_item()["ingr"]

        for i in range(len(ing["recipes"])):
            if dish_id == ing["recipes"][i]["dish_id"]:
                del ing["recipes"][i]
                break

        self.system.chf_write_ing(self, ing)

    def inventory_check(self):
        window_inv = tk.Toplevel()
        window_inv.title("Inventory Check")
        window_inv.geometry("900x500")
        window_inv.focus()

        search_bar = tk.Entry(window_inv, width=30)
        search_bar.grid(row=0, column=0)
        
        search_img = PhotoImage(file=("picture\\search.png"))
        search_button = tk.Button(window_inv, command=lambda: self.find_ing(window_inv, search_bar), image=search_img)
        search_button.image = search_img
        search_button.place(x=550, y=100)
        
        canva = tk.Canvas(window_inv)
        scrollbar = tk.Scrollbar(window_inv, orient="vertical", command=canva.yview)
        canva.configure(yscrollcommand=scrollbar.set)

        canva.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        window_inv.grid_rowconfigure(1, weight=1)
        window_inv.grid_columnconfigure(0, weight=1)

        scroll_frame = tk.Frame(canva)
        canva.create_window((0, 0), window=scroll_frame, anchor="nw")

        def on_configure(event):
            canva.configure(scrollregion=canva.bbox("all"))

        scroll_frame.bind("<Configure>", on_configure)
        ing1_img = PhotoImage(file=("picture\\Potatoes.png"))
        ing1 = tk.Button(scroll_frame, text="Potatoes", command=lambda: self.verify("Potatoes"), image=ing1_img)
        ing1.image = ing1_img
        ing1.grid(row=1, column=1)
        ing2_img = PhotoImage(file=("picture\\Truffle Oil.png"))
        ing2 = tk.Button(scroll_frame, text="Truffle Oil", command=lambda: self.verify("Truffle Oil"), image=ing2_img)
        ing2.image = ing2_img
        ing2.grid(row=1, column=2)
        ing3_img = PhotoImage(file=("picture\\Parmesan Cheese.png"))
        ing3 = tk.Button(scroll_frame, text="Parmesan Cheese", command=lambda: self.verify("Parmesan Cheese"), image=ing3_img)
        ing3.image = ing3_img
        ing3.grid(row=1, column=3)
        ing4_img = PhotoImage(file=("picture\\Salt.png"))
        ing4 = tk.Button(scroll_frame, text="Salt", command=lambda: self.verify("Salt"), image=ing4_img)
        ing4.image = ing4_img
        ing4.grid(row=2, column=1)
        ing5_img = PhotoImage(file=("picture\\Chickpeas.png"))
        ing5 = tk.Button(scroll_frame, text="Chickpeas", command=lambda: verify(chf, "Chickpeas"), image=ing5_img)
        ing5.image = ing5_img
        ing5.grid(row=2, column=2)
        ing6_img = PhotoImage(file=("picture\\Heirloom Tomatoes.png"))
        ing6 = tk.Button(scroll_frame, text="Heirloom Tomatoes", command=lambda: verify(chf, "Heirloom Tomatoes"), image=ing6_img)
        ing6.image = ing6_img
        ing6.grid(row=2, column=3)
        ing7_img = PhotoImage(file=("picture\\Burrata.png"))
        ing7 = tk.Button(scroll_frame, text="Burrata", command=lambda: verify(chf, "Burrata"), image=ing7_img)
        ing7.image = ing7_img
        ing7.grid(row=3, column=1)
        ing8_img = PhotoImage(file=("picture\\Salmon.png"))
        ing8 = tk.Button(scroll_frame, text="Salmon", command=lambda: verify(chf, "Salmon"), image=ing8_img)
        ing8.image = ing8_img
        ing8.grid(row=3, column=2)
        ing9_img = PhotoImage(file=("picture\\Short Ribs.png"))
        ing9 = tk.Button(scroll_frame, text="Short Ribs", command=lambda: verify(chf, "Short Ribs"), image=ing9_img)
        ing9.image = ing9_img
        ing9.grid(row=3, column=3)
        ing10_img = PhotoImage(file=("picture\\Miso Paste.png"))
        ing10 = tk.Button(scroll_frame, text="Miso Paste", command=lambda: verify(chf, "Miso Paste"), image=ing10_img)
        ing10.image = ing10_img
        ing10.grid(row=4, column=1)
        ing11_img = PhotoImage(file=("picture\\Cod.png"))
        ing11 = tk.Button(scroll_frame, text="Cod", command=lambda: verify(chf, "Cod"), image=ing11_img)
        ing11.image = ing11_img
        ing11.grid(row=4, column=2)
        ing12_img = PhotoImage(file=("picture\\Burger Buns.png"))
        ing12 = tk.Button(scroll_frame, text="Burger Buns", command=lambda: verify(chf, "Burger Buns"), image=ing12_img)
        ing12.image = ing12_img
        ing12.grid(row=4, column=3)
        ing13_img = PhotoImage(file=("picture\\Chicken Breast.png"))
        ing13 = tk.Button(scroll_frame, text="Chicken Breast", command=lambda: verify(chf, "Chicken Breast"), image=ing13_img)
        ing13.image = ing13_img
        ing13.grid(row=5, column=1)
        ing14_img = PhotoImage(file=("picture\\Matcha Powder.png"))
        ing14 = tk.Button(scroll_frame, text="Matcha Powder", command=lambda: verify(chf, "Matcha Powder"), image=ing14_img)
        ing14.image = ing14_img
        ing14.grid(row=5, column=2)
        ing15_img = PhotoImage(file=("picture\\Lemon Juice.png"))
        ing15 = tk.Button(scroll_frame, text="Lemon Juice", command=lambda: verify(chf, "Lemon Juice"), image=ing15_img)
        ing15.image = ing15_img
        ing15.grid(row=5, column=3)
        ing16_img = PhotoImage(file=("picture\\Chai Mix.png"))
        ing16 = tk.Button(scroll_frame, text="Chai Mix", command=lambda: verify(chf, "Chai Mix"), image=ing16_img)
        ing16.image = ing16_img
        ing16.grid(row=6, column=1)
        ing17_img = PhotoImage(file=("picture\\Chocolate.png"))
        ing17 = tk.Button(scroll_frame, text="Chocolate", command=lambda: verify(chf, "Chocolate"), image=ing17_img)
        ing17.image = ing17_img
        ing17.grid(row=6, column=2)
        ing18_img = PhotoImage(file=("picture\\Lemon Curd.png"))
        ing18 = tk.Button(scroll_frame, text="Lemon Curd", command=lambda: verify(chf, "Lemon Curd"), image=ing18_img)
        ing18.image = ing18_img
        ing18.grid(row=6, column=3)
        ing19_img = PhotoImage(file=("picture\\Caramel.png"))
        ing19 = tk.Button(scroll_frame, text="Caramel", command=lambda: verify(chf, "Caramel"), image=ing19_img)
        ing19.image = ing19_img
        ing19.grid(row=7, column=1)
        ing20_img = PhotoImage(file=("picture\\Cheesecake Base.png"))
        ing20 = tk.Button(scroll_frame, text="Cheesecake Base", command=lambda: verify(chf, "Cheesecake Base"), image=ing20_img)
        ing20.image = ing20_img
        ing20.grid(row=7, column=2)
        ing21_img = PhotoImage(file=("picture\\Portobello Mushrooms.png"))
        ing21 = tk.Button(scroll_frame, text="Portobello Mushrooms", command=lambda: verify(chf, "Portobello Mushrooms"), image=ing21_img)
        ing21.image = ing21_img
        ing21.grid(row=7, column=3)
        ing22_img = PhotoImage(file=("picture\\Lavender Syrup.png"))
        ing22 = tk.Button(scroll_frame, text="Lavender Syrup", command=lambda: verify(chf, "Lavender Syrup"), image=ing22_img)
        ing22.image = ing22_img
        ing22.grid(row=8, column=1)
        ing23_img = PhotoImage(file=("picture\\Milk.png"))
        ing23 = tk.Button(scroll_frame, text="Milk", command=lambda: verify(chf, "Milk"), image=ing23_img)
        ing23.image = ing23_img
        ing23.grid(row=8, column=2)
        ing24_img = PhotoImage(file=("picture\\Sugar.png"))
        ing24 = tk.Button(scroll_frame, text="Sugar", command=lambda: verify(chf, "Sugar"), image=ing24_img)
        ing24.image = ing24_img
        ing24.grid(row=8, column=3)
        ing25_img = PhotoImage(file=("picture\\Flour.png"))
        ing25 = tk.Button(scroll_frame, text="Flour", command=lambda: verify(chf, "Flour"), image=ing25_img)
        ing25.image = ing25_img
        ing25.grid(row=9, column=1)
        ing26_img = PhotoImage(file=("picture\\Eggs.png"))
        ing26 = tk.Button(scroll_frame, text="Eggs", command=lambda: verify(chf, "Eggs"), image=ing26_img)
        ing26.image = ing26_img
        ing26.grid(row=9, column=2)
        ing27_img = PhotoImage(file=("picture\\Butter.png"))
        ing27 = tk.Button(scroll_frame, text="Butter", command=lambda: verify(chf, "Butter"), image=ing27_img)
        ing27.image = ing27_img
        ing27.grid(row=9, column=3)
        ing28_img = PhotoImage(file=("picture\\Vanilla Extract.png"))
        ing28 = tk.Button(scroll_frame, text="Vanilla Extract", command=lambda: verify(chf, "Vanilla Extract"), image=ing28_img)
        ing28.image = ing28_img
        ing28.grid(row=10, column=1)
        ing29_img = PhotoImage(file=("picture\\Baking Chocolate.png"))
        ing29 = tk.Button(scroll_frame, text="Baking Chocolate", command=lambda: verify(chf, "Baking Chocolate"), image=ing29_img)
        ing29.image = ing29_img
        ing29.grid(row=10, column=2)
        ing30_img = PhotoImage(file=("picture\\Cream Cheese.png"))
        ing30 = tk.Button(scroll_frame, text="Cream Cheese", command=lambda: verify(chf, "Cream Cheese"), image=ing30_img)
        ing30.image = ing30_img
        ing30.grid(row=10, column=3)

    def find_ing(self, window, search_bar):
        for widget in window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") not in ["Search"]:
                widget.destroy()
        
        name = search_bar.get()
        ing = self.get_item()["ingr"]

        ing_valid = False
        for i in ing["ingredients"]:
            if name == i["name"]:
                result_img = PhotoImage(file=f"picture\\{name}.png")
                result = tk.Button(window, command=lambda: self.verify(i["name"]), image=result_img)
                result.image = result_img
                result.grid(row=1, column=0, pady=20)
                ing_valid = True
                break

        if ing_valid == False:
            label = tk.Label(window, text="Ingredient Not Found", font=("Arial", 12))
            label.grid(row=1, column=0, pady=120)

    def verify(self, name):
        ing = self.get_item()["ingr"]

        for i in ing["ingredients"]:
            if i["name"] == name:
                if i["stock"] > 0:
                    availability = "available"
                else:
                    availability = "not available"
                quantity = i["stock"]
                unit = i["unit"]
                break
        
        messagebox.showinfo(name, f"{name} is {availability}, {quantity} {unit} left")

    def equipment_management(self):
        window_eqp = tk.Toplevel()
        window_eqp.title("Equipment Management")
        window_eqp.geometry("400x300")

        label1 = tk.Label(window_eqp, text="Equipment Name:")
        label1.grid(row=0, column=0)
        entry1 = tk.Entry(window_eqp)
        entry1.grid(row=0, column=1, padx=10, pady=10)
        
        label2 = tk.Label(window_eqp, text="Status: ")
        label2.grid(row=1, column=0)
        status_ls = ["Broken", "Malfunctioning", "Missing"]
        status = tk.StringVar()
        status.set("Select Status")
        dropdown = tk.OptionMenu(window_eqp, status, *status_ls)
        dropdown.grid(row=1, column=1, padx=10)

        button1 = tk.Button(window_eqp, text="View Checklist", command=lambda: self.checkls())
        button1.grid(row=2, column=0, pady=20)

        button2 = tk.Button(window_eqp, text="Add Report", command=lambda: self.record_eqp(entry1, status))
        button2.grid(row=2, column=1, pady=20)
        
        button3 = tk.Button(window_eqp, text="Remove Equipment", command=lambda: self.remove_equipment())
        button3.grid(row=2, column=2, pady=20)

        button4 = tk.Button(window_eqp, text="Exit", command=lambda: window_eqp.destroy())
        button4.grid(row=3, column=1, pady=10)

    def checkls(self):
        window = tk.Toplevel()
        window.title("Equipment Checklist")
        window.geometry("600x400")
        
        eqp = self.get_item()["eqp"]
        
        table_frame = tk.Frame(window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        column_title = ("Name", "Status")
        table = ttk.Treeview(table_frame, columns=column_title, show="headings", height=15)
        
        table.heading("Name", text="Equipment Name")
        table.heading("Status", text="Status")
        table.column("Name", width=200)
        table.column("Status", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for i in range(len(eqp["reports"])):
            for key, value in eqp["reports"][i].items():
                table.insert("", "end", values=(key, value))
        
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        remove_button = tk.Button(button_frame, text="Remove Selected", 
                                command=lambda: self.remove_selected_equipment(table, window))
        remove_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = tk.Button(button_frame, text="Refresh", 
                                 command=lambda: self.refresh_checklist(table))
        refresh_button.pack(side=tk.LEFT, padx=5)

    def remove_equipment(self):
        window = tk.Toplevel()
        window.title("Remove Equipment")
        window.geometry("300x150")
        
        label = tk.Label(window, text="Enter Equipment Name to Remove:")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        entry = tk.Entry(window, width=25)
        entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        remove_button = tk.Button(window, text="Remove", 
                                command=lambda: self.remove_equipment_by_name(entry.get(), window))
        remove_button.grid(row=2, column=0, padx=5, pady=10)
        
        cancel_button = tk.Button(window, text="Cancel", command=window.destroy)
        cancel_button.grid(row=2, column=1, padx=5, pady=10)

    def remove_selected_equipment(self, table, parent_window):
        selection = table.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
        
        item = table.item(selection[0])
        equipment_name = item['values'][0]
        
        result = messagebox.askyesno("Confirm Removal", 
                                   f"Are you sure you want to remove '{equipment_name}' from the checklist?")
        
        if result:
            self.remove_equipment_by_name(equipment_name, None)
            self.refresh_checklist(table)

    def remove_equipment_by_name(self, equipment_name, window):
        if not equipment_name.strip():
            messagebox.showerror("Error", "Please enter an equipment name.")
            return
        
        eqp = self.get_item()["eqp"]
        
        removed = False
        for i, report in enumerate(eqp["reports"]):
            if equipment_name in report:
                del eqp["reports"][i]
                removed = True
                break
        
        if removed:
            self.system.chf_write_eqp(self, eqp)
            messagebox.showinfo("Success", f"'{equipment_name}' has been removed from the checklist.")
            if window:
                window.destroy()
        else:
            messagebox.showerror("Not Found", f"Equipment '{equipment_name}' not found in the checklist.")

    def refresh_checklist(self, table):
        for item in table.get_children():
            table.delete(item)
        
        eqp = self.get_item()["eqp"]
        
        for i in range(len(eqp["reports"])):
            for key, value in eqp["reports"][i].items():
                table.insert("", "end", values=(key, value))

    def record_eqp(self, entry, status):
        equipment_name = entry.get().strip()
        status_value = status.get()
        
        if not equipment_name:
            messagebox.showerror("Error", "Please enter an equipment name.")
            return
        
        if status_value == "Select Status":
            messagebox.showerror("Error", "Please select a status.")
            return
        
        eqp = self.get_item()["eqp"]
        
        equipment_exists = False
        for report in eqp["reports"]:
            if equipment_name in report:
                equipment_exists = True
                break
        
        if equipment_exists:
            result = messagebox.askyesno("Equipment Exists", 
                                       f"'{equipment_name}' already exists in the checklist. Do you want to update its status?")
            if result:
                for report in eqp["reports"]:
                    if equipment_name in report:
                        report[equipment_name] = status_value
                        break
                messagebox.showinfo("Updated", f"'{equipment_name}' status updated to '{status_value}'.")
            else:
                return
        else:
            item = {equipment_name: status_value}
            eqp["reports"].append(item)
            messagebox.showinfo("Added", f"'{equipment_name}' has been added to the checklist with status '{status_value}'.")
        
        self.system.chf_write_eqp(self, eqp)
        
        entry.delete(0, tk.END)
        status.set("Select Status")

def chef_interface(chf, MainWindow):
    window1 = tk.Toplevel(MainWindow)
    window1.title("Chef")
    window1.geometry("800x400")

    label1 = tk.Label(window1, text = "CHEF INTERFACE")
    label1.pack(pady=10)

    button1 = tk.Button(window1, text = "Recipe Management", command=lambda: chf.recipe_management(), width=20, height=5)
    button1.place(x=60, y=60)

    button2 = tk.Button(window1, text = "Inventory Check", command=lambda: chf.inventory_check(), width=20, height=5)
    button2.place(x=320, y=60)

    button3 = tk.Button(window1, text = "Equipment Management", command=lambda: chf.equipment_management(), width=20, height=5)
    button3.place(x=590, y=60)

    button4 = tk.Button(window1, text="Logout", command=window1.destroy)
    button4.place(x=370, y=200)
  
    window1.mainloop()