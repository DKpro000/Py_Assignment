import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime, timedelta
import os
from collections import Counter, defaultdict

MainWindow = Tk()

def ButtonCreator(ManagerWindow, title, options):
    ManagerWindow.title(title)
    ManagerFrame = Frame(ManagerWindow)
    ManagerFrame.pack(padx=10, pady=10)

    choice_var = StringVar(ManagerWindow)

    def Info(i):
        choice_var.set(str(i))
        ManagerFrame.destroy()

    # Layout buttons
    for i, name in enumerate(options):
        Button(ManagerFrame, text=name, command=lambda: Info(i)).grid(row=i, column=0, padx=5, pady=5)

    ManagerWindow.wait_variable(choice_var)

    return int(choice_var.get())


def TableCreator(ManagerWindow,title,columnNames,columnItems):
    TFrame = Frame(ManagerWindow)
    TFrame.pack(padx=10, pady=10, fill="both", expand=True)

    Tablecanvas = Canvas(TFrame)
    Tablecanvas.pack(side=LEFT, fill="both", expand=True)

    scrollbar = Scrollbar(TFrame, orient="vertical", command=Tablecanvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    Tablecanvas.configure(yscrollcommand=scrollbar.set)

    Tablescrollable_frame = Frame(Tablecanvas, bg="#387647")
    Tablecanvas.create_window((0, 0), window=Tablescrollable_frame, anchor="nw", tags="frame")
    Tablescrollable_frame.bind("<Configure>", lambda e: Tablecanvas.configure(scrollregion=Tablecanvas.bbox("all")))

    def resize_scrollable_frame(event):
        canvas_width = event.width
        Tablecanvas.itemconfig("frame", width=canvas_width)

    Tablecanvas.bind("<Configure>", resize_scrollable_frame)

    columnColor = ["red", "orange"]

    Label(Tablescrollable_frame, text=title).grid(row=0, column=0, columnspan=len(columnNames),sticky="nsew")
    for num, name in enumerate(columnNames):
        color = columnColor[num % len(columnColor)]
        Label(Tablescrollable_frame, text=name, bg=color).grid(row=1, column=num,sticky="nsew", padx=1, pady=1)

    Tcolumn = len(columnNames)
    for num, item in enumerate(columnItems):
        r = num // Tcolumn + 2
        c = num % Tcolumn
        color = columnColor[c % len(columnColor)]
        Label(Tablescrollable_frame, text=item, bg=color).grid(row=r, column=c,sticky="nsew")

    for i in range(Tcolumn):
        Tablescrollable_frame.grid_columnconfigure(i, weight=1)

    return TFrame

def Entry_form(MainWindow,title,list):
    MainWindow.title(title)
    EFrame = Frame(MainWindow)
    EFrame.pack(padx=10, pady=10)

    #something to hold the entry boxes
    EntryInputs = []

    #something to hold the data that we got from entry
    Data = []

    def Info():
        for values in EntryInputs:
            Data.append(values.get().strip())
        EFrame.destroy()

    # Layout
    for i, count in enumerate(list):
        Label(EFrame,text=count).grid(row=i, column=0)
        userEntry = Entry(EFrame)
        userEntry.grid(row=i, column=1)
        EntryInputs.append(userEntry)



    Button(EFrame, text=title, command=Info).grid(row=4, columnspan=2)

    MainWindow.wait_window(EFrame)

    # Return all three as a tuple
    return Data

def get_login_choice(LoginWindow):
    LoginWindow.title("Main Menu")
    LoginFrame = Frame(LoginWindow)
    LoginFrame.pack(padx=10, pady=10)

    choice_var = StringVar(LoginWindow)  # Pass the root window as master

    def LoginInput(number):
        choice_var.set(number)
        LoginFrame.destroy()


    Label(LoginFrame, text="Main Menu").grid(row=0, column=0, columnspan=3)

    Button(LoginFrame, text="Sign Up", command=lambda: LoginInput("1")).grid(row=1, column=0, padx=5)
    Button(LoginFrame, text="Login", command=lambda: LoginInput("2")).grid(row=1, column=1, padx=5)
    Button(LoginFrame, text="Exit", command=lambda: LoginInput("3")).grid(row=1, column=2, padx=5)

    LoginWindow.wait_variable(choice_var)

    return choice_var.get()

def SignUpInfo(MainWindow):
    MainWindow.title("Sign Up")
    MainFrame = Frame(MainWindow)
    MainFrame.pack(padx=10, pady=10)

    # Tkinter control variables
    Name_Choice = StringVar()
    Role_Choice = StringVar()
    Pas_Choice = StringVar()

    # Entries (must be saved so we can get their input)
    name_entry = Entry(MainFrame)
    role_entry = Entry(MainFrame)
    pass_entry = Entry(MainFrame, show="*")

    def Info():
        Name_Choice.set(name_entry.get())
        Role_Choice.set(role_entry.get())
        Pas_Choice.set(pass_entry.get())
        MainFrame.destroy()

    # Layout
    Label(MainFrame, text="Sign Up").grid(row=0, columnspan=2)

    Label(MainFrame, text="Account Name:").grid(row=1, column=0)
    name_entry.grid(row=1, column=1)

    Label(MainFrame, text="Role (Customer/Chef/Cashier):").grid(row=2, column=0)
    role_entry.grid(row=2, column=1)

    Label(MainFrame, text="Account Password:").grid(row=3, column=0)
    pass_entry.grid(row=3, column=1)

    Button(MainFrame, text="Sign Up", command=Info).grid(row=4, columnspan=2)

    MainWindow.wait_variable(Name_Choice)

    # Return all three as a tuple
    return Name_Choice.get(), Role_Choice.get(), Pas_Choice.get()

def LogInInfo(LogInWindow):
    LogInWindow.title("Sign Up")

    LogInFrame = Frame(LogInWindow)
    LogInFrame.pack(padx=10, pady=10)

    # Tkinter control variables
    Name_Choice = StringVar()
    Pas_Choice = StringVar()

    # Entries (must be saved so we can get their input)
    LogName = Entry(LogInFrame)
    LogPass = Entry(LogInFrame, show="*")

    def Info():
        Name_Choice.set(LogName.get())
        Pas_Choice.set(LogPass.get())
        LogInFrame.destroy()

    # Layout
    Label(LogInFrame, text="Log In").grid(row=0, columnspan=2)

    Label(LogInFrame, text="Account Name:").grid(row=1, column=0)
    LogName.grid(row=1, column=1)

    Label(LogInFrame, text="Account Password:").grid(row=2, column=0)
    LogPass.grid(row=2, column=1)

    Button(LogInFrame, text="Log In", command=Info).grid(row=3, columnspan=2)

    MainWindow.wait_variable(Name_Choice)

    # Return all three as a tuple
    return Name_Choice.get(), Pas_Choice.get()

def Manager_choice(ManagerWindow):
    ManagerWindow.title("Manager")
    ManagerFrame = Frame(ManagerWindow)
    ManagerFrame.pack(padx=10, pady=10)

    choice_var = StringVar(ManagerWindow)

    def LoginInput(number):
        choice_var.set(number)
        ManagerFrame.destroy()



    Label(ManagerFrame, text="Main Menu").grid(row=0, column=0, columnspan=3)

    Button(ManagerFrame, text="Users", command=lambda: LoginInput("1")).grid(row=1, column=0, padx=5)
    Button(ManagerFrame, text="Orders", command=lambda: LoginInput("2")).grid(row=1, column=1, padx=5)
    Button(ManagerFrame, text="Inventory", command=lambda: LoginInput("3")).grid(row=1, column=2, padx=5)
    Button(ManagerFrame, text="Financial", command=lambda: LoginInput("4")).grid(row=2, column=0, padx=5)
    Button(ManagerFrame, text="Feedback", command=lambda: LoginInput("5")).grid(row=2, column=1, padx=5)
    Button(ManagerFrame, text="Sign Out", command=lambda: LoginInput("6")).grid(row=2, column=2, padx=5)

    ManagerWindow.wait_variable(choice_var)

    return choice_var.get()

def tripleOption(ManagerWindow,title,first,second,third):
    ManagerWindow.title(title)
    ManagerFrame = Frame(ManagerWindow)
    ManagerFrame.pack(padx=10, pady=10)

    choice_var = StringVar(ManagerWindow)

    def LoginInput(number):
        choice_var.set(number)
        ManagerFrame.destroy()

    Label(ManagerFrame, text=title).grid(row=0, column=0, columnspan=3)

    Button(ManagerFrame, text=first, command=lambda: LoginInput("1")).grid(row=1, column=0, padx=5)
    Button(ManagerFrame, text=second, command=lambda: LoginInput("2")).grid(row=1, column=1, padx=5)
    Button(ManagerFrame, text=third, command=lambda: LoginInput("3")).grid(row=1, column=2, padx=5)

    ManagerWindow.wait_variable(choice_var)

    return choice_var.get()

def ApprovalPage(parent, title):
    dialog = Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)    # Stay on top of parent
    dialog.grab_set()           # Modal dialog: user must close this first

    acc_var = StringVar()

    Label(dialog, text=title).pack(pady=5)
    entry = Entry(dialog)
    entry.pack(padx=10, pady=5)
    entry.focus_set()

    def submit():
        acc_var.set(entry.get())
        dialog.destroy()

    Button(dialog, text="Submit", command=submit).pack(pady=5)

    # BLOCK execution here until window is closed
    dialog.wait_window(dialog)

    return acc_var.get()

def doubleOption(ManagerWindow,title,first,second):
    ManagerWindow.title(title)
    ManagerFrame = Frame(ManagerWindow)
    ManagerFrame.pack(padx=10, pady=10)

    choice_var = StringVar(ManagerWindow)

    def LoginInput(number):
        choice_var.set(number)
        ManagerFrame.destroy()

    Label(ManagerFrame, text=title).grid(row=0, column=0, columnspan=3)

    Button(ManagerFrame, text=first, command=lambda: LoginInput("1")).grid(row=1, column=0, padx=5)
    Button(ManagerFrame, text=second, command=lambda: LoginInput("2")).grid(row=1, column=1, padx=5)

    ManagerWindow.wait_variable(choice_var)

    return choice_var.get()