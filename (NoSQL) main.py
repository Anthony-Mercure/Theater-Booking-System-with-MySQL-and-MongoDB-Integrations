import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.ttk import *
import json
from pymongo import MongoClient
import random
from PIL import Image, ImageTk

# Making Connection
myclient = MongoClient("mongodb://localhost:27017/")

# Drop the existing database if it exists
myclient.drop_database("NoSQL_TheaterDB")

# Database
db = myclient["NoSQL_TheaterDB"]

# Load and insert data into collections
collections = {
    "Bookings": "Booking.json",
    "Movies": "Movies.json",
    "Seats": "Seats.json",
    "Showtimes": "Showtimes.json",
    "Theaters": "Theaters.json"
}

for collection_name, file_name in collections.items():
    # Created or Switched to collection
    collection = db[collection_name]

    # Loading the json file
    with open(f'NoSQL Data/{file_name}') as file:
        file_data = json.load(file)

    # Inserting the loaded data in the Collection
    # if JSON contains data more than one entry
    # insert_many is used else insert_one is used
    if isinstance(file_data, list):
        collection.insert_many(file_data)
    else:
        collection.insert_one(file_data)

class MovieTicketingApp:
    def __init__(self, root):
        # Initialize MongoDB connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["NoSQL_TheaterDB"]
        self.custom_font = font.Font(family="Verdana", size=12)
        self.seats = {}

        self.selected_seats = []

        self.root = root
        self.root.title("Movie Ticketing System")

        # Create a frame for theater selection
        self.theater_selection_frame = ttk.Frame(root)
        self.theater_selection_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Add label and dropdown for theater selection
        self.theater_label = ttk.Label(self.theater_selection_frame, text="Select Theater:", font=self.custom_font)
        self.theater_label.pack(side="left")

        self.theater_var = tk.StringVar()
        self.theater_dropdown = ttk.Combobox(self.theater_selection_frame, textvariable=self.theater_var, font=self.custom_font)
        self.theater_dropdown.pack(side="left")
        self.populate_theater_dropdown()

        # Create a frame for displaying movies
        self.movies_frame = ttk.Frame(root)
        self.movies_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Create a frame for displaying the movie list
        self.movie_list_frame = ttk.Frame(self.movies_frame)
        self.movie_list_frame.pack(side="left", fill="x", anchor='nw', expand=True, padx=10, pady=10)

        # Add label for movie list
        self.movie_list_label = ttk.Label(self.movie_list_frame, text="Movies:", font=self.custom_font)
        self.movie_list_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        # Create a listbox for displaying movies
        self.movie_listbox = tk.Listbox(self.movie_list_frame, font=self.custom_font)
        self.movie_listbox.pack(side="left", fill="x", anchor='nw', expand=True)

        self.movie_listbox.bind('<<ListboxSelect>>', self.update_movie_details)

        # Create a frame for displaying movie details
        self.movie_details_frame = ttk.Frame(self.movies_frame)
        self.movie_details_frame.pack(side="left", fill="x", anchor='nw', expand=True, padx=10, pady=10)

        # Add label for movie details
        self.movie_details_label = ttk.Label(self.movie_details_frame, text="Movie Details:", font=self.custom_font)
        self.movie_details_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        # Create treeview for displaying movie details
        self.movies_tree = ttk.Treeview(self.movie_details_frame, columns=("Genre", "Duration", "Rating"))
        self.movies_tree.heading("#0", text="Title")
        self.movies_tree.heading("Genre", text="Genre")
        self.movies_tree.heading("Duration", text="Duration")
        self.movies_tree.heading("Rating", text="Rating")

        # Set column widths and anchor points
        self.movies_tree.column('#0', width=150, anchor='center')  # Decreased width
        self.movies_tree.column('Genre', width=125, anchor='center')
        self.movies_tree.column('Duration', width=75, anchor='center')
        self.movies_tree.column('Rating', width=75, anchor='center')

        self.movies_tree.pack(fill="both", expand=True)

        # Create a frame for movie image
        self.movie_image_frame = ttk.Frame(self.movies_frame)
        self.movie_image_frame.pack(side="right",fill="x", anchor='nw', expand=True, padx=10, pady=10)

        # Create a label for movie image
        self.movie_image_label = ttk.Label(self.movie_image_frame, font=self.custom_font)
        self.movie_image_label.pack(side="top", fill="both", expand=True)

        # Create a frame for showtimes
        self.showtimes_frame = ttk.Frame(self.movie_details_frame)
        self.showtimes_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.showtime_buttons = {}
        self.showtime_selected = ""

        # Create a frame for checkout and payment sections
        self.checkout_payment_frame = ttk.Frame(root)
        self.checkout_payment_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Add Payment Details section
        self.payment_details_frame = ttk.Frame(self.checkout_payment_frame)
        self.payment_details_frame.pack(side="left", fill="both", expand=True)

        self.payment_label = ttk.Label(self.payment_details_frame, text="Payment Details:", font=self.custom_font)
        self.payment_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        style = ttk.Style()
        style.configure('Cash.TButton', padding=(10, 40, 10, 40), background="green", bordercolor="green",
                        foreground="green")
        style = ttk.Style()
        style.configure('CC.TButton', padding=(10, 40, 10, 40), background="orange", bordercolor="orange",
                        foreground="orange")

        self.cash_button = ttk.Button(self.payment_details_frame, text="Cash", command=self.select_cash_payment, style='Cash.TButton')
        self.cash_button.pack(side="left", padx=10)

        self.credit_debit_button = ttk.Button(self.payment_details_frame, text="Credit/Debit", command=self.select_credit_debit_payment, style='CC.TButton')
        self.credit_debit_button.pack(side="left", padx=10)

        # Add Receipt Details section
        self.receipt_details_frame = ttk.Frame(self.checkout_payment_frame)
        self.receipt_details_frame.pack(side="right", fill="both", expand=True)

        self.receipt_label = ttk.Label(self.receipt_details_frame, text="Receipt Details:", font=self.custom_font)
        self.receipt_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        self.total_charge_label = ttk.Label(self.receipt_details_frame, text="Total Ticket(s) charge: $00.00", font=self.custom_font)
        self.total_charge_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.tax_label = ttk.Label(self.receipt_details_frame, text="Tax: 7.5%", font=self.custom_font)
        self.tax_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.total_label = ttk.Label(self.receipt_details_frame, text="Total: $00.00", font=self.custom_font)
        self.total_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.payment_method_label = ttk.Label(self.receipt_details_frame, text="Payment Method: None", font=self.custom_font)
        self.payment_method_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        # Create a frame for ticket information
        self.ticket_info_frame = ttk.Frame(root)
        self.ticket_info_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Add label for ticket information
        self.ticket_info_label = ttk.Label(self.ticket_info_frame, text="Ticket Information:", font=self.custom_font)
        self.ticket_info_label.pack(side="left", padx=(20, 0), pady=(0, 10))

        # Create a text widget for displaying ticket information
        self.ticket_info_text = tk.Text(self.ticket_info_frame, height=5, width=50, font=self.custom_font)
        self.ticket_info_text.pack(side="left", padx=(20, 0), pady=(0, 10))

        # Create a checkout button
        style = ttk.Style()
        style.configure('Checkout.TButton', padding=(10, 80, 10, 80), background = "blue", bordercolor = "blue", foreground = "blue")  # Adjust the padding for better fitting

        # Create the button
        checkout_button = ttk.Button(root, text="Checkout", width=20, command=lambda: print("Button clicked"),
                                     style='Checkout.TButton')

        # Pack the button
        checkout_button.pack(side="right", padx=10, pady=10)

        # Update showtimes when movie or theater selection changes
        self.theater_var.trace_add("write", self.update_movie_list)
        self.update_movie_list()


    def populate_theater_dropdown(self):
        theaters_collection = self.db["Theaters"]
        theater_names = theaters_collection.distinct("name")
        self.theater_dropdown["values"] = theater_names
        if theater_names:
            self.theater_var.set(theater_names[0])

    def update_movie_list(self, *args):
        selected_theater = self.theater_var.get()
        if selected_theater:
            theaters_collection = self.db["Theaters"]
            theater = theaters_collection.find_one({"name": selected_theater})
            if theater:
                # Fetch seating capacity for the selected theater from the database
                seating_capacity = theater.get("seating_capacity", 0)
                # Create seat grid with the updated seating capacity
                self.create_seat_grid(seating_capacity)

                movies_collection = self.db["Movies"]
                movies = movies_collection.distinct("title")
                random.shuffle(movies)  # Shuffle the list of movies
                self.movie_listbox.delete(0, tk.END)
                for movie in movies:
                    self.movie_listbox.insert(tk.END, movie)

    def update_movie_details(self, event):
        if self.movie_listbox.curselection():
            selected_movie_index = self.movie_listbox.curselection()[0]
            selected_movie = self.movie_listbox.get(selected_movie_index)
            if selected_movie:
                movie = self.db["Movies"].find_one({"title": selected_movie})
                self.movies_tree.delete(*self.movies_tree.get_children())
                self.movies_tree.insert("", "end", text=selected_movie, values=(movie["genre"], movie["duration"], movie["maturity_rating"]))

                # Display movie image
                self.display_movie_image(movie["movie_id"])

                self.showtimes_frame.destroy()
                self.showtimes_frame = ttk.Frame(self.movie_details_frame)
                self.showtimes_frame.pack(side="bottom", fill="x", padx=10, pady=10)
                self.populate_showtimes(selected_movie)

    def display_movie_image(self, movie_id):
        # Load the image file
        image_path = f"image{movie_id}.png"
        movie_image = Image.open(image_path)

        # Resize the image to fit the label
        image_width, image_height = movie_image.size
        max_width = 200
        max_height = 300
        if image_width > max_width or image_height > max_height:
            ratio = min(max_width / image_width, max_height / image_height)
            new_width = int(image_width * ratio)
            new_height = int(image_height * ratio)
            movie_image = movie_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert the image to Tkinter PhotoImage
        self.movie_image_tk = ImageTk.PhotoImage(movie_image)

        # Update the label with the new image
        self.movie_image_label.config(image=self.movie_image_tk)
        self.movie_image_label.image = self.movie_image_tk  # Keep a reference to avoid garbage collection

    def populate_showtimes(self, selected_movie):
        theaters_collection = self.db["Theaters"]
        theater = theaters_collection.find_one({"name": self.theater_var.get()})
        theater_id = theater["theater_id"]
        movies_collection = self.db["Movies"]
        movie = movies_collection.find_one({"title": selected_movie})
        movie_id = movie["movie_id"]
        showtimes_collection = self.db["Showtimes"]
        showtimes = showtimes_collection.find({"movie_id": movie_id, "theater_id": theater_id})
        self.showtime_selected = ""
        for showtime in showtimes:
            showtime_button = tk.Button(self.showtimes_frame, text=str(showtime["date_time"]),
                                        command=lambda st=showtime["date_time"]: self.select_showtime(selected_movie, st))
            showtime_button.pack(side="left", padx=5)

            # Update seat grid based on reserved seats
            self.update_seat_grid(theater_id, movie_id, showtime["showtime_id"], selected_movie)

    def create_seat_grid(self, seating_capacity):
        # Calculate grid dimensions
        rows = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        num_rows = min(len(rows), (seating_capacity + 9) // 10)
        num_cols = min(10, (seating_capacity + num_rows - 1) // num_rows)
        # initializes the seat list
        self.seats = {}

        # Destroy existing seat grid frame if it exists
        if hasattr(self, 'seat_grid_frame'):
            self.seat_grid_frame.destroy()

        # Create frame for seat grid
        self.seat_grid_frame = ttk.Frame(self.root)
        self.seat_grid_frame.pack(side="top", padx=10, pady=10)

        # 'SCREEN' label
        s = ttk.Style()
        s.configure('Frame1.TFrame', background='red')
        screen_frame = ttk.Frame(self.seat_grid_frame, borderwidth=2, relief="solid", style = 'Frame1.TFrame')
        screen_frame.grid(row=0, column=0, columnspan=num_cols + 1, sticky="NSEW")
        screen_frame.rowconfigure(0, weight=2)
        screen_frame.columnconfigure(0, weight=2)
        screen_label = ttk.Label(screen_frame, text="SCREEN")
        screen_label.grid(row=0, column=0)


        # Add labels for seat numbers
        for j in range(num_cols):
            seat_label = ttk.Label(self.seat_grid_frame, text=str(j + 1))
            seat_label.grid(row=1, column=j + 1, pady=(0, 5))

        # Add labels for rows
        for i in range(num_rows):
            row_label = ttk.Label(self.seat_grid_frame, text=rows[i])
            row_label.grid(row=i + 2, column=0, padx=(0, 5))

        # Create buttons for seats
        seat_number = 1
        for i in range(num_rows):
            for j in range(num_cols):
                if seat_number <= seating_capacity:
                    seat_label = rows[i] + str(j + 1)
                    seat_button = tk.Button(self.seat_grid_frame, text=seat_label, width=5, fg="black",
                                             command=lambda seat=seat_label: self.select_seat(seat))
                    seat_button.grid(row=i + 2, column=j + 1, padx=5, pady=5)
                    self.seats[seat_label] = seat_button
                    seat_number += 1

    def update_seat_grid(self, theater_id, movie_id, showtime_id, selected_movie):
        theaters_collection = self.db["Theaters"]
        theater = theaters_collection.find_one({"name": self.theater_var.get()})
        theater_id = theater["theater_id"]
        movies_collection = self.db["Movies"]
        movie = movies_collection.find_one({"title": selected_movie})  # Use selected_movie here
        movie_id = movie["movie_id"]
        showtimes_collection = self.db["Showtimes"]
        showtimes = showtimes_collection.find({"movie_id": movie_id, "theater_id": theater_id})
        seats_collection = self.db["Seats"]
        reserved_seats_cursor = seats_collection.find(
            {"theater_id": theater_id, "movie_id": movie_id, "showtime_id": showtime_id, "status": 1}
        )
        reserved_seats = [seat["seat_number"] for seat in reserved_seats_cursor]

        for seat_label, seat_button in self.seats.items():
            if seat_label in reserved_seats:
                seat_button.config(state=tk.DISABLED)
            else:
                seat_button.config(state=tk.NORMAL)

    def select_showtime(self, selected_movie, selected_showtime):
        showtimes_collection = self.db["Showtimes"]

        # Find the showtime document based on the selected datetime
        showtime = showtimes_collection.find_one({"date_time": selected_showtime})

        if showtime:
            showtime_id = showtime["showtime_id"]

            self.showtime_selected = selected_showtime
            self.selected_movie = selected_movie
            self.selected_showtime_id = showtime_id

            self.update_ticket_info()
            self.update_seat_grid_for_selected_showtime()

    def update_seat_grid_for_selected_showtime(self):
        theaters_collection = self.db["Theaters"]
        movies_collection = self.db["Movies"]
        showtimes_collection = self.db["Showtimes"]

        theater = theaters_collection.find_one({"name": self.theater_var.get()})
        movie = movies_collection.find_one({"title": self.selected_movie})

        if theater and movie:
            theater_id = theater["theater_id"]
            movie_id = movie["movie_id"]

            # Find the showtime document based on date, movie, and theater
            showtime = showtimes_collection.find_one({
                "date_time": self.showtime_selected,
                "movie_id": movie_id,
                "theater_id": theater_id
            })

            if showtime:
                showtime_id = showtime["showtime_id"]
                self.update_seat_grid(theater_id, movie_id, showtime_id, self.selected_movie)

    def select_seat(self, seat_label):
        if seat_label in self.selected_seats:
            self.selected_seats.remove(seat_label)
            self.seats[seat_label].config(bg="SystemButtonFace", fg="red")
        else:
            self.selected_seats.append(seat_label)
            self.seats[seat_label].config(fg="green")
        self.update_ticket_info()

    def update_ticket_info(self):
        ticket_info = f"Movie: {self.selected_movie}\n"
        ticket_info += f"Showtime: {self.showtime_selected}\n"
        ticket_info += "Selected Seats:\n"
        for seat_label in self.selected_seats:
            ticket_info += f"{seat_label}, "
        self.ticket_info_text.delete(1.0, tk.END)
        self.ticket_info_text.insert(tk.END, ticket_info)

        # Update receipt details
        total_charge = len(self.selected_seats) * 10  # $10 per ticket
        tax = total_charge * 0.075  # 7.5% tax
        total = total_charge + tax

        self.total_charge_label.config(text=f"Total Ticket(s) charge: ${total_charge:.2f}")
        self.tax_label.config(text=f"Tax: ${tax:.2f}")
        self.total_label.config(text=f"Total: ${total:.2f}")

    def select_cash_payment(self):
        self.payment_method_label.config(text="Payment Method: Cash")

    def select_credit_debit_payment(self):
        self.payment_method_label.config(text="Payment Method: Credit/Debit")

    def book_ticket(self):
        selected_movie = self.selected_movie
        selected_showtime_id = self.selected_showtime_id
        selected_showtime = self.showtime_selected
        selected_seats = self.selected_seats

        # Ensure that a movie, showtime, and seats are selected
        if not (selected_movie and selected_showtime and selected_seats):
            messagebox.showerror("Error", "Please select a movie, showtime, and seats.")
            return

        try:
            theaters_collection = self.db["Theaters"]
            selected_theater = theaters_collection.find_one({"name": self.theater_var.get()})
            theater_id = selected_theater["theater_id"]

            # Start a session
            with self.client.start_session() as session:
                # Start a transaction
                with session.start_transaction():
                    bookings_collection = self.db["Bookings"]
                    seats_collection = self.db["Seats"]

                    for seat_label in selected_seats:
                        # Fetch Seat_ID from Seats collection
                        seat = seats_collection.find_one({"seat_number": seat_label, "theater_id": theater_id})
                        seat_id = seat["seat_id"]

                        # Insert booking details into the Bookings collection
                        booking_data = {
                            "showtime_id": selected_showtime_id,
                            "seat_id": seat_id,
                            "booking_date": selected_showtime
                        }
                        bookings_collection.insert_one(booking_data)

                        # Update the Seats collection to mark the seat as reserved
                        seats_collection.update_one(
                            {"_id": seat["_id"]},
                            {"$set": {"status": 1}}
                        )

                    # Insert transaction details into the Transactions collection
                    total_charge = len(selected_seats) * 10  # Assuming $10 per ticket
                    tax = total_charge * 0.075  # 7.5% tax
                    total_amount = total_charge + tax
                    transaction_data = {
                        "booking_id": booking_data["_id"],
                        "amount": total_amount,
                        "payment_method": self.payment_method_label.cget("text"),
                        "transaction_date": selected_showtime
                    }
                    transactions_collection = self.db["Transactions"]
                    transactions_collection.insert_one(transaction_data)

            messagebox.showinfo("Success", "Tickets booked successfully!")
            self.clear_booking_details()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to book tickets: {str(e)}")

    def clear_booking_details(self):
        self.showtime_selected = ""
        self.selected_movie = ""
        self.selected_showtime_id = ""
        self.selected_seats = []

        self.ticket_info_text.delete(1.0, tk.END)

        self.total_charge_label.config(text="Total Ticket(s) charge: $00.00")
        self.tax_label.config(text="Tax: 7.5%")
        self.total_label.config(text="Total: $00.00")
        self.payment_method_label.config(text="Payment Method: None")

        self.update_seat_grid_for_selected_showtime()

def main():
    # Create the Tkinter application
    root = tk.Tk()
    app = MovieTicketingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()