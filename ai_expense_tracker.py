import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
import urllib.request
import threading

# ─── Config ──────────────────────────────────────────────────
DATA_FILE = "expenses.json"
API_KEY = "your-api-key-here"  # <-- Apna Anthropic API key yahan daalo

# ─── Data ────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Claude AI API ───────────────────────────────────────────
def ask_claude(prompt, callback):
    def run():
        try:
            body = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())
                text = result["content"][0]["text"]
                callback(text)
        except Exception as e:
            callback(f"Error: {str(e)}")
    threading.Thread(target=run, daemon=True).start()

# ─── Main App ────────────────────────────────────────────────
class AIExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 AI Expense Tracker")
        self.root.geometry("900x680")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        self.expenses = load_data()
        self.selected_index = None

        self.build_ui()
        self.refresh_table()
        self.update_summary()

    def build_ui(self):
        # ── Title ──
        tk.Label(self.root, text="🤖 AI Expense Tracker",
                 font=("Georgia", 22, "bold"),
                 bg="#1a1a2e", fg="#e94560").pack(pady=(14, 2))
        tk.Label(self.root, text="Powered by Claude AI",
                 font=("Georgia", 9, "italic"),
                 bg="#1a1a2e", fg="#a0a0c0").pack()

        # ── Tabs ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#16213e", foreground="#a0a0c0",
                        font=("Consolas", 10, "bold"), padding=[14, 6])
        style.map("TNotebook.Tab", background=[("selected", "#e94560")],
                  foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=10)

        # Tab 1: Expenses
        tab1 = tk.Frame(self.notebook, bg="#1a1a2e")
        self.notebook.add(tab1, text="📋 Expenses")
        self.build_expense_tab(tab1)

        # Tab 2: AI Chat
        tab2 = tk.Frame(self.notebook, bg="#1a1a2e")
        self.notebook.add(tab2, text="💬 AI Chat")
        self.build_chat_tab(tab2)

        # Tab 3: AI Analysis
        tab3 = tk.Frame(self.notebook, bg="#1a1a2e")
        self.notebook.add(tab3, text="📊 AI Analysis")
        self.build_analysis_tab(tab3)

    # ── Tab 1: Expense Entry ──────────────────────────────────
    def build_expense_tab(self, parent):
        input_frame = tk.Frame(parent, bg="#16213e")
        input_frame.pack(fill="x", padx=16, pady=10)

        # Description
        tk.Label(input_frame, text="📝 Description", font=("Consolas", 10),
                 bg="#16213e", fg="#a0a0c0").grid(row=0, column=0, padx=(12,4), pady=10, sticky="w")
        self.desc_entry = tk.Entry(input_frame, width=24, font=("Consolas", 11),
                                   bg="#0f3460", fg="white", insertbackground="white", relief="flat", bd=6)
        self.desc_entry.grid(row=0, column=1, padx=(0,10), pady=10)

        # Amount
        tk.Label(input_frame, text="💵 Amount (Rs)", font=("Consolas", 10),
                 bg="#16213e", fg="#a0a0c0").grid(row=0, column=2, padx=(4,4), pady=10, sticky="w")
        self.amt_entry = tk.Entry(input_frame, width=12, font=("Consolas", 11),
                                  bg="#0f3460", fg="white", insertbackground="white", relief="flat", bd=6)
        self.amt_entry.grid(row=0, column=3, padx=(0,10), pady=10)

        # Category
        tk.Label(input_frame, text="📂 Category", font=("Consolas", 10),
                 bg="#16213e", fg="#a0a0c0").grid(row=0, column=4, padx=(4,4), pady=10, sticky="w")
        self.category_var = tk.StringVar(value="Food")
        self.categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
        cat_dropdown = ttk.Combobox(input_frame, textvariable=self.category_var,
                                    values=self.categories, width=13,
                                    font=("Consolas", 11), state="readonly")
        cat_dropdown.grid(row=0, column=5, padx=(0,10), pady=10)

        # AI Auto Category button
        tk.Button(input_frame, text="🤖 AI Category", command=self.ai_auto_category,
                  bg="#0f9b8e", fg="white", font=("Consolas", 9, "bold"),
                  relief="flat", padx=8, pady=4, cursor="hand2").grid(row=0, column=6, padx=4)

        # Buttons
        btn_frame = tk.Frame(parent, bg="#1a1a2e")
        btn_frame.pack(pady=4)
        for text, color, cmd in [
            ("➕ Add", "#e94560", self.add_expense),
            ("✏️ Update", "#0f9b8e", self.update_expense),
            ("🗑️ Delete", "#c84b31", self.delete_expense),
            ("🧹 Clear All", "#555577", self.clear_all),
        ]:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg=color, fg="white", font=("Consolas", 10, "bold"),
                      relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(parent, bg="#1a1a2e")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(6, 0))

        style = ttk.Style()
        style.configure("Treeview", background="#0f3460", foreground="white",
                        rowheight=26, fieldbackground="#0f3460", font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#e94560", foreground="white",
                        font=("Consolas", 10, "bold"))
        style.map("Treeview", background=[("selected", "#e94560")])

        cols = ("Date", "Description", "Category", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=9)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Description", width=260)
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("Amount", width=110, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Summary
        summary_frame = tk.Frame(parent, bg="#16213e")
        summary_frame.pack(fill="x", padx=16, pady=8)
        self.total_label = tk.Label(summary_frame, text="Total: Rs. 0",
                                     font=("Georgia", 13, "bold"), bg="#16213e", fg="#e94560")
        self.total_label.pack(side="left", padx=14, pady=6)
        self.count_label = tk.Label(summary_frame, text="Entries: 0",
                                     font=("Georgia", 11), bg="#16213e", fg="#a0a0c0")
        self.count_label.pack(side="right", padx=14, pady=6)

    # ── Tab 2: AI Chat ────────────────────────────────────────
    def build_chat_tab(self, parent):
        tk.Label(parent, text="💬 Chat with AI about your expenses",
                 font=("Georgia", 12, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=(12,4))

        self.chat_box = scrolledtext.ScrolledText(parent, height=18, width=80,
                                                   font=("Consolas", 10),
                                                   bg="#0f3460", fg="white",
                                                   insertbackground="white",
                                                   relief="flat", bd=8, state="disabled")
        self.chat_box.pack(padx=16, pady=6, fill="both", expand=True)

        input_row = tk.Frame(parent, bg="#1a1a2e")
        input_row.pack(fill="x", padx=16, pady=6)

        self.chat_entry = tk.Entry(input_row, font=("Consolas", 11),
                                   bg="#0f3460", fg="white", insertbackground="white",
                                   relief="flat", bd=6)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat())

        tk.Button(input_row, text="Send 🚀", command=self.send_chat,
                  bg="#e94560", fg="white", font=("Consolas", 10, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="right")

        # Quick prompts
        quick_frame = tk.Frame(parent, bg="#1a1a2e")
        quick_frame.pack(pady=4)
        quick_prompts = [
            "Mera total kitna hai?",
            "Kahan zyada kharch ho raha hai?",
            "Paise bachane ke tips do",
        ]
        for q in quick_prompts:
            tk.Button(quick_frame, text=q, command=lambda x=q: self.quick_chat(x),
                      bg="#16213e", fg="#a0a0c0", font=("Consolas", 9),
                      relief="flat", padx=8, pady=4, cursor="hand2").pack(side="left", padx=4)

    # ── Tab 3: AI Analysis ────────────────────────────────────
    def build_analysis_tab(self, parent):
        tk.Label(parent, text="📊 AI-Powered Expense Analysis",
                 font=("Georgia", 12, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=(12,4))

        btn_frame = tk.Frame(parent, bg="#1a1a2e")
        btn_frame.pack(pady=8)

        for text, color, cmd in [
            ("🔍 Analyze Spending", "#e94560", self.analyze_spending),
            ("💡 Budget Suggestion", "#0f9b8e", self.budget_suggestion),
            ("⚠️ Overspending Alert", "#c84b31", self.overspending_alert),
        ]:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg=color, fg="white", font=("Consolas", 10, "bold"),
                      relief="flat", padx=14, pady=8, cursor="hand2").pack(side="left", padx=8)

        self.analysis_box = scrolledtext.ScrolledText(parent, height=20, width=80,
                                                       font=("Consolas", 10),
                                                       bg="#0f3460", fg="white",
                                                       insertbackground="white",
                                                       relief="flat", bd=8, state="disabled")
        self.analysis_box.pack(padx=16, pady=8, fill="both", expand=True)

    # ─── AI Features ─────────────────────────────────────────
    def ai_auto_category(self):
        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showwarning("Error", "Pehle description daalo!")
            return
        self.show_analysis("🤖 Category detect kar raha hoon...\n")
        prompt = f"""Given this expense description: "{desc}"
Choose the BEST category from: Food, Transport, Shopping, Bills, Entertainment, Health, Other.
Reply with ONLY the category name, nothing else."""
        def callback(result):
            result = result.strip()
            if result in self.categories:
                self.category_var.set(result)
                self.root.after(0, lambda: messagebox.showinfo("AI Category", f"Category set: {result} ✅"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("AI", f"Suggested: {result}"))
        ask_claude(prompt, callback)

    def analyze_spending(self):
        if not self.expenses:
            messagebox.showwarning("Error", "Koi expense nahi hai abhi!")
            return
        self.show_analysis("🔍 Analyzing your expenses...\n\n")
        summary = self.get_expense_summary()
        prompt = f"""Analyze these expenses and give insights in simple English (3-4 lines):
{summary}
Tell: which category has most spending, any unusual patterns, and 2 tips to save money."""
        ask_claude(prompt, lambda r: self.show_analysis(f"📊 Analysis:\n\n{r}\n"))

    def budget_suggestion(self):
        if not self.expenses:
            messagebox.showwarning("Error", "Koi expense nahi hai abhi!")
            return
        self.show_analysis("💡 Budget suggestion generate ho raha hai...\n\n")
        summary = self.get_expense_summary()
        prompt = f"""Based on these expenses:
{summary}
Suggest a realistic monthly budget for each category in Indian Rupees.
Format as a simple list. Keep it practical and helpful."""
        ask_claude(prompt, lambda r: self.show_analysis(f"💡 Budget Suggestion:\n\n{r}\n"))

    def overspending_alert(self):
        if not self.expenses:
            messagebox.showwarning("Error", "Koi expense nahi hai abhi!")
            return
        self.show_analysis("⚠️ Overspending check ho raha hai...\n\n")
        summary = self.get_expense_summary()
        prompt = f"""Look at these expenses:
{summary}
Identify if the person is overspending in any category.
Give a friendly warning and specific advice in simple English. Be direct but encouraging."""
        ask_claude(prompt, lambda r: self.show_analysis(f"⚠️ Overspending Alert:\n\n{r}\n"))

    def send_chat(self):
        msg = self.chat_entry.get().strip()
        if not msg:
            return
        self.chat_entry.delete(0, tk.END)
        self.append_chat(f"You: {msg}\n")
        summary = self.get_expense_summary()
        prompt = f"""You are a helpful personal finance assistant.
User's current expenses:
{summary}

User asks: {msg}

Reply in simple, friendly English in 2-3 lines."""
        self.append_chat("🤖 AI: Thinking...\n")
        def callback(reply):
            self.chat_box.config(state="normal")
            content = self.chat_box.get("1.0", tk.END)
            content = content.replace("🤖 AI: Thinking...\n", "")
            self.chat_box.delete("1.0", tk.END)
            self.chat_box.insert(tk.END, content)
            self.chat_box.config(state="disabled")
            self.append_chat(f"🤖 AI: {reply}\n\n")
        ask_claude(prompt, callback)

    def quick_chat(self, question):
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.insert(0, question)
        self.send_chat()

    # ─── Helpers ─────────────────────────────────────────────
    def get_expense_summary(self):
        if not self.expenses:
            return "No expenses yet."
        total = sum(e["amount"] for e in self.expenses)
        by_cat = {}
        for e in self.expenses:
            by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
        lines = [f"Total spent: Rs. {total:.2f}", "By category:"]
        for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
            lines.append(f"  - {cat}: Rs. {amt:.2f}")
        lines.append("Recent expenses:")
        for e in self.expenses[-5:]:
            lines.append(f"  - {e['description']} (Rs. {e['amount']}) [{e['category']}]")
        return "\n".join(lines)

    def show_analysis(self, text):
        self.analysis_box.config(state="normal")
        self.analysis_box.delete("1.0", tk.END)
        self.analysis_box.insert(tk.END, text)
        self.analysis_box.config(state="disabled")
        self.notebook.select(2)

    def append_chat(self, text):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, text)
        self.chat_box.see(tk.END)
        self.chat_box.config(state="disabled")

    def add_expense(self):
        desc = self.desc_entry.get().strip()
        amt = self.amt_entry.get().strip()
        if not desc:
            messagebox.showwarning("Error", "Description daalo!")
            return
        try:
            amount = float(amt)
        except ValueError:
            messagebox.showwarning("Error", "Amount sahi daalo!")
            return
        self.expenses.append({
            "date": datetime.now().strftime("%d-%m-%Y"),
            "description": desc,
            "category": self.category_var.get(),
            "amount": amount
        })
        save_data(self.expenses)
        self.clear_inputs()
        self.refresh_table()
        self.update_summary()

    def update_expense(self):
        if self.selected_index is None:
            messagebox.showwarning("Error", "Pehle entry select karo!")
            return
        desc = self.desc_entry.get().strip()
        amt = self.amt_entry.get().strip()
        try:
            amount = float(amt)
        except ValueError:
            messagebox.showwarning("Error", "Amount sahi daalo!")
            return
        self.expenses[self.selected_index].update({
            "description": desc, "category": self.category_var.get(), "amount": amount
        })
        save_data(self.expenses)
        self.clear_inputs()
        self.refresh_table()
        self.update_summary()

    def delete_expense(self):
        if self.selected_index is None:
            messagebox.showwarning("Error", "Pehle entry select karo!")
            return
        if messagebox.askyesno("Confirm", "Delete karna chahte ho?"):
            self.expenses.pop(self.selected_index)
            save_data(self.expenses)
            self.clear_inputs()
            self.refresh_table()
            self.update_summary()

    def clear_all(self):
        if self.expenses and messagebox.askyesno("Confirm", "Saari entries delete karo?"):
            self.expenses = []
            save_data(self.expenses)
            self.clear_inputs()
            self.refresh_table()
            self.update_summary()

    def clear_inputs(self):
        self.desc_entry.delete(0, tk.END)
        self.amt_entry.delete(0, tk.END)
        self.category_var.set("Food")
        self.selected_index = None

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        self.selected_index = idx
        exp = self.expenses[idx]
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, exp["description"])
        self.amt_entry.delete(0, tk.END)
        self.amt_entry.insert(0, str(exp["amount"]))
        self.category_var.set(exp["category"])

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for exp in self.expenses:
            self.tree.insert("", "end", values=(
                exp["date"], exp["description"],
                exp["category"], f"Rs. {exp['amount']:.2f}"
            ))

    def update_summary(self):
        total = sum(e["amount"] for e in self.expenses)
        self.total_label.config(text=f"Total: Rs. {total:.2f}")
        self.count_label.config(text=f"Entries: {len(self.expenses)}")


# ─── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = AIExpenseTracker(root)
    root.mainloop()