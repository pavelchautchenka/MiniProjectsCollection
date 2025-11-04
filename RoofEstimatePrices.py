from tkinter import *
from fpdf import FPDF

# Create the main window
window = Tk()
window.title("Roofing Job Estimator")

# Initialize variables
tasks = {
    "Roof Installation": 2000,
    "Insulation Installation": 1500,
    "Gutter Installation": 500,
    "Roof Repair": 800
}
job_items = []
total_cost = 0.0


# Function to add a task to the job estimate
def add_task():
    selected_task = task_listbox.get(ANCHOR)
    if selected_task and quantity_entry.get().isdigit():
        quantity = int(quantity_entry.get())
        cost = tasks[selected_task]
        item_total = cost * quantity
        job_items.append((selected_task, quantity, item_total))
        total_cost_entry.delete(0, END)
        total_cost_entry.insert(END, str(calculate_total()))
        update_job_text()
    else:
        job_text.insert(END, "Please enter a valid quantity.\n")


# Function to calculate the total cost
def calculate_total():
    total = 0.0
    for item in job_items:
        total += item[2]
    return total


# Function to generate and save the job estimate as a PDF
def generate_estimate():
    client_name = client_entry.get()

    if not client_name:
        job_text.insert(END, "Please enter the client's name.\n")
        return

    pdf = FPDF()
    pdf.add_page()

    # Set up PDF formatting
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, txt="Roofing Job Estimate", align="C")
    pdf.ln(10)  # Move to the next line
    pdf.cell(0, 10, txt="Client: " + client_name, align="L")
    pdf.ln(10)

    # Add job items to PDF
    for item in job_items:
        task_name, quantity, item_total = item
        pdf.cell(0, 10, txt=f"Task: {task_name}, Quantity: {quantity}, Total: ${item_total}", align="L")
        pdf.ln(10)

    # Add total cost to PDF
    pdf.cell(0, 10, txt="Total Cost: $" + str(calculate_total()), align="L")

    # Save the PDF file
    pdf.output("roofing_job_estimate.pdf")
    job_text.insert(END, "Job estimate generated as 'roofing_job_estimate.pdf'.\n")


# GUI layout
task_label = Label(window, text="Task:")
task_label.pack()

task_listbox = Listbox(window, selectmode=SINGLE)
for task in tasks:
    task_listbox.insert(END, task)
task_listbox.pack()

quantity_label = Label(window, text="Quantity:")
quantity_label.pack()

quantity_entry = Entry(window)
quantity_entry.pack()

add_button = Button(window, text="Add Task", command=add_task)
add_button.pack()

total_cost_label = Label(window, text="Total Cost:")
total_cost_label.pack()

total_cost_entry = Entry(window)
total_cost_entry.pack()
total_cost_entry.config(state='readonly')  # Disable manual editing of the total cost

client_label = Label(window, text="Client's Name:")
client_label.pack()

client_entry = Entry(window)
client_entry.pack()

generate_button = Button(window, text="Generate Estimate", command=generate_estimate)
generate_button.pack()

job_text = Text(window, height=10, width=50)
job_text.pack()


# Function to update the job text
def update_job_text():
    job_text.delete(1.0, END)
    for item in job_items:
        job_text.insert(END, f"Task: {item[0]}, Quantity: {item[1]}, Total: ${item[2]}\n")


# Start the GUI event loop
window.mainloop()
