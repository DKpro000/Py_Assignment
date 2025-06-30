CLASS Manager
    PROCEDURE __init__( system, panel )
        self.system ← system
        self.panel ← panel
        self.kex ← NEW KeyExchange()
        self.shared_key ← NULL
    END PROCEDURE

    FUNCTION retrieve_data()
        encrypted ← self.system.get_data(self)
        RETURN encrypted
    END FUNCTION

    FUNCTION exchange_public_key() → INTEGER
        RETURN self.kex.public
    END FUNCTION

    PROCEDURE receive_public_key( other_pub : INTEGER )
        self.shared_key ← self.kex.generate_shared_key(other_pub)
    END PROCEDURE

    FUNCTION get_item()  → DICTIONARY
        ciphertext ← self.retrieve_data()
        plaintext ← pseudo_decrypt(ciphertext, self.shared_key)
        RETURN str_to_json(plaintext)
    END FUNCTION

    PROCEDURE approve( accID )
        data ← self.get_item()
        users_tbl ← data["user"]["users"]
        FOR u IN self.panel.pending_users DO
            IF u.accID = accID THEN
                APPEND u TO users_tbl
                self.system.write_users(self, data["user"])
                REMOVE u FROM self.panel.pending_users
                INFOBOX("Approved user ", accID)
                RETURN
        END FOR
        ERRORBOX("No pending user ", accID)
    END PROCEDURE

    PROCEDURE delete( accID )
        data      ← self.get_item()
        users_tbl ← data["user"]["users"]
        new_tbl   ← [u ∈ users_tbl  WHERE u.accID ≠ accID]
        IF LENGTH(new_tbl) < LENGTH(users_tbl) THEN
            data["user"]["users"] ← new_tbl
            self.system.write_users(self, data["user"])
            INFOBOX("Removed user ", accID)
        ELSE
            ERRORBOX("No user ", accID)
    END PROCEDURE

    PROCEDURE reject( accID )
        IF REMOVE_FIRST( self.panel.pending_users, WHERE accID = accID ) THEN
            INFOBOX("Denied registration for ", accID)
        ELSE
            ERRORBOX("No pending user ", accID)
    END PROCEDURE

    FUNCTION list_approved( window ) → (ARRAY users, FRAME gui)
        frame ← NEW Frame(window)
        data  ← self.get_item()["user"]["users"]
        rows  ← FLATTEN( [u.accID, u.role]  FOR u IN data )
        TableCreator(frame, "List of approved users:",
                            ("Account ID","Role"), rows)
        RETURN (data, frame)
    END FUNCTION

    PROCEDURE modify_user( accID, new_role = NULL, new_password = NULL )
        data ← self.get_item()
        FOR u IN data["user"]["users"] DO
            IF u.accID = accID THEN
                IF new_role      THEN u.role ← new_role
                IF new_password  THEN u.pass ← new_password
                self.system.write_users(self, data["user"])
                INFOBOX("Updated user ", accID)
                RETURN
        END FOR
        ERRORBOX("User ", accID, " not found")
    END PROCEDURE

    FUNCTION list_pending_orders(window) → (ARRAY orders, FRAME gui)
        frame   ← NEW Frame(window)
        orders  ← FILTER( self.get_item()["order"]["orders"], λ o : LOWER(o.status) ≠ "completed")
        IF orders IS EMPTY THEN
            LABEL(frame,"There are currently no outstanding orders.")
        ELSE
            rows ← FLATTEN([o.order_id, o.customer_id, o.order_time, o.status, o.total]  FOR o IN orders)
            TableCreator(frame,"List of uncompleted orders:", ("OrderID","CustomerID","Time","Status","Amount"),rows)
        RETURN (orders, frame)
    END FUNCTION

    PROCEDURE update_order_status(order_id, new_status)
        data ← self.get_item()
        orders_tbl ← data["order"]["orders"]
        inventory ← data["inventory"]
        recipes ← inventory["recipes"]
        ingreds ← inventory["ingredients"]

        FOR o IN orders_tbl DO
            IF o.order_id ≠ INTEGER(order_id) THEN CONTINUE
            old ← o.status

            IF old = "In progress" AND new_status = "Completed" THEN
                dishes ← [ (it.dish_id, it.quantity) FOR it IN data["order"]["order_items"] IF it.order_id = o.order_id ]
                FOR (dish_id, qty) IN dishes DO
                    r ← FIND_FIRST(recipes, λ x : x.dish_id = dish_id)
                    IF r IS NULL THEN CONTINUE
                    FOR ing IN r.ingredients DO
                        id ← ing.ingredient_id
                        need← ing.quantity * qty
                        obj ← FIND_FIRST(ingreds, λ x : x.ingredient_id = id)
                        IF obj THEN obj.stock ← MAX(obj.stock - need,0).ROUND(2)
                self.system.write_ingredients(self, inventory)

            IF new_status = "Cancelled" THEN
                REMOVE o FROM orders_tbl
                self.system.write_mng_orders(self, data["order"])
                INFOBOX("Cancelled order ", order_id)
                RETURN

            o.status ← new_status
            self.system.write_mng_orders(self, data["order"])
            INFOBOX("Updated order ", order_id, " → ", new_status)
            RETURN
        END FOR
        ERRORBOX("Order ", order_id, " not found")
    END PROCEDURE

    FUNCTION financial_summary_past_week(window) → (ARRAY orders, FRAME gui)
        frame   ← NEW Frame(window)
        orders  ← self.get_item()["order"]["orders"]
        today   ← DATE_NOW()
        weekago ← today - 7 days

        recent  ← [o ∈ orders WHERE weekago ≤ DATE(o.order_time) ≤ today AND o.status = "Completed"]
        IF recent IS EMPTY THEN
            LABEL(frame,"No orders in the past week.")
            RETURN ([], frame)

        LABEL(frame, "Order statistics in the past week ", "(total ", LENGTH(recent), " orders):")
        rows ← FLATTEN([o.order_id,o.customer_id,o.order_time,  o.status,o.total] FOR o IN recent)
        TableCreator(frame,"Order statistics", ("OrderID","CustomerID","Time","Status","Amount"),rows)
        LABEL(frame,"Total amount: ", Σ(o.total FOR o IN recent).FORMAT(2))
        RETURN (recent, frame)
    END FUNCTION

    FUNCTION print_all_ingredients(window) → TABLE
        data ← self.get_item()
        inv ← data["inventory"]
        thres ← data["threshold"]
        rows ← []
        FOR it IN inv["ingredients"] DO
            id,name,stock,unit ← it.ingredient_id,it.name,it.stock,it.unit
            IF id IN thres AND stock ≤ thres[id] THEN
                name ← BOLD(name)
            APPEND rows, [id,name,stock,unit]
        END FOR
        RETURN TableCreator(window, "Ingredients inventory list (bold ⇒ below threshold):", ("ingredient_id","name","stock","unit"), FLATTEN(rows))
    END FUNCTION

    FUNCTION prediction_output(window) → TABLE
        model ← NEW LinearRegression.Model()
        RETURN model.print_output(window)
    END FUNCTION

    FUNCTION list_purchase_orders(window) → (ARRAY orders, TABLE gui)
        orders ← self.get_item()["ingredient_order"].get("purchase_orders",[])
        rows   ← FLATTEN([po.purchase_id,po.ingredient_name,po.ingredient_id, po.quantity,po.total_price,po.order_time,po.status] FOR po IN orders)
        table ← TableCreator(window,"Current replenishment order", ("ReplenishmentID","Food","FoodID","Quantity", "Total price","Time","Status"), rows)
        RETURN (orders, table)
    END FUNCTION

    PROCEDURE update_purchase_order_status(rid, new_stat)
        data ← self.get_item()
        orders ← data["ingredient_order"]["purchase_orders"]
        inv ← data["inventory"]
        ingreds ← inv["ingredients"]

        FOR po IN orders DO
            IF po.purchase_id ≠ INTEGER(rid) THEN CONTINUE
            old ← po.status
            qty ← PARSE_FLOAT(po.quantity)          // extract numeric part
            ing ← FIND_FIRST(ingreds, λ x : x.ingredient_id = INTEGER(po.ingredient_id))
            IF old="Ordered"   AND new_stat="Received" THEN
                ing.stock ← (ing.stock + qty).ROUND(2)
            IF old="Received"  AND new_stat="Cancelled" THEN
                ing.stock ← MAX(ing.stock - qty,0).ROUND(2)
            IF old="Received"  AND new_stat="Ordered" THEN
                new_stat ← "Received"                // ignore downgrade
            po.status ← new_stat
            BREAK
        END FOR
        self.system.write_ingredient_order(self,data["ingredient_order"])
        self.system.write_ingredients(self,inv)
        INFOBOX("ReplenishmentID ", rid, " status: ", old, " → ", new_stat)
    END PROCEDURE

    PROCEDURE add_purchase_order( ingredient_id, quantity )
        data ← self.get_item()
        inv ← data["inventory"]
        ing ← FIND_FIRST(inv["ingredients"],
                          λ x : x.ingredient_id = INTEGER(ingredient_id))
        IF ing IS NULL THEN ERRORBOX("Ingredient not found"); RETURN

        unit  ← ing.unit
        price ← ing.price_per_unit
        total ← ROUND(price * FLOAT(quantity),2)
        poTbl ← data["ingredient_order"]["purchase_orders"]
        next_id ← (poTbl[-1].purchase_id + 1) IF poTbl ELSE 1

        new_po ← { purchase_id   : next_id,
                   ingredient_id : ingredient_id,
                   ingredient_name: ing.name,
                   quantity      : quantity, unit,
                   total_price   : total,
                   order_time    : ISO_TIMESTAMP_NOW(),
                   status        : "Ordered" }
        APPEND new_po TO poTbl
        self.system.write_ingredient_order(self,data["ingredient_order"])
        LOG("Added replenishment ", next_id)
    END PROCEDURE

    PROCEDURE delete_purchase_order(purchase_id)
        data   ← self.get_item()
        poTbl  ← data["ingredient_order"]["purchase_orders"]
        IF REMOVE_FIRST(poTbl, λ p : p.purchase_id = purchase_id) THEN
            self.system.write_ingredient_order(self,data["ingredient_order"])
            INFOBOX("Purchase order ", purchase_id, " deleted")
        ELSE
            ERRORBOX("Purchase order ", purchase_id, " not found")
    END PROCEDURE

    FUNCTION list_feedback(window) → FRAME
        frame ← NEW Frame(window)
        fb    ← self.get_item()["feedbacks"]["feedback"]
        rows  ← FLATTEN([f.feedback_id,f.customer_id,f.dish_id,
                          f.rating,f.comment,
                          f.time OR f.Time OR "N/A"]  FOR f IN fb)
        TableCreator(frame,"Feedbacks",
                     ("ID","CustomerID","DishID","Rating","Comment","Time"),rows)
        RETURN frame
    END FUNCTION
END CLASS

PROCEDURE manager_interface(mgr : Manager, root_window)
    win ← NEW Toplevel(root_window)
    win.fullscreen ← TRUE

    LOOP
        cmd ← Manager_choice(win)
        SWITCH cmd
        CASE "1":
            sub ← tripleOption(win,"Users Options:","Pending approval",  "Approved","Quit")
            IF sub = "1":
                frame,pending ← mgr.panel.show_pending(win)
                op ← tripleOption(win,"Users(Pending):","Approve","Reject","Quit")
                IF op="1": acc ← ApprovalPage(win,"accID to approve:"); mgr.approve(acc)
                IF op="2": acc ← ApprovalPage(win,"accID to reject:");  mgr.reject(acc)
                frame.destroy()

            IF sub = "2":
                users,frame ← mgr.list_approved(win)
                op ← tripleOption(win,"Approved:","Modify","Delete","Quit")
                IF op="1":
                    (uid,nr,np) ← Entry_form(win,"Modify", ("accID","New role","New password"))
                    mgr.modify_user(uid, nr OR NULL, np OR NULL)
                IF op="2":
                    uid ← ApprovalPage(win,"accID to delete:")
                    mgr.delete(uid)
                frame.destroy()

        CASE "2":
            pending, frame ← mgr.list_pending_orders(win)
            op ← doubleOption(win,"Orders:","Update order","Quit")
            IF op="1":
                (oid,state) ← Entry_form(win,"Update order",
                                         ("OrderID","Status:"))
                mgr.update_order_status(oid, state.title())
            frame.destroy()

        CASE "3":
            table ← mgr.print_all_ingredients(win)
            op ← doubleOption(win,"Inventory:","Predict next week","Quit")

            IF op="1":
                pred_table ← mgr.prediction_output(win)
                sub ← doubleOption(win,"Prediction:","Replenishment","Quit")
                IF sub="1":
                    orders, lpo ← mgr.list_purchase_orders(win)
                    act ← tripleOption(win,"Replenishment:",
                                        "New","Update","Quit")
                    IF act="1":
                        list_frame ← TableCreator(win,"Ingredient list", … )
                        (iid,qty) ← Entry_form(win,"New",
                                               ("Ingredient ID","Amount:"))
                        mgr.add_purchase_order(iid,qty)
                        list_frame.destroy()

                    IF act="2":
                        (pid,) ← Entry_form(win,"Update",("Replenishment ID:",))
                        choice ← doubleOption(win,"Options","Update status","Delete")
                        IF choice="1":
                            (stat,) ← Entry_form(win,"Status",
                                                 ("New status:",))
                            mgr.update_purchase_order_status(pid, stat.title())
                        IF choice="2":
                            mgr.delete_purchase_order(pid)
                    lpo.destroy()
                pred_table.destroy()
            table.destroy()

        CASE "4":
            orders, frame ← mgr.financial_summary_past_week(win)
            ButtonCreator(win,"Options",("Quit",))
            frame.destroy()

        CASE "5":
            frame ← mgr.list_feedback(win)
            ButtonCreator(win,"Options",("Quit",))
            frame.destroy()

        CASE "6":
            win.destroy()
            BREAK

        DEFAULT:
            ERRORBOX("Invalid option")
    END LOOP
END PROCEDURE
