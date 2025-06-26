import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime, timedelta
import os
from collections import Counter, defaultdict

MainWindow = Tk()
MainWindow.attributes('-fullscreen', True)
MainWindow.configure(bg="#C9A0DC")

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

    Tablescrollable_frame = Frame(Tablecanvas, bg="black")
    Tablecanvas.create_window((0, 0), window=Tablescrollable_frame, anchor="nw", tags="frame")
    Tablescrollable_frame.bind("<Configure>", lambda e: Tablecanvas.configure(scrollregion=Tablecanvas.bbox("all")))

    def resize_scrollable_frame(event):
        canvas_width = event.width
        Tablecanvas.itemconfig("frame", width=canvas_width)

    Tablecanvas.bind("<Configure>", resize_scrollable_frame)

    columnColor = ["#F3E8FB", "#E4D0F4"]

    Label(Tablescrollable_frame, text=title).grid(row=0, column=0, columnspan=len(columnNames),sticky="nsew")
    for num, name in enumerate(columnNames):
        Label(Tablescrollable_frame, text=name, bg="#E0E6ED").grid(row=1, column=num,sticky="nsew", padx=1, pady=1)

    Tcolumn = len(columnNames)
    for num, item in enumerate(columnItems):
        r = num // Tcolumn + 2  # +2 to account for title and header rows
        c = num % Tcolumn
        row_color = columnColor[(r - 2) % len(columnColor)]  # (r - 2) so striping starts after headers
        Label(Tablescrollable_frame, text=item, bg=row_color).grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

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

    # Create a red frame aligned to the right side of the window
    LoginFrame = Frame(LoginWindow, bg="#2E2E2E")
    LoginFrame.place(relx=1, rely=1, relwidth=0.4, relheight=1, anchor="se")

    choice_var = StringVar(LoginWindow)  # This will store the user's choice

    def LoginInput(number):
        choice_var.set(number)
        LoginFrame.destroy()

    # Use an internal frame to center widgets inside LoginFrame
    inner_frame = Frame(LoginFrame, bg="#2E2E2E")
    inner_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Widgets
    Label(inner_frame, text="Main Menu", bg="#2E2E2E", fg="white", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=3, pady=(0, 20))

    Button(inner_frame, text="Sign Up", width=10, command=lambda: LoginInput("1")).grid(row=1, column=0, padx=5)
    Button(inner_frame, text="Login", width=10, command=lambda: LoginInput("2")).grid(row=1, column=1, padx=5)
    Button(inner_frame, text="Exit", width=10, command=lambda: LoginInput("3")).grid(row=1, column=2, padx=5)

    LoginWindow.wait_variable(choice_var)

    return choice_var.get()

def SignUpInfo(MainWindow):
    MainWindow.title("Sign Up")

    # Create a red background frame on the left side
    RedFrame = Frame(MainWindow, bg="#2E2E2E")
    RedFrame.place(relx=1, rely=1, relwidth=0.4, relheight=1, anchor="se")

    # Control variables
    Name_Choice = StringVar()
    Role_Choice = StringVar()
    Pas_Choice = StringVar()
    Action_Choice = StringVar()  # "signup" or "back"

    # Inner centered frame
    inner_frame = Frame(RedFrame, bg="#2E2E2E")
    inner_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Entry widgets
    name_entry = Entry(inner_frame, width=30)
    role_entry = Entry(inner_frame, width=30)
    pass_entry = Entry(inner_frame, show="*", width=30)

    def Info():
        Name_Choice.set(name_entry.get())
        Role_Choice.set(role_entry.get())
        Pas_Choice.set(pass_entry.get())
        Action_Choice.set("signup")
        RedFrame.destroy()

    def GoBack():
        Action_Choice.set("back")
        RedFrame.destroy()

    # Layout
    Label(inner_frame, text="Sign Up", bg="#2E2E2E", fg="white", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    Label(inner_frame, text="Account Name:", bg="#2E2E2E", fg="white").grid(row=1, column=0, sticky=E, padx=5, pady=5)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    Label(inner_frame, text="Role (Customer/Chef/Cashier):", bg="#2E2E2E", fg="white").grid(row=2, column=0, sticky=E, padx=5, pady=5)
    role_entry.grid(row=2, column=1, padx=5, pady=5)

    Label(inner_frame, text="Account Password:", bg="#2E2E2E", fg="white").grid(row=3, column=0, sticky=E, padx=5, pady=5)
    pass_entry.grid(row=3, column=1, padx=5, pady=5)

    Button(inner_frame, text="Sign Up", width=20, command=Info).grid(row=4, column=0, columnspan=2, pady=(10, 5))
    Button(inner_frame, text="Back", width=20, command=GoBack).grid(row=5, column=0, columnspan=2)

    MainWindow.wait_variable(Action_Choice)

    if Action_Choice.get() == "signup":
        return Name_Choice.get(), Role_Choice.get(), Pas_Choice.get()
    else:
        return None
def LogInInfo(LogInWindow):
    LogInWindow.title("Log In")

    # Red sidebar frame on the left
    RedFrame = Frame(LogInWindow, bg="#2E2E2E")
    RedFrame.place(relx=1, rely=1, relwidth=0.4, relheight=1, anchor="se")

    # Tkinter control variables
    Name_Choice = StringVar()
    Pas_Choice = StringVar()
    Action_Choice = StringVar()  # "login" or "back"

    # Inner frame to center widgets in red frame
    inner_frame = Frame(RedFrame, bg="#2E2E2E")
    inner_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Entry fields
    LogName = Entry(inner_frame, width=30)
    LogPass = Entry(inner_frame, show="*", width=30)

    def Info():
        Name_Choice.set(LogName.get())
        Pas_Choice.set(LogPass.get())
        Action_Choice.set("login")
        RedFrame.destroy()

    def GoBack():
        Action_Choice.set("back")
        RedFrame.destroy()

    # Layout
    Label(inner_frame, text="Log In", bg="#2E2E2E", fg="white", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    Label(inner_frame, text="Account Name:", bg="#2E2E2E", fg="white").grid(row=1, column=0, sticky=E, padx=5, pady=5)
    LogName.grid(row=1, column=1, padx=5, pady=5)

    Label(inner_frame, text="Account Password:", bg="#2E2E2E", fg="white").grid(row=2, column=0, sticky=E, padx=5, pady=5)
    LogPass.grid(row=2, column=1, padx=5, pady=5)

    Button(inner_frame, text="Log In", width=20, command=Info).grid(row=3, column=0, columnspan=2, pady=(10, 5))
    Button(inner_frame, text="Back", width=20, command=GoBack).grid(row=4, column=0, columnspan=2)

    LogInWindow.wait_variable(Action_Choice)

    if Action_Choice.get() == "login":
        return Name_Choice.get(), Pas_Choice.get()
    else:
        return None

def Manager_choice(ManagerWindow):
    ManagerWindow.title("Manager")
    ManagerWindow.configure(bg="grey")

    ManagerFrame = Frame(ManagerWindow, bg="white")
    ManagerFrame.place(relx=1, rely=1, relwidth=0.8, relheight=1, anchor="se")

    choice_var = StringVar(ManagerWindow)

    def LoginInput(number):
        choice_var.set(number)
        ManagerFrame.destroy()

    # Configure grid to expand
    for i in range(3):  # rows
        ManagerFrame.rowconfigure(i, weight=1)
    for j in range(3):  # columns
        ManagerFrame.columnconfigure(j, weight=1)

    Label(ManagerFrame, text="Main Menu", font=("Arial", 24, "bold"), bg="white").grid(row=0, column=0, columnspan=3, pady=20)

    btn_font = ("Arial", 16)
    btn_kwargs = {"width": 15, "height": 2, "font": btn_font}

    Button(ManagerFrame, text="Users", command=lambda: LoginInput("1"), **btn_kwargs).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    Button(ManagerFrame, text="Orders", command=lambda: LoginInput("2"), **btn_kwargs).grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    Button(ManagerFrame, text="Inventory", command=lambda: LoginInput("3"), **btn_kwargs).grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    Button(ManagerFrame, text="Financial", command=lambda: LoginInput("4"), **btn_kwargs).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    Button(ManagerFrame, text="Feedback", command=lambda: LoginInput("5"), **btn_kwargs).grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
    Button(ManagerFrame, text="Sign Out", command=lambda: LoginInput("6"), **btn_kwargs).grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

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