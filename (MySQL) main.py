import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk
import random

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password= "Anthony120*",
    database="TheaterDB"
)

class MovieTicketingApp:
    def __init__(self, root):

        self.seats = {}

        self.selected_seats = []

        self.root = root
        self.root.title("Movie Ticketing System")

        # Create a frame for theater selection
        self.theater_selection_frame = ttk.Frame(root)
        self.theater_selection_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Add label and dropdown for theater selection
        self.theater_label = ttk.Label(self.theater_selection_frame, text="Select Theater:")
        self.theater_label.pack(side="left")

        self.theater_var = tk.StringVar()
        self.theater_dropdown = ttk.Combobox(self.theater_selection_frame, textvariable=self.theater_var)
        self.theater_dropdown.pack(side="left")
        self.populate_theater_dropdown()

        # Add button to view all April showings
        self.view_showings_button = ttk.Button(self.theater_selection_frame, text="View All April Showings", command=self.view_april_showings)
        self.view_showings_button.pack(side="right")

        # Create a frame for displaying movies
        self.movies_frame = ttk.Frame(root)
        self.movies_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Create a listbox for displaying movies
        self.movie_listbox = tk.Listbox(self.movies_frame)
        self.movie_listbox.pack(side="left", fill="both", expand=True)

        self.movie_listbox.bind('<<ListboxSelect>>', self.update_movie_details)

        # Create a frame for displaying movie details
        self.movie_details_frame = ttk.Frame(self.movies_frame)
        self.movie_details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Add label for movie details
        self.movie_details_label = ttk.Label(self.movie_details_frame, text="Movie Details:")
        self.movie_details_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        # Create treeview for displaying movie details
        self.movies_tree = ttk.Treeview(self.movie_details_frame, columns=("Genre", "Duration", "Rating"))
        self.movies_tree.heading("#0", text="Title")
        self.movies_tree.heading("Genre", text="Genre")
        self.movies_tree.heading("Duration", text="Duration")
        self.movies_tree.heading("Rating", text="Rating")
        self.movies_tree.pack(fill="both", expand=True)

        # Create a frame for movie image
        self.movie_image_frame = ttk.Frame(self.movies_frame)
        self.movie_image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create a label for movie image
        self.movie_image_label = ttk.Label(self.movie_image_frame)
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

        self.payment_label = ttk.Label(self.payment_details_frame, text="Payment Details:")
        self.payment_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        self.cash_button = ttk.Button(self.payment_details_frame, text="Cash", command=self.select_cash_payment)
        self.cash_button.pack(side="left", padx=10)

        self.credit_debit_button = ttk.Button(self.payment_details_frame, text="Credit/Debit", command=self.select_credit_debit_payment)
        self.credit_debit_button.pack(side="left", padx=10)

        # Add Receipt Details section
        self.receipt_details_frame = ttk.Frame(self.checkout_payment_frame)
        self.receipt_details_frame.pack(side="right", fill="both", expand=True)

        self.receipt_label = ttk.Label(self.receipt_details_frame, text="Receipt Details:")
        self.receipt_label.pack(side="top", padx=(20, 0), pady=(0, 10))

        self.total_charge_label = ttk.Label(self.receipt_details_frame, text="Total Ticket(s) charge: $00.00")
        self.total_charge_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.tax_label = ttk.Label(self.receipt_details_frame, text="Tax: 7.5%")
        self.tax_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.total_label = ttk.Label(self.receipt_details_frame, text="Total: $00.00")
        self.total_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        self.payment_method_label = ttk.Label(self.receipt_details_frame, text="Payment Method: None")
        self.payment_method_label.pack(anchor="w", padx=(20, 0), pady=(0, 5))

        # Create a frame for ticket information
        self.ticket_info_frame = ttk.Frame(root)
        self.ticket_info_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Add label for ticket information
        self.ticket_info_label = ttk.Label(self.ticket_info_frame, text="Ticket Information:")
        self.ticket_info_label.pack(side="left", padx=(20, 0), pady=(0, 10))

        # Create a text widget for displaying ticket information
        self.ticket_info_text = tk.Text(self.ticket_info_frame, height=5, width=50)
        self.ticket_info_text.pack(side="left", padx=(20, 0), pady=(0, 10))

        # Create a checkout button
        self.checkout_button = ttk.Button(self.ticket_info_frame, text="Checkout", command=self.book_ticket)
        self.checkout_button.pack(side="right", padx=10, pady=10)

        # Update showtimes when movie or theater selection changes
        self.theater_var.trace_add("write", self.update_movie_list)
        self.update_movie_list()

    def populate_theater_dropdown(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT Name FROM Theaters")
        theaters = cursor.fetchall()
        theater_names = [theater[0] for theater in theaters]
        self.theater_dropdown["values"] = theater_names
        if theater_names:
            self.theater_var.set(theater_names[0])

    def update_movie_list(self, *args):
        selected_theater = self.theater_var.get()
        if selected_theater:
            cursor = mydb.cursor()
            cursor.execute("SELECT Title FROM Movies")
            movies = cursor.fetchall()
            random.shuffle(movies)  # Shuffle the list of movies
            self.movie_listbox.delete(0, tk.END)
            for movie in movies:
                self.movie_listbox.insert(tk.END, movie[0])

            # Fetch seating capacity for the selected theater from the database
            cursor.execute("SELECT Seating_Capacity FROM Theaters WHERE Name = %s", (selected_theater,))
            seating_capacity = cursor.fetchone()[0]

            # Create seat grid with the updated seating capacity
            self.create_seat_grid(seating_capacity)

    def update_movie_details(self, event):
        if self.movie_listbox.curselection():
            selected_movie_index = self.movie_listbox.curselection()[0]
            selected_movie = self.movie_listbox.get(selected_movie_index)
            if selected_movie:
                cursor = mydb.cursor()
                cursor.execute("SELECT Movie_ID, Genre, Duration, Maturity_Rating FROM Movies WHERE Title = %s", (selected_movie,))
                movie_info = cursor.fetchone()
                self.movies_tree.delete(*self.movies_tree.get_children())
                self.movies_tree.insert("", "end", text=selected_movie, values=(movie_info[1], movie_info[2], movie_info[3]))

                # Display movie image
                self.display_movie_image(movie_info[0])

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
        cursor = mydb.cursor()
        cursor.execute("SELECT Theater_ID FROM Theaters WHERE Name = %s", (self.theater_var.get(),))
        theater_id = cursor.fetchone()[0]
        cursor.execute("SELECT Movie_ID FROM Movies WHERE Title = %s", (selected_movie,))
        movie_id = cursor.fetchone()[0]
        cursor.execute("SELECT Showtime_ID,Date_time FROM Showtimes WHERE Movie_ID = %s AND Theater_ID = %s",
                       (movie_id, theater_id))
        showtimes = cursor.fetchall()
        self.showtime_selected = ""
        for showtime in showtimes:
            showtime_button = tk.Button(self.showtimes_frame, text=str(showtime[1]),
                                        command=lambda st=showtime[1]: self.select_showtime(selected_movie, st))
            showtime_button.pack(side="left", padx=5)

            # Update seat grid based on reserved seats
            self.update_seat_grid(theater_id, movie_id, showtime[0])

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
        screen_frame = ttk.Frame(self.seat_grid_frame, borderwidth=2, relief="solid")
        screen_frame.grid(row=0, column=0, columnspan=num_cols + 1)
        screen_label = ttk.Label(screen_frame, text="SCREEN")
        screen_label.pack()

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

    def update_seat_grid(self, theater_id, movie_id, showtime_id):
        cursor = mydb.cursor()
        cursor.execute(
            "SELECT Seat_Number FROM Seats WHERE Theater_ID = %s AND Movie_ID = %s AND Showtime_ID = %s AND Status = 1",
            (theater_id, movie_id, showtime_id))
        reserved_seats = [seat[0] for seat in cursor.fetchall()]

        for seat_label, seat_button in self.seats.items():
            if seat_label in reserved_seats:
                seat_button.config(state=tk.DISABLED)
            else:
                seat_button.config(state=tk.NORMAL)

    def select_showtime(self, selected_movie, selected_showtime):
        cursor = mydb.cursor()
        cursor.execute("SELECT Showtime_ID FROM Showtimes WHERE Date_time = %s", (selected_showtime,))
        showtime_id = cursor.fetchone()[0]

        self.showtime_selected = selected_showtime
        self.selected_movie = selected_movie
        self.selected_showtime_id = showtime_id  # Store the selected showtime_id

        # Fetch all remaining results from the cursor
        cursor.fetchall()

        # Close the cursor
        cursor.close()

        self.update_ticket_info()
        self.update_seat_grid_for_selected_showtime()

    def update_seat_grid_for_selected_showtime(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT Theater_ID FROM Theaters WHERE Name = %s", (self.theater_var.get(),))
        theater_id = cursor.fetchone()[0]
        cursor.execute("SELECT Movie_ID FROM Movies WHERE Title = %s", (self.selected_movie,))
        movie_id = cursor.fetchone()[0]
        cursor.execute("SELECT Showtime_ID FROM Showtimes WHERE Date_time = %s AND Movie_ID = %s AND Theater_ID = %s",
                       (self.showtime_selected, movie_id, theater_id))
        showtime_id = cursor.fetchone()[0]
        self.update_seat_grid(theater_id, movie_id, showtime_id)

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

        # Debugging print statements
        print(f"Selected Movie: {selected_movie}")
        print(f"Selected Showtime (ID): {selected_showtime_id}")
        print(f"Selected Seats: {selected_seats}")

        # Ensure that a movie, showtime, and seats are selected
        if not (selected_movie and selected_showtime and selected_seats):
            messagebox.showerror("Error", "Please select a movie, showtime, and seats.")
            return

        try:
            # Start a transaction
            with mydb.cursor() as cursor:
                cursor.execute("START TRANSACTION")

                # Insert booking details into the bookings table
                for seat_label in selected_seats:
                    # Fetch Seat_ID from Seats table
                    cursor.execute("SELECT Seat_ID FROM Seats WHERE Seat_Number = %s AND Theater_ID = "
                                   "(SELECT Theater_ID FROM Theaters WHERE Name = %s)",
                                   (seat_label, self.theater_var.get()))
                    seat_id = cursor.fetchone()[0]
                    cursor.fetchall()  # Consume any remaining unread results

                    # Debugging print statements
                    print(f"Inserting booking for seat {seat_label}, Seat_ID: {seat_id}")
                    print(f"Inserting booking for Showtime_ID: {selected_showtime}")

                    cursor.execute(
                        "INSERT INTO Bookings (Booking_ID, Showtime_ID, Seat_ID, Booking_Date) VALUES (NULL, %s, %s, %s)",
                        (selected_showtime_id, seat_id, selected_showtime))

                    # Update the seats table to mark the seat as reserved
                    cursor.execute("UPDATE Seats SET Status = 1 WHERE Seat_Number = %s AND Theater_ID = "
                                   "(SELECT Theater_ID FROM Theaters WHERE Name = %s)",
                                   (seat_label, self.theater_var.get()))
                    cursor.fetchall()  # Consume any remaining unread results

                # Insert transaction details into the transactions table
                total_charge = len(selected_seats) * 10  # Assuming $10 per ticket
                cursor.execute("INSERT INTO Transactions (Amount, Payment_Method) VALUES (%s, %s)",
                               (total_charge, self.payment_method_label.cget("text")))

                # Commit the transaction
                mydb.commit()
                messagebox.showinfo("Success", "Tickets booked successfully!")
        except Exception as e:
            # Rollback the transaction if an error occurs
            mydb.rollback()
            messagebox.showerror("Error", f"Failed to book tickets: {str(e)}")

    def view_april_showings(self):
        # Create the view
        cursor = mydb.cursor()
        cursor.execute(
            "CREATE VIEW Movie_Times AS SELECT Title, Date_Time FROM Movies JOIN Showtimes ON Movies.Movie_ID = Showtimes.Movie_ID WHERE Date_Time LIKE '2024-04%'")

        # Fetch the data from the view
        cursor.execute("SELECT * FROM Movie_Times")
        showings = cursor.fetchall()

        # Display the data in a messagebox
        showings_str = "\n".join([f"{showing[0]} - {showing[1]}" for showing in showings])
        messagebox.showinfo("View All April Showings", showings_str)

        # Drop the view after the messagebox is closed
        cursor.execute("DROP VIEW IF EXISTS Movie_Times")


def main():
    # Create the Tkinter application
    root = tk.Tk()
    app = MovieTicketingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()