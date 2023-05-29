import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import time
import re


class ChargingStation:
    def __init__(self, station_name, charging_rate):
        self.station_name = station_name
        self.charging_rate = charging_rate
        self.available_slots = 4  # Number of available charging slots
        self.occupied_slots = 0  # Number of currently occupied charging slots
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Suraj@123",
            database="pythondb1"
        )

    def charge_vehicle(self, vehicle_no):
        if self.available_slots > 0:
            # self.available_slots -= 1
            # self.occupied_slots += 1
            messagebox.showinfo("Charging Started", f"Charging started for Vehicle No. {vehicle_no}. Please park your vehicle.")
            self.carpic()
            self.available_slots -= 1
            self.occupied_slots += 1
            self.start_time = time.time()  # Record the start time
        else:
            messagebox.showinfo("No Available Slots", "Sorry, all charging slots are occupied. Please wait.")

    def carpic(self):

        self.car_img=Image.open(r"D:\Test\Work\pROJECT\EV Station Management\carmain.png")
        # car_img=car_img.rotate(90)
        self.car_img=self.car_img.resize((250,150), Image.LANCZOS)
        self.car_photo=ImageTk.PhotoImage(self.car_img)

        self.car_label=tk.Label(root,image=self.car_photo)
        self.car_label.image=self.car_photo
        
        # car_label.place(x=40,y=800)
        if self.available_slots==4: 
            self.car_label.place(x=120,y=600)
        elif self.available_slots==3:
            self.car_label.place(x=500,y=600)
        elif self.available_slots==2:
            self.car_label.place(x=660,y=600)
        elif self.available_slots==1:
            self.car_label.place(x=1000,y=600)

    def car_remove(self,vehicle_no):
        if vehicle_no:
            self.car_label.place_forget()

    def stop_charging(self, vehicle_no):
        # if self.occupied_slots > 0:
        self.available_slots += 1
        self.occupied_slots -= 1 
        messagebox.showinfo("Charging Stopped", f"Charging stopped for Vehicle No. {vehicle_no}. Please pay.")
        self.car_remove(vehicle_no)
        # else:
            # messagebox.showinfo("No Occupied Slots", "There are no occupied charging slots.")

        # Calculate the charging duration
        duration_seconds = round(time.time() - self.start_time)
        duration_minutes = duration_seconds // 60
        duration_seconds %= 60

        # Insert the charging details into the database
        cursor = self.db_connection.cursor()
        query = "INSERT INTO charging_history (vehicle_no, station_name, charging_rate, duration_minutes, duration_seconds) VALUES ( %s, %s, %s, %s, %s)"
        values = (vehicle_no, self.station_name, self.charging_rate, duration_minutes, duration_seconds)
        cursor.execute(query, values)
        self.db_connection.commit()

    def generate_bill(self, vehicle_no):
        # Fetch the charging details from the database
        cursor = self.db_connection.cursor()
        query = "SELECT Id, vehicle_no, station_name, charging_rate, duration_minutes, duration_seconds\
              FROM charging_history WHERE vehicle_no = %s ORDER BY Id DESC LIMIT 1"

        cursor.execute(query, (vehicle_no,))
        record = cursor.fetchone()
        # print(record)

        if record:
            Id, vehicle_no, station_name, charging_rate, duration_minutes, duration_seconds = record
          
            # Calculate the charging cost based on charging rate and duration
            charging_duration = f"{duration_minutes} minutes {duration_seconds} seconds"
            if duration_minutes<=0:
                charging_cost=150
            else:
                charging_cost = self.charging_rate * duration_minutes
            
        

            # Generate the bill message
            bill_message = f"Vehicle No.: {vehicle_no}\n\n"
            bill_message += f"Charging Station: {station_name}\n"
            bill_message += f"Charging Rate: {self.charging_rate} kW\n"
            bill_message += f"Charging Duration: {charging_duration}\n"
            bill_message += f"Charging Cost: Rs.{charging_cost}\n"

            messagebox.showinfo("Bill Generation", bill_message)
        else:
            messagebox.showinfo("No Billing Information", f"No charging history found for Vehicle No. {vehicle_no}.")

        cursor = self.db_connection.cursor()
        query = "UPDATE charging_history SET Amount=%s WHERE Id = %s"
        cursor.execute(query, (charging_cost,Id))
        self.db_connection.commit()




l=[]

def start_charging():
    vehicle_no = vehicle_entry.get()
    n=len(vehicle_no)
    valid_no=re.findall('[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}$',vehicle_no)
    if n<=10 and n>=9 and valid_no:
        if vehicle_no not in l:
            l.append(vehicle_no)
            # print(l)2
            station.charge_vehicle(vehicle_no)
            # carpic()
            update_slots_label()
        else:
            messagebox.showerror("Error",f"Oops...! Already allocated a Slot for {vehicle_no}.")
    else:
        messagebox.showerror("Error",f"Invalid Vehicle No.")
def ok():
    payroot.destroy()
    messagebox.showinfo("Payment","Payment Done Successfully..!     Thank you for using our charging station")

def stop_charging():
    global payroot
    vehicle_no = vehicle_entry.get()
    if vehicle_no in l:
        # print(l)
        l.remove(vehicle_no)
        # print(l)
        station.stop_charging(vehicle_no)
        station.generate_bill(vehicle_no)
        update_slots_label()

        payroot=tk.Tk()
        payroot.title("Payment")
        payroot.geometry("400x300")
        payroot.config(bg="light blue")

        G_Button=tk.Checkbutton(payroot,text="Gpay/Phonepe",bg="Light yellow",width=15,font=("bold"))
        G_Button.place(x=10,y=50)

        Card_Button=tk.Checkbutton(payroot,text="Card",bg="Light yellow",width=15,font="bold")
        Card_Button.place(x=10,y=100)

        Cash_Button=tk.Checkbutton(payroot,text="Cash",bg="Light yellow",width=15,font="bold")
        Cash_Button.place(x=10,y=150)

        # mode=["Gpay","Phonepe","Credit Card","Debit Card","Cash"]
        # drop=tk.OptionMenu(payroot,self.*mode)


        ok_button=tk.Button(payroot,text="Pay Now",command=ok,bg="Green",fg="Yellow",font=("Arial",20,"italic bold"),width=15)
        ok_button.place(x=5,y=200)
        payroot.mainloop()
        


        
    else:
        messagebox.showerror("Error",f"There is no Such Vehicle with {vehicle_no}")


def update_slots_label():
    slots_label["text"] = f"Available Slots: {station.available_slots}"


# Creating an instance of ChargingStation
station = ChargingStation("Station A", 10)

# Creating the GUI
root = tk.Tk()
root.title("Charging Station")
root.geometry("1950x1080")

# Load and resize the background image
bg_image = Image.open(r"D:\Test\Work\pROJECT\EV Station Management\background_image.png")
bg_image = bg_image.resize((1950, 1080), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a label with the background image
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
 

title_label = tk.Label(root, text="Charging Station", font=("Helvetica", 80,'italic bold'), bg="#2B2B2B",fg="Grey")
title_label.pack(pady=10)

slots_label = tk.Label(root, text=f"Available Slots: {station.available_slots}", font=("Arial", 30,"bold"), bg="Grey",fg="Brown")
slots_label.pack(ipady=30)

vehicle_label = tk.Label(root, text="Vehicle No:", font=("Arial", 15), bg="#45458B")
vehicle_label.place(x=600,y=300)

vehicle_entry = tk.Entry(root, font=("Arial", 15,"bold"))
vehicle_entry.place(x=730,y=300)

charge_button = tk.Button(root, text="Start Charging", command=start_charging,background="Green",font=(25))
charge_button.place(x=620,y=400)

stop_button = tk.Button(root, text="Stop Charging", command=stop_charging,background="Red",font=(25))
stop_button.place(x=820,y=400)

root.mainloop()
