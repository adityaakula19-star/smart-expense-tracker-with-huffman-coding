import os
import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

import database
import reports
from huffman import compress_file, decompress_file


CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Salary", "Other"]


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Tracker with Huffman Compression")
        self.root.geometry("1040x680")
        self.root.minsize(920, 600)
        self.user = None
        self.selected_transaction_id = None
        self.dark_mode = False

        database.initialize_database()
        self.colors = self._theme()
        self._build_login()

    def _theme(self):
        if self.dark_mode:
            return {
                "bg": "#15171c",
                "panel": "#20242c",
                "text": "#f4f6fb",
                "muted": "#a9b0bf",
                "accent": "#2fbf71",
                "danger": "#f05d5e",
                "entry": "#2b303a",
            }
        return {
            "bg": "#f4f6f8",
            "panel": "#ffffff",
            "text": "#1f2933",
            "muted": "#59636f",
            "accent": "#1f8a70",
            "danger": "#c24141",
            "entry": "#ffffff",
        }

    def _clear(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.configure(bg=self.colors["bg"])

    def _label(self, parent, text, size=10, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", size, "bold" if bold else "normal"),
        )

    def _button(self, parent, text, command, accent=False, danger=False):
        bg = self.colors["accent"] if accent else self.colors["panel"]
        fg = "white" if accent else self.colors["text"]
        if danger:
            bg = self.colors["danger"]
            fg = "white"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=tk.FLAT,
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold" if accent or danger else "normal"),
        )

    def _build_login(self):
        self._clear()
        card = tk.Frame(self.root, bg=self.colors["panel"], padx=34, pady=32)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._label(card, "Smart Expense Tracker", 22, True).grid(row=0, column=0, columnspan=2, pady=(0, 6))
        self._label(card, "Local reports compressed with Huffman Coding", 10).grid(row=1, column=0, columnspan=2, pady=(0, 22))

        self._label(card, "Username").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.username_var = tk.StringVar()
        tk.Entry(card, textvariable=self.username_var, width=32, bg=self.colors["entry"], fg=self.colors["text"]).grid(row=2, column=1, pady=6)

        self._label(card, "Password").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.password_var = tk.StringVar()
        tk.Entry(card, textvariable=self.password_var, width=32, show="*", bg=self.colors["entry"], fg=self.colors["text"]).grid(row=3, column=1, pady=6)

        actions = tk.Frame(card, bg=self.colors["panel"])
        actions.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        self._button(actions, "Login", self.login, True).pack(side=tk.LEFT, padx=6)
        self._button(actions, "Signup", self.signup).pack(side=tk.LEFT, padx=6)

    def signup(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if len(username) < 3:
            messagebox.showerror("Invalid username", "Username must contain at least 3 characters.")
            return
        if len(password) < 6 or not any(char.isdigit() for char in password):
            messagebox.showerror("Weak password", "Password must be at least 6 characters and include a number.")
            return
        try:
            user_id = database.create_user(username, password)
        except Exception:
            messagebox.showerror("Signup failed", "This username already exists.")
            return
        self.user = {"id": user_id, "username": username}
        self._build_main()

    def login(self):
        user = database.authenticate_user(self.username_var.get(), self.password_var.get())
        if not user:
            messagebox.showerror("Login failed", "Invalid username or password.")
            return
        self.user = user
        self._build_main()

    def _build_main(self):
        self._clear()
        top = tk.Frame(self.root, bg=self.colors["panel"], padx=18, pady=12)
        top.pack(fill=tk.X)
        self._label(top, f"Welcome, {self.user['username']}", 15, True).pack(side=tk.LEFT)
        self._button(top, "Dark Mode" if not self.dark_mode else "Light Mode", self.toggle_theme).pack(side=tk.RIGHT, padx=6)
        self._button(top, "Logout", self._build_login).pack(side=tk.RIGHT, padx=6)

        body = tk.Frame(self.root, bg=self.colors["bg"], padx=14, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=self.colors["panel"], padx=14, pady=14)
        left.pack(side=tk.LEFT, fill=tk.Y)
        right = tk.Frame(body, bg=self.colors["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

        self._build_form(left)
        self._build_dashboard(right)
        self._build_table(right)
        self.refresh_all()

    def _build_form(self, parent):
        self._label(parent, "Transaction", 14, True).pack(anchor=tk.W, pady=(0, 12))
        self.type_var = tk.StringVar(value="Expense")
        ttk.Combobox(parent, textvariable=self.type_var, values=["Expense", "Income"], state="readonly", width=25).pack(anchor=tk.W, pady=4)

        self.category_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(parent, textvariable=self.category_var, values=CATEGORIES, width=25).pack(anchor=tk.W, pady=4)

        self.amount_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.amount_var, width=28, bg=self.colors["entry"], fg=self.colors["text"]).pack(anchor=tk.W, pady=4)
        self.amount_var.set("Amount")

        self.date_var = tk.StringVar(value=date.today().isoformat())
        tk.Entry(parent, textvariable=self.date_var, width=28, bg=self.colors["entry"], fg=self.colors["text"]).pack(anchor=tk.W, pady=4)

        self.description_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.description_var, width=28, bg=self.colors["entry"], fg=self.colors["text"]).pack(anchor=tk.W, pady=4)
        self.description_var.set("Description")

        self._button(parent, "Add", self.add_transaction, True).pack(fill=tk.X, pady=(14, 4))
        self._button(parent, "Update Selected", self.update_transaction).pack(fill=tk.X, pady=4)
        self._button(parent, "Delete Selected", self.delete_transaction, danger=True).pack(fill=tk.X, pady=4)
        self._button(parent, "Clear Form", self.clear_form).pack(fill=tk.X, pady=4)

        tk.Frame(parent, bg=self.colors["panel"], height=18).pack()
        self._label(parent, "Reports", 14, True).pack(anchor=tk.W, pady=(12, 8))
        self._button(parent, "Export CSV", lambda: self.export_report("csv")).pack(fill=tk.X, pady=4)
        self._button(parent, "Export TXT", lambda: self.export_report("txt")).pack(fill=tk.X, pady=4)
        self._button(parent, "Compress Report", self.compress_report, True).pack(fill=tk.X, pady=4)
        self._button(parent, "Decompress .bin", self.decompress_report).pack(fill=tk.X, pady=4)

    def _build_dashboard(self, parent):
        self.cards = tk.Frame(parent, bg=self.colors["bg"])
        self.cards.pack(fill=tk.X)
        self.summary_vars = {
            "income": tk.StringVar(),
            "expense": tk.StringVar(),
            "balance": tk.StringVar(),
            "monthly": tk.StringVar(),
        }
        labels = [("Income", "income"), ("Expenses", "expense"), ("Balance", "balance"), ("This Month", "monthly")]
        for label, key in labels:
            card = tk.Frame(self.cards, bg=self.colors["panel"], padx=16, pady=12)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self._label(card, label, 10).pack(anchor=tk.W)
            self._label(card, "", 16, True).pack(anchor=tk.W)
            card.winfo_children()[1].configure(textvariable=self.summary_vars[key])

        chart_panel = tk.Frame(parent, bg=self.colors["panel"], padx=12, pady=12)
        chart_panel.pack(fill=tk.X, pady=(12, 12))
        self._label(chart_panel, "Category-wise Expense Analysis", 13, True).pack(anchor=tk.W)
        self.chart = tk.Canvas(chart_panel, height=150, bg=self.colors["panel"], highlightthickness=0)
        self.chart.pack(fill=tk.X)

    def _build_table(self, parent):
        tools = tk.Frame(parent, bg=self.colors["bg"])
        tools.pack(fill=tk.X)
        self.search_var = tk.StringVar()
        tk.Entry(tools, textvariable=self.search_var, width=40, bg=self.colors["entry"], fg=self.colors["text"]).pack(side=tk.LEFT, pady=4)
        self._button(tools, "Search", self.refresh_table).pack(side=tk.LEFT, padx=8)
        self._button(tools, "Reset", self.reset_search).pack(side=tk.LEFT)

        columns = ("ID", "Type", "Category", "Amount", "Date", "Description")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=110 if column != "Description" else 250)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.tree.bind("<<TreeviewSelect>>", self.select_transaction)

    def add_transaction(self):
        values = self._form_values()
        if not values:
            return
        database.add_transaction(self.user["id"], *values)
        self.clear_form()
        self.refresh_all()

    def update_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("No selection", "Select a transaction first.")
            return
        values = self._form_values()
        if not values:
            return
        database.update_transaction(self.selected_transaction_id, *values)
        self.clear_form()
        self.refresh_all()

    def delete_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("No selection", "Select a transaction first.")
            return
        database.delete_transaction(self.selected_transaction_id)
        self.clear_form()
        self.refresh_all()

    def _form_values(self):
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a number.")
            return None
        try:
            date.fromisoformat(self.date_var.get())
        except ValueError:
            messagebox.showerror("Invalid date", "Date must use YYYY-MM-DD format.")
            return None
        return (
            self.type_var.get(),
            self.category_var.get(),
            amount,
            self.date_var.get(),
            self.description_var.get().strip(),
        )

    def select_transaction(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        row = self.tree.item(selected[0], "values")
        self.selected_transaction_id = int(row[0])
        self.type_var.set(row[1])
        self.category_var.set(row[2])
        self.amount_var.set(row[3])
        self.date_var.set(row[4])
        self.description_var.set(row[5])

    def clear_form(self):
        self.selected_transaction_id = None
        self.type_var.set("Expense")
        self.category_var.set(CATEGORIES[0])
        self.amount_var.set("")
        self.date_var.set(date.today().isoformat())
        self.description_var.set("")
        if hasattr(self, "tree"):
            self.tree.selection_remove(self.tree.selection())

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_table()

    def refresh_dashboard(self):
        summary = database.dashboard_summary(self.user["id"])
        self.summary_vars["income"].set(f"Rs. {summary['total_income']:.2f}")
        self.summary_vars["expense"].set(f"Rs. {summary['total_expense']:.2f}")
        self.summary_vars["balance"].set(f"Rs. {summary['balance']:.2f}")
        self.summary_vars["monthly"].set(f"Rs. {summary['monthly_spending']:.2f}")
        self.draw_chart(summary["categories"])

    def draw_chart(self, categories):
        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 760)
        if not categories:
            self.chart.create_text(12, 75, text="No expense data yet", anchor=tk.W, fill=self.colors["muted"], font=("Segoe UI", 11))
            return

        max_value = max(amount for _, amount in categories) or 1
        bar_height = 20
        y = 18
        for category, amount in categories[:5]:
            bar_width = int((width - 220) * (amount / max_value))
            self.chart.create_text(8, y + 10, text=category, anchor=tk.W, fill=self.colors["text"], font=("Segoe UI", 10))
            self.chart.create_rectangle(110, y, 110 + bar_width, y + bar_height, fill=self.colors["accent"], outline="")
            self.chart.create_text(125 + bar_width, y + 10, text=f"Rs. {amount:.2f}", anchor=tk.W, fill=self.colors["muted"], font=("Segoe UI", 10))
            y += 26

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = database.list_transactions(self.user["id"], self.search_var.get())
        for row in rows:
            transaction_id, transaction_type, category, amount, entry_date, description = row
            self.tree.insert("", tk.END, values=(transaction_id, transaction_type, category, f"{amount:.2f}", entry_date, description))

    def reset_search(self):
        self.search_var.set("")
        self.refresh_table()

    def export_report(self, report_type):
        path = reports.generate_csv_report(self.user["id"], self.user["username"]) if report_type == "csv" else reports.generate_txt_report(self.user["id"], self.user["username"])
        messagebox.showinfo("Report generated", f"Saved report:\n{os.path.abspath(path)}")
        return path

    def compress_report(self):
        path = filedialog.askopenfilename(
            title="Choose TXT or CSV report",
            initialdir=os.path.abspath(reports.REPORT_DIR) if os.path.exists(reports.REPORT_DIR) else os.getcwd(),
            filetypes=[("Report files", "*.txt *.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        output_path = os.path.splitext(path)[0] + ".bin"
        result = compress_file(path, output_path)
        messagebox.showinfo(
            "Compression complete",
            f"Original Size: {result['original_size']} bytes\n"
            f"Compressed Size: {result['compressed_size']} bytes\n"
            f"Compression Ratio: {result['compression_ratio']}%\n\n"
            f"Saved: {output_path}",
        )

    def decompress_report(self):
        path = filedialog.askopenfilename(title="Choose compressed report", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if not path:
            return
        output_path = filedialog.asksaveasfilename(
            title="Save decompressed report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not output_path:
            return
        try:
            decompress_file(path, output_path)
        except Exception as exc:
            messagebox.showerror("Decompression failed", str(exc))
            return
        messagebox.showinfo("Decompression complete", f"Restored file:\n{output_path}")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.colors = self._theme()
        self._build_main()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
