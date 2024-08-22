from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import psycopg2

def execute_query(query, params=()):

    try:
        with psycopg2.connect(dbname="school", user="django_pavel", password="password", host="localhost", port="5432") as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    return cursor.fetchall()
                conn.commit()
    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))
    return None

def update_treeview():
    """Refresh the treeview with updated data from the database."""
    for item in tree.get_children():
        tree.delete(item)
    records = execute_query("SELECT * FROM students;")
    if records:
        for record in records:
            tree.insert('', END, values=record)

def initialize_database():
    """Create the students table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS students(
        student_id SERIAL PRIMARY KEY, 
        name TEXT, 
        address TEXT, 
        age INT, 
        phone_number TEXT
    );
    """
    execute_query(query)
    messagebox.showinfo("Information", "Table initialized successfully.")
    update_treeview()

def add_student():
    """Insert a new student record into the database."""
    query = "INSERT INTO students(name, address, age, phone_number) VALUES (%s, %s, %s, %s)"
    params = (name_var.get(), address_var.get(), age_var.get(), phone_var.get())
    execute_query(query, params)
    messagebox.showinfo("Information", "Student added successfully.")
    update_treeview()

def modify_student():
    """Update an existing student record in the database."""
    selected_item = tree.selection()[0]
    student_id = tree.item(selected_item)['values'][0]
    query = "UPDATE students SET name = %s, address = %s, age = %s, phone_number = %s WHERE student_id = %s"
    params = (name_var.get(), address_var.get(), age_var.get(), phone_var.get(), student_id)
    execute_query(query, params)
    messagebox.showinfo("Information", "Student record updated successfully.")
    update_treeview()

def remove_student():
    """Delete a student record from the database."""
    selected_item = tree.selection()[0]
    student_id = tree.item(selected_item)['values'][0]
    query = "DELETE FROM students WHERE student_id = %s"
    params = (student_id,)
    execute_query(query, params)
    messagebox.showinfo("Information", "Student record deleted successfully.")
    update_treeview()

# Main application window
app = Tk()
app.title("Student Management System")

# Variables
name_var = StringVar()
address_var = StringVar()
age_var = IntVar()
phone_var = StringVar()

# Input Frame
input_frame = LabelFrame(app, text="Student Information")
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

Label(input_frame, text="Name:").grid(row=0, column=0, pady=2, sticky="w")
Entry(input_frame, textvariable=name_var).grid(row=0, column=1, pady=2, sticky="ew")

Label(input_frame, text="Address:").grid(row=1, column=0, pady=2, sticky="w")
Entry(input_frame, textvariable=address_var).grid(row=1, column=1, pady=2, sticky="ew")

Label(input_frame, text="Age:").grid(row=2, column=0, pady=2, sticky="w")
Entry(input_frame, textvariable=age_var).grid(row=2, column=1, pady=2, sticky="ew")

Label(input_frame, text="Phone Number:").grid(row=3, column=0, pady=2, sticky="w")
Entry(input_frame, textvariable=phone_var).grid(row=3, column=1, pady=2, sticky="ew")

# Button Frame
button_frame = Frame(app)
button_frame.grid(row=1, column=0, pady=5, sticky="ew")

Button(button_frame, text="Initialize DB", command=initialize_database).grid(row=0, column=0, padx=5)
Button(button_frame, text="Add Student", command=add_student).grid(row=0, column=1, padx=5)
Button(button_frame, text="Modify Student", command=modify_student).grid(row=0, column=2, padx=5)
Button(button_frame, text="Remove Student", command=remove_student).grid(row=0, column=3, padx=5)

# Treeview Frame
tree_frame = Frame(app)
tree_frame.grid(row=2, column=0, pady=10, sticky="nsew")

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
tree.pack()

tree_scroll.config(command=tree.yview)

tree['columns'] = ("student_id", "name", "address", "age", "phone_number")
tree.column("#0", width=0, stretch=NO)
tree.column("student_id", anchor=CENTER, width=80)
tree.column("name", anchor=W, width=120)
tree.column("address", anchor=W, width=120)
tree.column("age", anchor=CENTER, width=50)
tree.column("phone_number", anchor=W, width=120)

tree.heading("student_id", text="ID", anchor=CENTER)
tree.heading("name", text="Name", anchor=CENTER)
tree.heading("address", text="Address", anchor=CENTER)
tree.heading("age", text="Age", anchor=CENTER)
tree.heading("phone_number", text="Phone Number", anchor=CENTER)

# Initialize and populate treeview
update_treeview()

app.mainloop()
