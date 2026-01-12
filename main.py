import extract_data
import topsis
import rsm
import UTA
import Sp_Cs
import AHP
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from itertools import cycle


# window size
global_window_width = 1500
global_window_height = 900


def try_conv(vector):
    try:
        [float(el) for el in vector]
        return True
    except ValueError:
        return False

def open_UTA_star_window(r, minimum, benefit_attributes_):

    def fun_method():
        ranking_area.delete('1.0', tk.END)  # Clear the ranking area
        lower_limits_ = []
        upper_limits_ = []
        weight_vector_ = []
        compartments_ = []

        for i in range(len(criteria_entries)):
            if i % 4 == 0:
                lower_limits_.append(float(criteria_entries[i].get()))
            elif i % 4 - 1 == 0:
                upper_limits_.append(float(criteria_entries[i].get()))
            elif i % 4 - 2 == 0:
                weight_vector_.append(float(criteria_entries[i].get()))
            elif i % 4 - 3 == 0:
                compartments_.append(float(criteria_entries[i].get()))

        if try_conv(lower_limits_) and try_conv(upper_limits_) and try_conv(weight_vector_) and try_conv(compartments_):
            lower_limits_ = list(map(float, lower_limits_))
            upper_limits_ = list(map(float, upper_limits_))
            weight_vector_ = list(map(float, weight_vector_))
            compartments_ = list(map(int, compartments_))
            sum_weight_vector = sum(weight_vector_)
            weight_vector_normalized = [el / sum_weight_vector for el in weight_vector_]

            result_ = UTA.UTA_star(r[3], lower_limits_, upper_limits_, weight_vector_normalized,
                                   benefit_attributes_, compartments_)
            if result_ == None:
                ranking_area.insert(tk.END, "Niestety twoje kryteria są zbyt wąskie.")
            if result_ == 1:
                ranking_area.insert(tk.END, "Liczba przedziałów musi być dodatnia!")
            else:
                text = ""
                for i in range(len(result_)):
                    text += f"{i + 1}. {r[1][result_[i]][1]}, {r[1][result_[i]][2]}\n"
                ranking_area.insert(tk.END, text)
        else:
            messagebox.showwarning("Warning", "Wrong value entered!")


    def end_fullscreen(event=None):
        root.attributes('-fullscreen', False)
        return "break"


    new_window = tk.Toplevel(root)
    new_window.title("UTA Star")
    new_window.geometry("%dx%d" % (global_window_width, global_window_height))
    new_window.state("zoomed")
    new_window.bind("<Escape>", end_fullscreen)

    # Criteria frame without scrolling
    criteria_frame = tk.LabelFrame(new_window, text="Kryteria brane pod uwagę", padx=5, pady=5)
    criteria_frame.grid(row=0, column=0, sticky="news", padx=10, pady=5)

    # Define the criteria here
    criteria_labels = r[2][1:]  # Add more criteria as needed
    criteria_entries = []

    # Add labels for Min, Max, Weight above the columns
    tk.Label(criteria_frame, text="Kryterium").grid(row=0, column=0, sticky="w", padx=5)
    for j, label in enumerate(["Min", "Max", "Weight[%]", "Liczba przedziałów"]):
        tk.Label(criteria_frame, text=label).grid(row=0, column=j + 1, sticky="w", padx=5)

    # Dynamically create the criteria entries
    for i, label in enumerate(criteria_labels):
        tk.Label(criteria_frame, text=label).grid(row=i + 1, column=0, sticky="w", padx=5)
        for j in range(4):  # For Min, Max, Weight
            entry = tk.Entry(criteria_frame, width=8)
            entry.grid(row=i + 1, column=j + 1, padx=5, pady=2)
            # Set default value
            if j % 4 == 0:
                entry.insert(tk.END, str(minimum[i]))
            elif j % 4 - 1 == 0:
                entry.insert(tk.END, str(maximum[i]))
            elif j % 4 - 2 == 0:
                entry.insert(tk.END, str(1 / len(minimum) * 100))
            elif j % 4 - 3 == 0:
                entry.insert(tk.END, str(1))
            criteria_entries.append(entry)
    # Ranking frame with scrolling text
    ranking_frame = tk.LabelFrame(new_window, text="Ranking", padx=5, pady=5)
    ranking_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=5)
    ranking_area = tk.Text(ranking_frame, wrap=tk.WORD)
    ranking_area.grid(row=0, column=0, sticky="nsew")

    scrollbar_ranking = tk.Scrollbar(ranking_frame, orient="vertical", command=ranking_area.yview)
    ranking_area['yscrollcommand'] = scrollbar_ranking.set
    scrollbar_ranking.grid(row=0, column=1, sticky='nsew')

    button_frame = tk.Frame(new_window)
    button_frame.grid(row=1, column=0, padx=5, pady=5)

    generate_button = tk.Button(button_frame, text="Generuj Ranking", command=fun_method)
    generate_button.grid(row=0, column=0, pady=5)

    return_button = tk.Button(button_frame, text="Powrót do okna głównego", command=new_window.destroy)
    return_button.grid(row=0, column=1, pady=5)

    new_window.grid_columnconfigure(1, weight=1)
    new_window.grid_rowconfigure(0, weight=1)

    ranking_frame.grid_columnconfigure(0, weight=1)
    ranking_frame.grid_rowconfigure(0, weight=1)

if __name__ == "__main__":
    # Function to exit fullscreen mode
    def end_fullscreen(event=None):
        root.attributes('-fullscreen', False)
        return "break"

    # Function to change cursor appearance to 'hand2' (clicking pointer)
    def change_cursor(event):
        event.widget.config(cursor="hand2")

    # Extract data from a database (assuming this function exists)
    r = extract_data.get_data_from_database()

    # List representing benefit attributes
    benefit_attributes_ = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    # Transpose a list of data and find minimum and maximum values
    transposed_list = list(zip(*r[3]))[1:]
    minimum = [min(column) for column in transposed_list]
    maximum = [max(column) for column in transposed_list]
    print(maximum)

    # Create the main Tkinter window
    root = tk.Tk()
    # Set the size of the tkinter window
    root.geometry("%dx%d" % (global_window_width, global_window_height))
    root.state("zoomed")
    root.title("Decision Support Systems")

    # Load a background image
    my_size = 250
    width_background_image = 5*my_size
    height_background_image = 3*my_size
    background_image = Image.open("start_page_photo.png")
    background_image = background_image.resize((width_background_image, height_background_image))
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create a label for the main title
    tk.Label(root, text="Gdzie świat poniesie Cię dziś?", font=("Helvetica", 40)).pack()

    # Define methods as a dictionary with method names as keys and associated functions as values
    methods = {
        "Topsis": lambda: open_topsis_window(r, minimum, benefit_attributes_),
        "RSM": lambda: open_RSM_window(r, minimum, benefit_attributes_),
        "UTA Star": lambda: open_UTA_star_window(r, minimum, benefit_attributes_),
        "SP_CS": lambda: open_SPCS_window(r, minimum, benefit_attributes_),
        "AHP": lambda: open_AHP_window(r, minimum, benefit_attributes_)
    }

    # Create a label as a reminder for method selection
    label_reminder = tk.Label(root, text="Powyżej wybierz odpowiednią metodę.", font=("Helvetica", 12))
    label_reminder.pack(side=tk.BOTTOM, pady=10)

    # Create a frame for buttons
    button_frame = tk.Frame(root, background='white')
    button_frame.pack(side=tk.BOTTOM, pady=20)

    # List of rainbow colors
    rainbow_colors = ["gray", "gray", "blue", "gray", "gray", "gray"]
    color_cycle = cycle(rainbow_colors)

    # Function to handle mouse entering a button
    def on_enter(event):
        next_color = next(color_cycle)
        event.widget.config(bg=next_color, fg='white', width=21, height=2)
        change_cursor(event)

    # Function to handle mouse leaving a button
    def on_leave(event):
        event.widget.config(bg='black', fg='white', width=20, height=2)
        event.widget.config(cursor="")

    # Create buttons for each method and bind mouse events
    for method, action in methods.items():
        button = tk.Button(button_frame, text=method, command=action, height=2, width=20, bg='black', fg='white', font=("Helvetica",12,'bold'))
        button.pack(side=tk.LEFT, padx=30, pady=0)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    # Start the Tkinter main loop
    root.mainloop()