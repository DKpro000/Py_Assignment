from tkinter import *
from tkinter import ttk, filedialog, messagebox
from collections import Counter, defaultdict
#GUI
from GUI import ButtonCreator, TableCreator, Entry_form, get_login_choice, SignUpInfo, LogInInfo, Manager_choice, tripleOption, ApprovalPage, doubleOption, MainWindow
#DataBase
from DataBase import datasets, load, write, str_to_json
#AES
from AES import KeyExchange, pseudo_encrypt, pseudo_decrypt
#Manager
from Manager import Manager, manager_interface
#Cashier
from Cashier import Cashier, cashier_interface
#Customer
from Customer import Customer, customer_interface
#Chef
from Chef import Chef, chef_interface


class system_manager:
    def __init__(self):
        self.data_banker = datasets()
        self.users_available = self.data_banker.get_users()

        self._plain_data = {
            Manager: {
                "user": self.data_banker.get_users(),
                "order": self.data_banker.get_orders(),
                "inventory": self.data_banker.get_iventory(),
                "ingredient_order": self.data_banker.get_ingredient_order(),
                "finance": self.data_banker.get_finance(),
                "feedbacks": self.data_banker.get_feedback(),
                "threshold": self.data_banker.get_threshold()
            },
            Cashier: {
                "menu": self.data_banker.get_menu(),
                "order": self.data_banker.get_orders(),
                "inventory": self.data_banker.get_iventory(),
            },
            Chef: {
                "menu": self.data_banker.get_menu(),
                "ingr": self.data_banker.get_iventory(),
                "order": self.data_banker.get_orders(),
                "eqp": self.data_banker.get_eqp()
                
            },
            Customer: {
                "menu": self.data_banker.get_menu(),
                "feedback": self.data_banker.get_feedback(),
                "order": self.data_banker.get_orders(),
                "inventory": self.data_banker.get_iventory(),
                "user": self.data_banker.get_users(),
            }
        }

        self.kex = KeyExchange()
        self.shared_key = None

    def exchange_public_key(self):
        return self.kex.public

    def receive_public_key(self, other_pub):
        self.shared_key = self.kex.generate_shared_key(other_pub)

    def send_message(self, message):
        return pseudo_encrypt(message, self.shared_key)

    def get_data(self, requester) -> str:
        cls = type(requester)
        if cls not in self._plain_data:
            raise ValueError(f"Unknown requester: {cls}")
        plain = str(self._plain_data[cls])
        return self.send_message(plain)

    def login(self, accID, password):
        for user in self.users_available['users']:
            if user["accID"] == accID and user["pass"] == password:
                return True, user['role']
        return False, None

    def write_mn_users(self, users_dict):
        latest = self.data_banker.get_users()
        users_list = latest.get('users', [])
        users_list = [u for u in users_list if u.get('accID') != users_dict.get('accID')]
        users_list.append(users_dict)
        latest['users'] = users_list
        write(latest, 'datasets/users.txt')
        self.users_available = latest
        self._plain_data[Manager]['user'] = latest
        
    #Manager
    def manager_only(method):
        def wrapper(self, requester, *args, **kwargs):
            if requester.__class__.__name__ == 'Manager':
                return method(self, requester, *args, **kwargs)
            print(f"Permission denied: {method.__name__} requires Manager role.")
        return wrapper

    @manager_only
    def write_mng_orders(self, requester, orders_dict):
        write(orders_dict, 'datasets/orders.txt')
        self._plain_data[Manager]['order'] = orders_dict

    @manager_only
    def write_ingredients(self, requester, inv_dict):
        write(inv_dict, 'datasets/ingredients.txt')
        self._plain_data[Manager]['inventory'] = inv_dict

    @manager_only
    def write_ingredient_order(self, requester, ingO_dict):
        write(ingO_dict, 'datasets/ingredient_order.txt')
        self._plain_data[Manager]['ingredient_order'] = ingO_dict

    @manager_only
    def write_users(self, requester, users_dict):
        write(users_dict, 'datasets/users.txt')
        self._plain_data[Manager]['user'] = users_dict
        self.users_available = users_dict

    @manager_only
    def delete_users(self, requester, users_dict):
        write(users_dict, 'datasets/users.txt')
        self._plain_data[Manager]['user'] = users_dict
        self.users_available = users_dict

    #Cashier
    def cashier_only(method):
        def wrapper(self, requester, *args, **kwargs):
            if requester.__class__.__name__ == 'Cashier':
                return method(self, requester, *args, **kwargs)
            print(f"Permission denied: {method.__name__} requires Cashier role.")
        return wrapper

    @cashier_only
    def write_chs_orders(self, requester, order_dict, dishes=None):
        write(order_dict, 'datasets/orders.txt')
        self._plain_data[Manager]['order'] = order_dict

    @cashier_only
    def write_menu(self, requester, menu_dict):
        write(menu_dict, 'datasets/menu.txt')
        self._plain_data[Cashier]['menu'] = menu_dict

    #Customer
    def customer_only(method):
        def wrapper(self, requester, *args, **kwargs):
            if requester.__class__.__name__ == 'Customer':
                return method(self, requester, *args, **kwargs)
            print(f"Permission denied: {method.__name__} requires Customer role.")
        return wrapper

    @customer_only
    def delete_users(self, requester, users_dict):
        write(users_dict, 'datasets/users.txt')
        self._plain_data[Customer]['user'] = users_dict
        self.users_available = users_dict

    @customer_only
    def write_ctm_orders(self, requester, order_dict, dishes=None):
        write(order_dict, 'datasets/orders.txt')
        self._plain_data[Manager]['order'] = order_dict

    @customer_only
    def write_cs_users(self, requester, users_dict):
        write(users_dict, 'datasets/users.txt')
        self._plain_data[Customer]['user'] = users_dict
        self.users_available = users_dict

    @customer_only
    def write_feedback(self, requester, users_dict):
        write(users_dict, 'datasets/feedbacks.txt')
        self._plain_data[Customer]['feedback'] = users_dict
        self.users_available = users_dict

    #Chef
    def chef_only(method):
        def wrapper(self, requester, *args, **kwargs):
            if requester.__class__.__name__ == 'Chef':
                return method(self, requester, *args, **kwargs)
            print(f"Permission denied: {method.__name__} requires Chef role.")
        return wrapper

    @chef_only
    def chf_write_menu(self, requester, data):
        write(data, 'datasets/menu.txt')
        self._plain_data[Chef]['menu'] = data
    
    @chef_only
    def chf_write_ing(self, requester, data):
        write(data, 'datasets/ingredients.txt')
        self._plain_data[Chef]['ingr'] = data

    @chef_only
    def chf_write_eqp(self, requester, data):
        write(data, 'datasets/equipments.txt')
        self._plain_data[Chef]['eqp'] = data

    @chef_only
    def chf_write_orders(self, requester, orders_dict):
        write(orders_dict, 'datasets/orders.txt')
        self._plain_data[Chef]['order'] = orders_dict
    
    @chef_only
    def chf_write_ingredients(self, requester, orders_dict):
        write(orders_dict, 'datasets/orders.txt')
        self._plain_data[Chef]['order'] = orders_dict

"""# Main Panel"""
class panel:
    def __init__(self):
        self.pending_users = []

    def sign_up(self, acc_name, acc_role, acc_password):
        user = {"role": acc_role, "accID": acc_name, "pass": acc_password}
        self.pending_users.append(user)
        print(f"User {acc_name}({acc_role}) has submitted a registration application and is awaiting approval by the administrator.")

    def show_pending(self,ManagerWindow):
        pendingFrame = Frame(ManagerWindow)
        pendingFrame.pack(padx=10, pady=10, fill="both", expand=True)

        if not self.pending_users:
            Label(pendingFrame, text="There are no pending users.").pack()
            return pendingFrame,[]

        Label(pendingFrame, text="List of users pending approval：").pack()
        teptPendingList = []
        for u in self.pending_users:
            teptPendingList.append(u['accID'])
            teptPendingList.append(u['role'])
        TableCreator(pendingFrame,"Pending Users",("ID","Role"),teptPendingList)
        return pendingFrame, self.pending_users

system = system_manager()
pnl = panel()
while True:
    choice = get_login_choice(MainWindow)
    if choice == '1':
        result = SignUpInfo(MainWindow)
        if result is None:
            continue
        acc, rol, pas = result
        if rol.lower() == 'customer':
            system.write_mn_users({"role": 'customer', "accID": acc, "pass": pas})
            messagebox.showinfo(message="Customer account created")
        elif rol.lower() == 'chef' or rol.lower() == 'cashier':
            pnl.sign_up(acc, rol.lower(), pas)
        else:
            messagebox.showerror(message="Invalid Role")

    elif choice == '2':
        result = LogInInfo(MainWindow)
        if result is None:
            continue
        acc, pas = result
        ok, role = system.login(acc, pas)
        if not ok:
            messagebox.showerror(message="Login failed: wrong account or password.")
            continue
        messagebox.showinfo(message=f"Login successful, role: {role.capitalize()}")
        if role == 'manager':
            sys = system_manager()
            mgr = Manager(sys, pnl)

            sys_pub = sys.exchange_public_key()
            mgr_pub = mgr.exchange_public_key()

            mgr.receive_public_key(sys_pub)
            sys.receive_public_key(mgr_pub)

            manager_interface(mgr, MainWindow)
        elif role.lower() == 'cashier':
            sys = system_manager()

            chs = Cashier(sys, pnl)

            sys_pub = sys.exchange_public_key()
            chs_pub = chs.exchange_public_key()

            sys.receive_public_key(chs_pub)
            chs.receive_public_key(sys_pub)

            cashier_interface(chs,MainWindow)
        elif role.lower() == 'chef':
            sys = system_manager()

            chf = Chef(sys, pnl)

            sys_pub = sys.exchange_public_key()
            chf_pub = chf.exchange_public_key()

            sys.receive_public_key(chf_pub)
            chf.receive_public_key(sys_pub)

            chef_interface(chf,MainWindow)
        elif role.lower() == 'customer':
            sys_cus = system_manager()
            customer = Customer(sys_cus, pnl)

            system_pub_key = sys_cus.exchange_public_key()
            customer_pub_key = customer.exchange_public_key()

            sys_cus.receive_public_key(customer_pub_key)
            customer.receive_public_key(system_pub_key)

            customer_interface(customer, MainWindow,acc, pas)
        else:
            print("Unknown role, unable to enter the interface.")

    elif choice == '3':
        print("Exiting the system.")
        break

    else:
        print("Invalid option, please try again. ")



