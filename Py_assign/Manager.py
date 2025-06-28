from AES import KeyExchange, pseudo_encrypt, pseudo_decrypt
from DataBase import load, write, str_to_json
import re
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import os
from collections import Counter, defaultdict
from LinearRegression import Model
from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption

class Manager:
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

    """System Administration"""
    def approve(self, accID):
        f_data = self.get_item()
        users_available = f_data['user']
        for user in self.panel.pending_users:
            if user['accID'] == accID:
                users_available['users'].append(user)
                self.system.write_users(self, users_available)
                self.panel.pending_users.remove(user)
                messagebox.showinfo(message=f"The administrator approved the registration of user: {accID}.")
                return
        messagebox.showerror(message=f"No pending user named {accID} found.")

    def delete(self, accID):
        f_data = self.get_item()
        users_available = f_data['user']
        users = users_available.get('users', [])

        new_users = [u for u in users if u.get('accID') != accID]

        if len(new_users) < len(users):
            users_available['users'] = new_users
            self.system.write_users(self, users_available)

            messagebox.showinfo(message=f"The administrator has removed user: {accID}.")
        else:
            messagebox.showerror(message=f"No user named {accID} found.")

    def reject(self, accID):
        for user in self.panel.pending_users:
            if user['accID'] == accID:
                self.panel.pending_users.remove(user)
                messagebox.showinfo(message=f"The administrator denied registration for user {accID}.")
                return
        messagebox.showerror(message=f"No pending user named {accID} found.")

    def list_approved(self,ManagerWindow):
        ApprvFrame = Frame(ManagerWindow)
        ApprvFrame.pack(padx=10, pady=10, fill="both", expand=True)

        f_data = self.get_item()
        users_available = f_data['user']
        users = users_available.get('users', [])
        TempApprvList = []
        for user in users:
            TempApprvList.append(user['accID'])
            TempApprvList.append(user['role'])
        TableCreator(ApprvFrame,"List of approved users:",("Account ID","Role"),TempApprvList)
        return users, ApprvFrame

    def modify_user(self, accID, new_role=None, new_password=None):
        f_data = self.get_item()
        users_available = f_data['user']
        for user in users_available['users']:
            if user['accID'] == accID:
                if new_role:
                    user['role'] = new_role
                if new_password:
                    user['pass'] = new_password
                self.system.write_users(self, users_available)
                messagebox.showinfo(message=f"User updated: {accID}")
                return
        messagebox.showerror(message=f"User {accID} not found")

    """Order Management"""
    def list_pending_orders(self, ManagerWindow):
        pending_order_Frame = Frame(ManagerWindow)
        pending_order_Frame.pack(padx=10, pady=10, fill="both", expand=True)

        f_data = self.get_item()
        orders_data = f_data['order']
        pending = [o for o in orders_data['orders'] if o['status'].lower() != 'completed']
        pending_order_List = []
        if not pending:
            Label(pending_order_Frame, text="There are currently no outstanding orders.").pack()
        else:
            for o in pending:
                pending_order_List.append(o['order_id'])
                pending_order_List.append(o['customer_id'])
                pending_order_List.append(o['order_time'])
                pending_order_List.append(o['status'])
                pending_order_List.append(o['total'])

            TableCreator(pending_order_Frame,"List of uncompleted orders:",("OrderID","CustomerID","Time","Status","Amount"),pending_order_List)
        return pending, pending_order_Frame

    def update_order_status(self, order_id, new_status):
        f_data = self.get_item()
        orders_data = f_data['order']
        inventory = f_data['inventory']
        ingredients = inventory['ingredients']
        recipes = inventory['recipes']
    
        for idx, o in enumerate(orders_data['orders']):
            if o['order_id'] != int(order_id):
                continue
    
            old_status = o.get('status')
    
            if old_status == "In progress" and new_status == "Completed":
                dishes = [(it["dish_id"], it["quantity"]) for it in orders_data["order_items"] if it["order_id"] == o["order_id"]] 
                for dish_id, qty in dishes:
                    recipe = next((r for r in recipes if r["dish_id"] == dish_id), None)
                    if not recipe:
                        continue
                    for ing in recipe["ingredients"]:
                        ing_id = ing["ingredient_id"]
                        need_qty = ing["quantity"] * qty
                        ing_obj = next((x for x in ingredients if x["ingredient_id"] == ing_id), None)
                        if not ing_obj:
                            continue
                        ing_obj["stock"] = round(max(ing_obj["stock"] - need_qty, 0), 2)
                        
                self.system.write_ingredients(self, inventory)

            if new_status == "Cancelled":
                orders_data['orders'].pop(idx)
                self.system.write_mng_orders(self, orders_data)
                messagebox.showinfo(message=f"Cancelled and removed order {order_id}")
                return
    
            o['status'] = new_status
            self.system.write_mng_orders(self, orders_data)
            messagebox.showinfo(message=f"Updated order {order_id} status to {new_status}")
            return

        messagebox.showerror(message=f"Order {order_id} not found")


    """Financial Management"""
    def financial_summary_past_week(self,ManagerWindow):
        FinanceFrame = Frame(ManagerWindow)
        FinanceFrame.pack(padx=10, pady=10, fill="both", expand=True)

        f_data = self.get_item()
        orders_data = f_data['order']
        all_orders = orders_data.get('orders', [])

        now = datetime.now().date()
        week_ago = now - timedelta(days=7)

        recent_orders = []
        for order in all_orders:
            try:
                order_time = datetime.fromisoformat(order['order_time']).date()
            except Exception as e:
                messagebox.showerror(message=f"Order {order['order_id']} time format error: {e}")
                continue

            if week_ago <= order_time <= now and order['status'] == 'Completed':
                recent_orders.append(order)

        if not recent_orders:
            Label(FinanceFrame, text="No orders in the past week.").pack()
            recent_orders = []
            return recent_orders, FinanceFrame

        #print(f"Order statistics in the past week (a total of {len(recent_orders)} orders):")
        Label(FinanceFrame, text=f"Order statistics in the past week (a total of {len(recent_orders)} orders):").pack()
        total_amount = 0.0
        TempFinanceList = []
        for order in recent_orders:
            TempFinanceList.append(order['order_id'])
            TempFinanceList.append(order['customer_id'])
            TempFinanceList.append(order['order_time'])
            TempFinanceList.append(order['status'])
            TempFinanceList.append(order['total'])
            total_amount += order.get('total', 0.0)
        TableCreator(FinanceFrame, "Order statistics", ("OrderID", "CustomerID", "Time", "Status", "Amount"), TempFinanceList)
        Label(FinanceFrame, text=f"Total amount：{total_amount:.2f}").pack()
        return recent_orders, FinanceFrame

    def prediction_output(self,ManagerWindow):
        model = Model()
        return model.print_output(ManagerWindow)

    """Inventory Control"""
    def list_purchase_orders(self,ManagerWindow):
        f_data = self.get_item()
        po_dict = f_data['ingredient_order']
        if isinstance(po_dict, list):
            orders = po_dict
        else:
            orders = po_dict.get("purchase_orders", [])
        TempLPO = []
        for po in orders:
            TempLPO.append(po['purchase_id'])
            TempLPO.append(po['ingredient_name'])
            TempLPO.append(po['ingredient_id'])
            TempLPO.append(po['quantity'])
            TempLPO.append(po['total_price'])
            TempLPO.append(po['order_time'])
            TempLPO.append(po['status'])


        return orders, TableCreator(ManagerWindow,"Current replenishment order",("ReplenishmentID","Food","FoodID","Quantity","Total price","Time","Status"),TempLPO)



    def print_all_ingredients(self, ManagerWindow):
        f_data = self.get_item()
        inv = f_data['inventory']
        thresholds = f_data['threshold']
        columnitems = []
        for item in inv['ingredients']:
            ing_id = item['ingredient_id']
            name = item['name']
            stock = item['stock']
            unit = item['unit']
            if ing_id in thresholds:
                th = thresholds[ing_id]
                if stock <= th:
                    name = f"\033[1m{name}\033[0m"
            columnitems.append(ing_id)
            columnitems.append(name)
            columnitems.append(stock)
            columnitems.append(unit)
        return TableCreator(ManagerWindow,"Ingredients inventory list (stock <= below of threshold will be bolded): ",
                    ('ingredient_id','name','stock','unit'),
                    columnitems)

    def update_purchase_order_status(self, rid, stat):
        f_data      = self.get_item()
        po_dict     = f_data['ingredient_order']
        orders      = po_dict.get("purchase_orders", [])
        inventory   = f_data['inventory']
        ingredients = inventory["ingredients"]

        for od in orders:
            if od['purchase_id'] == int(rid):
                old_status = od['status']
                new_status = stat

                m = re.match(r"([\d\.]+)(\w+)", od['quantity'])
                qty_val = float(m.group(1)) if m else 0.0

                ing_obj = next((x for x in ingredients
                                if x['ingredient_id'] == int(od['ingredient_id'])), None)

                if not ing_obj:
                    continue

                if old_status == "Ordered" and new_status == "Received":
                    if ing_obj:
                        ing_obj["stock"] = round(ing_obj["stock"] + qty_val, 2)

                elif old_status == "Received" and new_status == "Cancelled":
                    if ing_obj:
                        ing_obj["stock"] = round(max(ing_obj["stock"] - qty_val, 0), 2)

                elif old_status == "Received" and new_status == "Ordered":
                    new_status = "Received"
                    
                od['status'] = new_status
                break

        self.system.write_ingredient_order(self, po_dict)
        self.system.write_ingredients(self, inventory)

        messagebox.showinfo(
            message=f"ReplenishmentID {rid} status updated from {old_status} to {new_status}."
        )

    def add_purchase_order(self, ingredient_id, quantity):
        f_data = self.get_item()
        inv = f_data['inventory']
        ing = next((it for it in inv['ingredients'] if it['ingredient_id'] == int(ingredient_id)), None)
        if not ing:
            messagebox.showerror(message=f"Ingredient with ID {ingredient_id} not found.")
            return
        unit = ing['unit']
        price_per_unit = ing['price_per_unit']
        total_price = round(price_per_unit * float(quantity), 2)
        po_data = f_data['ingredient_order']
        next_id = (po_data['purchase_orders'][-1]['purchase_id'] + 1) if po_data['purchase_orders'] else 1
        po = {
            'purchase_id': next_id,
            'ingredient_id': ingredient_id,
            'ingredient_name': ing['name'],
            'quantity': f"{quantity}{unit}",
            'total_price': total_price,
            'order_time': datetime.now().isoformat(),
            'status': 'Ordered'
        }
        po_data['purchase_orders'].append(po)
        self.system.write_ingredient_order(self, po_data)
        print(f"ReplenishmentID {next_id}: Food {ing['name']} (ID:{ingredient_id}), Quantity {quantity}{unit}, Total price {total_price}, Time {po['order_time']}")

    def delete_purchase_order(self, purchase_id):
        f_data = self.get_item()
        po_dict = f_data['ingredient_order']
        if not isinstance(po_dict, dict) or 'purchase_orders' not in po_dict:
            print("There are no replenishment orders to delete.")
            return
        orders = po_dict['purchase_orders']
        for idx, o in enumerate(orders):
            if o['purchase_id'] == purchase_id:
                orders.pop(idx)
                self.system.write_ingredient_order(self, po_dict)
                messagebox.showinfo(message=f"Purchase order {purchase_id} has been deleted")
                return
        messagebox.showerror(message=f"Purchase order {purchase_id} not found")

    """Customer Feedback"""
    def list_feedback(self,ManagerWindow):
        feedbackFrame = Frame(ManagerWindow)
        feedbackFrame.pack(padx=10, pady=10, fill="both", expand=True)

        tempFeedbackList = []
        f_data = self.get_item()
        fk = f_data['feedbacks']
        for fb in fk.get('feedback', []):
            tempFeedbackList.append(fb['feedback_id'])
            tempFeedbackList.append(fb['customer_id'])
            tempFeedbackList.append(fb['dish_id'])
            tempFeedbackList.append(fb['rating'])
            tempFeedbackList.append(fb['comment'])
            tempFeedbackList.append(fb.get('time') or fb.get('Time', 'N/A'))
        TableCreator(feedbackFrame,"Feedbacks",("ID","CustomerID","DishID","Rating","Comment","Time"),tempFeedbackList)
        return feedbackFrame

def manager_interface(mgr,MainWindow):
    ManagerWindow = Toplevel(MainWindow)
    ManagerWindow.attributes('-fullscreen', True)
    while True:
        cmd = Manager_choice(ManagerWindow)
        if cmd == '1':
            choice = tripleOption(ManagerWindow,"Users \nOptions:","Pending approval","Approved","Quit")
            if choice == '1':
                pendingFrame,pending_users = mgr.panel.show_pending(ManagerWindow)
                option = tripleOption(ManagerWindow,"Users(Pending approval): \nOptions:","Approve","Reject","Quit")
                if option == '1':
                    accID = ApprovalPage(ManagerWindow, 'Enter the accID to approve:')
                    if accID:
                        mgr.approve(accID)
                        pendingFrame.destroy()
                    else:
                        messagebox.showwarning("Input", "No account ID entered.")
                elif option == '2':
                    accID = ApprovalPage(ManagerWindow, 'Enter the accID to approve:')
                    if accID:
                        mgr.reject(accID)
                        pendingFrame.destroy()
                    else:
                        messagebox.showwarning("Input", "No account ID entered.")
                elif option == '3':
                    pendingFrame.destroy()
                    continue
                else:
                    messagebox.showerror(message="invalid option")
            elif choice == '2':
                users, AFrame = mgr.list_approved(ManagerWindow)

                choice = tripleOption(ManagerWindow,"[Manager] Users(Approved): \nOptions", "Modify", "Delete","Quit")
                if choice == '1':
                    uid,nr,np = Entry_form(ManagerWindow,"Modify",('Enter the accID to be modified: ','New role (optional): ','New password(optional): '))
                    mgr.modify_user(uid, new_role=nr or None, new_password=np or None)

                    AFrame.destroy()
                elif choice == '2':
                    uid = ApprovalPage(ManagerWindow, 'Enter the accID to delete:')
                    mgr.delete(uid)
                    AFrame.destroy()
                    continue
                elif choice == '3':
                    AFrame.destroy()
                else:
                    messagebox.showerror(message="invalid option")
            elif choice == '3':
                continue
        elif cmd == '2':
            pending, pending_order_Frame = mgr.list_pending_orders(ManagerWindow)
            choice = doubleOption(ManagerWindow,"[Manager] Orders: \nOptions","Update order","Quit")
            if choice == '1':
                ID, State= Entry_form(ManagerWindow,"Update order",('OrderID: ','Status (Completed/In progress/Cancelled): '))
                try:
                    int(ID)
                    if State == 'Completed' or State == 'In progress' or State == 'Cancelled':
                        mgr.update_order_status(ID, State)
                        pending_order_Frame.destroy()
                        ManagerWindow = Toplevel(MainWindow)
                        ManagerWindow.attributes('-fullscreen', True)
                    else:
                        messagebox.showerror(message="Invalid Status")
                        pending_order_Frame.destroy()
                        ManagerWindow = Toplevel(MainWindow)
                        ManagerWindow.attributes('-fullscreen', True)
                except Exception as e:
                    print(e)
                    messagebox.showerror(message="Invalid Update")
                    pending_order_Frame.destroy()
                    ManagerWindow = Toplevel(MainWindow)
                    ManagerWindow.attributes('-fullscreen', True)
            elif choice == '2':
                pending_order_Frame.destroy()
                continue

        elif cmd == '3':
            table = mgr.print_all_ingredients(ManagerWindow)
            choice = doubleOption(ManagerWindow,"\n[Manager] Inventory: \nOptions","Next Week Inventory Requirements Prediction","Quit")
            if choice != False:
                table.destroy()
            if choice == '1':
                OutputTable = mgr.prediction_output(ManagerWindow)
                sub_choice = doubleOption(ManagerWindow,"[Manager] Prediction Complete: \nOptions","Replenishment","Quit")
                if sub_choice != False:
                    OutputTable.destroy()
                if sub_choice == '1':
                    orders, LPOFrame = mgr.list_purchase_orders(ManagerWindow)
                    option = tripleOption(ManagerWindow,"[Manager] Inventory (Replenishment): \nOptions","New Replenishment","Update Replenishment","Quit")
                    if option == '1':
                        LPOFrame.destroy()
                        inv = mgr.get_item()
                        inv = inv["inventory"]
                        IngredientList = []
                        for it in inv['ingredients']:
                            IngredientList.append(it['ingredient_id'])
                            IngredientList.append(it['name'])
                            IngredientList.append(it['unit'])
                            IngredientList.append(it['price_per_unit'])
                            IngredientList.append(it['unit'])

                        NewReplinishementFrame = TableCreator(ManagerWindow, "Ingredient list：",
                                     ('ingredient_id', 'name', 'unit', 'Price(RM)','/ unit'),
                                     IngredientList)
                        entry = Entry_form(ManagerWindow,'Ingredient list',('Ingredient ID: ','Amount (in unit): '))
                        if entry and len(entry) == 2 and entry[0].strip() and entry[1].strip():
                            iid, qty = entry[0].strip(), entry[1].strip()
                            mgr.add_purchase_order(iid, qty)
                            NewReplinishementFrame.destroy()
                            ManagerWindow = Toplevel(MainWindow)
                            ManagerWindow.attributes('-fullscreen', True)
                        else:
                            messagebox.showerror("Input Error", "Please fill in both fields correctly.")
                            NewReplinishementFrame.destroy()
                            ManagerWindow = Toplevel(MainWindow)
                            ManagerWindow.attributes('-fullscreen', True)
                    elif option == '2':
                        pid_data = Entry_form(ManagerWindow,"update",('Replenishment ID: ',))
                        state = '0'
                        if not pid_data or not pid_data[0].isdigit():
                            messagebox.showerror("Input Error", "Please enter a valid Replenishment ID.")
                        else:
                            pid = int(pid_data[0])
                            state = doubleOption(ManagerWindow, "[Manager] \nOptions", "Update status", "Delete")

                        if state == '1':
                            new = Entry_form(ManagerWindow,"Update status",('New status (Ordered, Received, Cancelled):',))
                            if new[0].title() in ['Ordered', 'Received', 'Cancelled']:
                                mgr.update_purchase_order_status(pid, new[0].title())
                                LPOFrame.destroy()
                                ManagerWindow = Toplevel(MainWindow)
                                ManagerWindow.attributes('-fullscreen', True)
                            else:
                                messagebox.showerror(message="Invalid Status")
                                LPOFrame.destroy()
                                ManagerWindow = Toplevel(MainWindow)
                                ManagerWindow.attributes('-fullscreen', True)
                        elif state == '2':
                            mgr.delete_purchase_order(pid)
                            LPOFrame.destroy()
                            ManagerWindow = Toplevel(MainWindow)
                            ManagerWindow.attributes('-fullscreen', True)
                        elif state == '3':
                            LPOFrame.destroy()
                            pass
                    elif option == '3':
                        LPOFrame.destroy()
                        pass

                elif sub_choice == '2':
                    pass
            elif choice == '2':
                pass
        elif cmd =='4':
            recent_orders, FinanceFrame = mgr.financial_summary_past_week(ManagerWindow)
            choice = ButtonCreator(ManagerWindow,"[Manager] \nOptions",("Quit",))
            if choice == 0:
                FinanceFrame.destroy()
                continue

        elif cmd =='5':
            feedbackFrame = mgr.list_feedback(ManagerWindow)
            choice = ButtonCreator(ManagerWindow, "[Manager] \nOptions", ("Quit",))
            if choice == 0:
                feedbackFrame.destroy()
                continue
        elif cmd == '6':
            ManagerWindow.destroy()
            break
        else: messagebox.showerror(message="Invalid Option")