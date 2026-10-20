import tkinter as tk
from tkinter import ttk

from services.api_client import get_rate

CURRENCIES = ["USD", "PHP", "EUR", "JPY"]


class AppWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Currency Converter")

        self.amount_var = tk.StringVar()
        self.from_var = tk.StringVar(value="USD")
        self.to_var = tk.StringVar(value="PHP")
        self.result_var = tk.StringVar(value="")
        self.rate_var = tk.StringVar(value="")

        tk.Label(root, text="Amount").grid(row=0, column=0, padx=8, pady=6)
        amount_entry = tk.Entry(root, textvariable=self.amount_var)
        amount_entry.grid(row=0, column=1, padx=8, pady=6)
        amount_entry.bind("<Return>", lambda _event: self.convert())

        ttk.Combobox(
            root,
            textvariable=self.from_var,
            values=CURRENCIES,
            state="readonly",
            width=8,
        ).grid(row=1, column=0, padx=8)
        ttk.Combobox(
            root, textvariable=self.to_var, values=CURRENCIES, state="readonly", width=8
        ).grid(row=1, column=1, padx=8)

        tk.Button(root, text="Convert", command=self.convert).grid(
            row=2, column=0, columnspan=2, pady=6
        )

        tk.Label(root, textvariable=self.result_var, font=("Arial", 12, "bold")).grid(
            row=3, column=0, columnspan=2
        )
        tk.Label(root, textvariable=self.rate_var).grid(
            row=4, column=0, columnspan=2, pady=(0, 8)
        )

    def convert(self) -> None:
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            self.result_var.set("Please enter a number.")
            return
        try:
            rate = get_rate(self.from_var.get(), self.to_var.get())
        except Exception as error:  # FR-07 will replace this with clear messages
            self.result_var.set(f"Error: {error}")
            return
        self.result_var.set(
            f"{amount:,.2f} {self.from_var.get()} = {amount * rate:,.2f} {self.to_var.get()}"
        )
        self.rate_var.set(f"1 {self.from_var.get()} = {rate:.6f} {self.to_var.get()}")
