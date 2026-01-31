import tkinter as tk
from tkinter import messagebox
from backend import StoreBackend
from PIL import Image, ImageTk

class PrettyPinkStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pretty Pink Store")
        self.root.configure(bg="#ffe6f0")
        self.backend = StoreBackend()
        self.cart = []

        self.welcome_page()

    def welcome_page(self):
        self.clear_window()

        tk.Label(self.root, text="Pretty Pink Store", font=("Helvetica", 26, "bold"),
                 bg="#ffe6f0", fg="#ff66b3").pack(pady=40)
        tk.Button(self.root, text="Shop Now", font=("Helvetica", 16), bg="#ff99cc", fg="white",
                  command=self.show_products).pack(pady=20)

    def show_products(self):
        self.clear_window()

        self.main_frame = tk.Frame(self.root, bg="#ffc0cb")
        self.main_frame.pack(fill="both", expand=True)

        title = tk.Label(self.main_frame, text="Our Cute Collection 💕", font=("Helvetica", 20, "bold"),
                         bg="#ffc0cb", fg="#ff1493")
        title.pack(pady=20)

        canvas = tk.Canvas(self.main_frame, bg="#ffc0cb", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#ffc0cb")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        products = self.backend.fetch_products()
        self.images = {}
        max_columns = 5
        row = 0
        col = 0

        for product_id, product_name, product_price, product_qty, image_path in products:
            frame = tk.Frame(scroll_frame, bg="#fff0f5", bd=2, relief="groove", padx=10, pady=10)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            try:
                img = Image.open(f"images/{image_path}")
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.images[product_id] = photo
                tk.Label(frame, image=photo, bg="#fff0f5").pack()
            except Exception as e:
                print(f"Image load failed for {image_path}:", e)
                tk.Label(frame, text="No Image", bg="#fff0f5").pack()

            tk.Label(frame, text=f"{product_name} - ₹{product_price}", font=("Helvetica", 10, "bold"),
                     bg="#fff0f5", fg="#ff66b3").pack()
            tk.Label(frame, text=f"In stock: {product_qty}", font=("Helvetica", 9), bg="#fff0f5").pack()

            qty_entry = tk.Entry(frame, width=5)
            qty_entry.insert(0, "1")
            qty_entry.pack(pady=5)

            tk.Button(frame, text="Add to Cart", bg="#ffb6c1", fg="white",
                      command=lambda pid=product_id, pname=product_name, price=product_price,
                                     q=qty_entry: self.add_to_cart(pid, pname, price, q)).pack()

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

        row += 1
        checkout_button = tk.Button(scroll_frame, text="Proceed to Checkout 🛒", font=("Helvetica", 14, "bold"),
                                    bg="#ff66b3", fg="white", command=self.checkout)
        checkout_button.grid(row=row, column=0, columnspan=max_columns, pady=20)

    def add_to_cart(self, product_id, product_name, product_price, qty_entry):
        try:
            quantity = int(qty_entry.get())
            if quantity > 0:
                self.cart.append((product_id, product_name, product_price, quantity))
                messagebox.showinfo("Cart", f"Added {quantity} x {product_name} to cart 💕")
            else:
                messagebox.showerror("Invalid Quantity", "Please enter a quantity greater than 0.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for quantity.")

    def checkout(self):
        self.clear_window()

        if not self.cart:
            tk.Label(self.root, text="Your cart is empty 😢", font=("Helvetica", 16),
                     bg="#ffe6f0", fg="#ff66b3").pack(pady=20)
            return

        tk.Label(self.root, text="Checkout 🛒", font=("Helvetica", 20, "bold"),
                 bg="#ffe6f0", fg="#ff66b3").pack(pady=10)

        total = 0
        for _, name, price, qty in self.cart:
            tk.Label(self.root, text=f"{name} x {qty} - ₹{price * qty}", font=("Helvetica", 14), bg="#ffe6f0").pack()
            total += price * qty

        tk.Label(self.root, text=f"Total: ₹{total}", font=("Helvetica", 16, "bold"),
                 bg="#ffe6f0", fg="#cc0066").pack(pady=10)
        tk.Button(self.root, text="Confirm Purchase", font=("Helvetica", 14),
                  bg="#ff66b3", fg="white", command=lambda: self.confirm_purchase(total)).pack(pady=10)

    def confirm_purchase(self, total):
        try:
            self.backend.record_sale(self.cart, total)
            self.show_bill(total)
        except Exception as e:
            messagebox.showerror("Error", f"Error recording sale: {e}")

    def show_bill(self, total):
        self.clear_window()
        tk.Label(self.root, text="📜 Your Receipt", font=("Helvetica", 20, "bold"),
                 bg="#ffe6f0", fg="#ff66b3").pack(pady=10)

        for product_id, name, price, qty in self.cart:
            tk.Label(self.root, text=f"{name} x {qty} = ₹{price * qty}", font=("Helvetica", 14),
                     bg="#ffe6f0").pack()

        tk.Label(self.root, text=f"Total: ₹{total}", font=("Helvetica", 16, "bold"),
                 bg="#ffe6f0", fg="#cc0066").pack(pady=10)
        tk.Label(self.root, text="Thank you for shopping with us! 💕", font=("Helvetica", 14),
                 bg="#ffe6f0", fg="#ff66b3").pack(pady=5)

        self.cart.clear()
        tk.Button(self.root, text="Back to Home", font=("Helvetica", 14), bg="#ff99cc", fg="white",
                  command=self.welcome_page).pack(pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PrettyPinkStoreApp(root)
    root.mainloop()
