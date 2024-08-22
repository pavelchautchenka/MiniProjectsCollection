from tkinter import *
import ast

app = Tk()
app.title("Calculator")
index = 0

def append_digit(digit):
    global index
    display.insert(index, digit)
    index += 1


def append_operator(operator):
    global index
    length = len(operator)
    display.insert(index, operator)
    index += length


def clear_display():
    display.delete(0, END)


def evaluate_expression():
    expression = display.get()
    try:
        node = ast.parse(expression, mode="eval")
        result = eval(compile(node, '<string>', 'eval'))
        clear_display()
        display.insert(0, result)
    except Exception:
        clear_display()
        display.insert(0, "Ошибка")


def remove_last():
    expression = display.get()
    if len(expression):
        new_expression = expression[:-1]
        clear_display()
        display.insert(0, new_expression)


def create_button(text, row, column, width=6, height=3, command=None):
    Button(app, text=text, width=width, height=height, command=command).grid(row=row, column=column)


display = Entry(app, font=("Arial", 20))
display.grid(row=1, columnspan=6, sticky=W + E)

digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for idx, digit in enumerate(digits):
    row = (idx // 3) + 2
    column = idx % 3
    create_button(digit, row, column, command=lambda num=digit: append_digit(num))

create_button("0", 5, 1, command=lambda: append_digit(0))

operations = ['+', '-', '*', '/', '*3.14', "%", "(", "**", ")", "**2"]
for idx, operation in enumerate(operations):
    row = (idx // 3) + 2
    column = (idx % 3) + 3
    create_button(operation, row, column, command=lambda op=operation: append_operator(op))

create_button("AC", 5, 0, command=clear_display)
create_button("=", 5, 2, command=evaluate_expression)
create_button("<-", 5, 4, command=remove_last)

app.mainloop()
