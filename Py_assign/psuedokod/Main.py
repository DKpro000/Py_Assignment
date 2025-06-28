CLASS system_manager
    PROCEDURE __init__()
        data_banker ← NEW datasets()
        users_available ← data_banker.get_users()

        // Snapshot of every table to be served (plaintext)
        _plain_data ← {
            Manager  : { user : data_banker.get_users(),
                         order : data_banker.get_orders(),
                         inventory : data_banker.get_iventory(),
                         ingredient_order : data_banker.get_ingredient_order(),
                         finance : data_banker.get_finance(),
                         feedbacks : data_banker.get_feedback(),
                         threshold : data_banker.get_threshold() },
            Cashier  : { menu : data_banker.get_menu(),
                         order : data_banker.get_orders(),
                         inventory : data_banker.get_iventory() },
            Chef     : { menu : data_banker.get_menu(),
                         ingr : data_banker.get_iventory(),
                         order : data_banker.get_orders(),
                         eqp : data_banker.get_eqp() },
            Customer : { menu : data_banker.get_menu(),
                         feedback : data_banker.get_feedback(),
                         order : data_banker.get_orders(),
                         inventory : data_banker.get_iventory(),
                         user : data_banker.get_users() }
        }

        kex ← NEW KeyExchange()
        shared_key ← NULL
    END PROCEDURE

    FUNCTION exchange_public_key() → RETURN kex.public
    PROCEDURE receive_public_key(other_pub) → shared_key ← kex.generate_shared_key(other_pub)
    FUNCTION send_message(msg) → RETURN pseudo_encrypt(msg, shared_key)

    FUNCTION get_data(requester) → STRING
        cls ← CLASS_OF(requester)
        IF cls ∉ _plain_data THEN RAISE "Unknown requester"
        RETURN send_message( STRING(_plain_data[cls]) )
    END FUNCTION

    FUNCTION login(accID, pwd) → (BOOL ok, STRING role)
        FOR u IN users_available.users DO
            IF u.accID = accID AND u.pass = pwd THEN RETURN (TRUE, u.role)
        RETURN (FALSE, NULL)
    END FUNCTION

    DECORATOR manager_only(func):
        RETURN λ(self, requester, *args):
                 IF CLASS_OF(requester)="Manager" THEN
                     RETURN func(self, requester, *args)
                 ELSE PRINT "Permission denied"
END CLASS

CLASS panel
    PROCEDURE __init__() → pending_users ← []
    PROCEDURE sign_up(id, role, pwd)
        APPEND {role,accID:id,pass:pwd} TO pending_users
        PRINT "User " ◦ id ◦ " awaits approval"
    END PROCEDURE

    FUNCTION show_pending(win) → (FRAME gui, ARRAY users)
        frame ← NEW Frame(win)
        IF pending_users EMPTY THEN LABEL(frame,"No pending users")
        ELSE  TableCreator(frame,"Pending Users", ("ID","Role"),
                           FLATTEN([u.accID,u.role] FOR u IN pending_users))
        RETURN (frame, pending_users)
    END FUNCTION
END CLASS

system ← NEW system_manager()
pnl ← NEW panel()

LOOP
    choice ← get_login_choice(MainWindow)

    IF choice = "1":
        (acc, role, pwd) ← SignUpInfo(MainWindow)
        IF role = "customer":
            system.write_mn_users({"role":"customer","accID":acc,"pass":pwd})
            INFOBOX("Customer account created")
        ELIF role ∈ {"chef","cashier"}:
            pnl.sign_up(acc, role, pwd)
        ELSE ERRORBOX("Invalid role")

    ELIF choice = "2":
        (acc, pwd) ← LogInInfo(MainWindow)
        (ok, role) ← system.login(acc, pwd)
        IF NOT ok THEN ERRORBOX("Login failed"); CONTINUE
        INFOBOX("Login successful, role: " ◦ role)

        sys ← NEW system_manager()

        SWITCH role
        CASE "manager":
            mgr ← NEW Manager(sys, pnl)
            DUAL_KEY_EXCHANGE(sys, mgr)
            manager_interface(mgr, MainWindow)

        CASE "cashier":
            chs ← NEW Cashier(sys, pnl)
            DUAL_KEY_EXCHANGE(sys, chs)
            cashier_interface(chs, MainWindow)

        CASE "chef":
            chf ← NEW Chef(sys, pnl)
            DUAL_KEY_EXCHANGE(sys, chf)
            chef_interface(chf, MainWindow)

        CASE "customer":
            cus ← NEW Customer(sys, pnl)
            DUAL_KEY_EXCHANGE(sys, cus)
            customer_interface(cus, MainWindow, acc, pwd)

        DEFAULT:
            PRINT "Unknown role"

    ELIF choice = "3":
        PRINT "Exiting system"
        BREAK

    ELSE
        PRINT "Invalid option"
END LOOP

PROCEDURE DUAL_KEY_EXCHANGE(core, client)
    core_pub   ← core.exchange_public_key()
    client_pub ← client.exchange_public_key()
    core.receive_public_key(client_pub)
    client.receive_public_key(core_pub)
END PROCEDURE
