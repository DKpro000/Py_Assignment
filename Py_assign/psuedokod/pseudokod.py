FUNCTION cashier_interface(app, MainWindow):
    #Get menu data from app
    menu_data = app.get_item()
    menu = menu_data["menu"]

    # Create a new top-level window and tab interface
    Create a new window from MainWindow
    Create a Notebook inside the new window
    Create a main tab frame that is stored in NOtebook

    # Create a scrollable canvas for the main tab
    Create a Canvas in the main tab
    Add the canvas to the layout
    Call app.scrollBar to add scrollbar functionality to the canvas

    # Create a second top-level window (for checkout or detail display)
    Create a new top-level window as app.CWindow

    # Create a frame inside the canvas for scrolling content
    Create a scrollable frame inside the canvas
    Link the scroll region to the frame and make it size dynamically

    # Make the canvas adapt its width on resize
    Bind a resize handler that updates the canvas frame width and height

    # Add the main tab to the notebook and show it
    Add tab labeled "ALL" to the notebook
    Display the notebook

    # Define number of columns for layout
    Set number of columns = 3
    Set initial row index = 0

    # Group menu items by category
    For each item in menu["menu_items"]:
        Group items under their "category" key (default is "Unknown")

    # Add all items to the "ALL" tab, grouped by category
    For each category and list of items:
        Add a label for the category to the scrollable frame

        For each item in category list:
            Calculate column and row position
            Create a bordered frame for the item
            Call app.printCols to populate the frame with image, name, and price

        Update the row index for the next category group

    # Configure columns to expand evenly
    For each column in 0 to cols:
        Set column weight = 1

    # Create individual tabs per category with same content layout
    For each category and list of items:
        Create a new tab for this category
        Add a scrollable container for items

        Save reference to the category frame in app.category_frames

        For each item in category list:
            Calculate column and row position
            Create a bordered frame for the item
            Call app.printCols to populate the frame with image, name, and price

        Configure category tab columns to expand evenly

    # Add additional utility tabs/buttons
    Call app.Settings with notebook
    Call app.PrintReceipt with notebook
    Call app.report with notebook
    Call app.Quit with notebook and the main window

FUNCTION printCols(CWindow, innerFrame, image_path, dish, price):
    # making sure that all items start with the quantity of
    IF dish not in dish_quantities:
        Initialize dish quantity to 0

    # Create outer frame inside the container
    Create a new frame inside innerFrame

    # Load and display the image (if available)
    IF image file exists at image_path:
        TRY:
            Load the image
            Save a reference to avoid garbage collection
            Display the image in the frame
        EXCEPT:
            Display an error message: "Error loading image"
    ELSE:
        Display a message: "Image not found"

    # Show dish name and price
    Display a label with dish name and price (formatted as currency)

    # Create a frame for quantity controls
    Create qty_frame inside the main frame

    # Set up variable to track/display current quantity
    Create a StringVar set to current quantity of the dish
    Display the quantity in a label bound to StringVar

    # functions for the increase and decrease buttons
    DEFINE increase():
        IF checkIngredientRequired returns False:
            RETURN (do not add item)

        Increment dish quantity
        Update qty_var to new quantity
        Add [dish, price] to cart
        Add price to total
        Refresh the cart display in CWindow

    DEFINE decrease():
        IF current quantity > 0:
            Decrement dish quantity
            Update qty_var

            # Remove the dish from the cart (first match only)
            FOR each item in cart:
                IF item matches the dish:
                    Subtract price from total
                    Remove item from cart
                    BREAK

            Restore ingredients using checkIngredientRollback
            Refresh the cart display in CWindow

    # Add "+" and "-" buttons linked to increase and decrease functions
    Add "-" button to qty_frame with command = decrease
    Add "+" button to qty_frame with command = increase
_name = "name"