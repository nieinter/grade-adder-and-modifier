import datetime
import ttkbootstrap as ttk
import pymongo
from tkinter import messagebox

from bson.objectid import ObjectId


class App(ttk.Window):
    def __init__(self) -> None:
        super().__init__(themename="superhero")
        self.geometry("700x900")
        self.resizable(False, False)
        self.frame_add = FrameAdd()
        self.frame_change = FrameModify()
        self.title("Dodawanie ocen")
        self.f_a = True

        self.frame_add.pack(side="left", expand=True)

        ttk.Button(self,
                   text="⮂",
                   command=self.change_frames).pack(side="right", anchor="se", fill="y")

    def change_frames(self) -> None:
        self.frame_change.treeview_fill()
        if self.f_a:
            self.f_a = False
            self.frame_add.pack_forget()
            self.frame_change.pack(side="left", expand=True)
            self.title("Modyfikacja ocen")
        else:
            self.f_a = True
            self.frame_change.pack_forget()
            self.frame_add.pack(side="left", expand=True)
            self.title("Dodawanie ocen")


class FrameModify(ttk.Frame):
    def __init__(self) -> None:
        super().__init__()
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myclient["grades_db"]
        self.mycol = self.mydb["lesson_journal"]
        mycol_id = self.mydb["login_data"]
        self.selected_item = None

        ids = []
        for i in mycol_id.find():
            ids.append(str(i["_id"]))

        ttk.Style().configure("L.TLabel", font=("Century Gothic", 20))
        ttk.Style().configure("B.TButton", font=("Century Gothic", 20))

        self.var_grade = ttk.StringVar()
        self.var_weight = ttk.IntVar()
        self.var_des = ttk.StringVar()
        self.id = ttk.StringVar(value=ids[0])

        ttk.Label(self,
                  text="ID ucznia",
                  style="L.TLabel").pack(pady=30)

        combobox = (ttk.Combobox(self,
                                 state="readonly",
                                 textvariable=self.id,
                                 values=ids))
        combobox.pack()

        self.treeview = ttk.Treeview(self,
                                     columns=("subject", "grade", "weight", "description", "date"),
                                     show="headings")
        self.treeview.heading("subject", text="Przedmiot")
        self.treeview.heading("grade", text="Ocena")
        self.treeview.heading("weight", text="Waga")
        self.treeview.heading("description", text="Opis")
        self.treeview.heading("date", text="Data")

        self.treeview.column("subject", anchor="center", minwidth=50, width=100)
        self.treeview.column("grade", anchor="center", minwidth=50, width=100)
        self.treeview.column("weight", anchor="center", minwidth=50, width=100)
        self.treeview.column("description", anchor="center", minwidth=50, width=150)
        self.treeview.column("date", anchor="center", minwidth=50, width=100)
        self.treeview_fill()

        self.treeview.pack(pady=30, fill="both", expand=True, padx=40)

        ttk.Label(self,
                  text="Ocena",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.var_grade,
                     values=('-', '6', '-6', '+5', '5', '-5',
                             '+4', '4', '-4', '+3', '3', '-3', '+2', '2', '-2', '+1', '1')).pack()

        ttk.Label(self,
                  text="Waga",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.var_weight,
                     values=[str(x) for x in tuple(range(11))]).pack()

        ttk.Label(self,
                  text="Opis",
                  style="L.TLabel").pack(pady=30)

        ttk.Entry(self,
                  width=40,
                  textvariable=self.var_des).pack()

        self.button_confirm = ttk.Button(self,
                                         text="Wprowadź zmianę",
                                         style="B.TButton",
                                         state="disabled",
                                         command=lambda: self.change_values())
        self.button_confirm.pack(pady=30)

        combobox.bind("<<ComboboxSelected>>", lambda x: self.treeview_fill())
        self.treeview.bind("<ButtonRelease-1>", self.on_treeview_select)

    def treeview_fill(self) -> None:
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        data = self.mycol.find({"uid": self.id.get()})
        for i in data:
            self.treeview.insert("", "end", iid=f"{list(i.values())[0:1][0]}", values=list(i.values())[2:])

    def on_treeview_select(self, event):
        self.selected_item = self.treeview.focus()
        item_values = self.treeview.item(self.selected_item, "values")

        self.var_grade.set(item_values[1])
        self.var_weight.set(item_values[2])
        self.var_des.set(item_values[3])

        self.button_confirm.configure(state="active")

    def change_values(self) -> None:
        if "" not in (self.var_grade.get(), self.var_weight.get(), self.var_des.get()):
            self.mycol = self.mydb["lesson_journal"]

            self.mycol.update_one({"_id": ObjectId(self.selected_item)}, {"$set":
                                                                              {"Ocena": self.var_grade.get(),
                                                                               "Waga": int(self.var_weight.get()),
                                                                               "Opis": self.var_des.get()}})
            self.var_grade.set("-")
            self.var_weight.set(0)
            self.var_des.set("")
            self.treeview_fill()
            self.button_confirm.configure(state="disabled")
        else:
            messagebox.showinfo("Informacje", "Nie podano wszystkich informacji")


class FrameAdd(ttk.Frame):
    def __init__(self) -> None:
        super().__init__()
        col = pymongo.MongoClient("mongodb://localhost:27017/")["grades_db"]["login_data"]
        ids = []
        for i in col.find():
            ids.append(str(i["_id"]))

        ttk.Style().configure("L.TLabel", font=("Century Gothic", 20))
        ttk.Style().configure("B.TButton", font=("Century Gothic", 20))

        self.var_sub = ttk.StringVar()
        self.var_grade = ttk.StringVar()
        self.var_weight = ttk.IntVar()
        self.var_des = ttk.StringVar()
        self.id = ttk.StringVar()

        ttk.Label(self,
                  text="ID ucznia",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.id,
                     values=ids).pack()

        ttk.Label(self,
                  text="Przedmiot",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.var_sub,
                     values=("Matematyka",
                             "Biologia",
                             "Język angielski",
                             "Język polski",
                             "Język niemiecki",
                             "Język francuski",
                             "Język łaciński",
                             "Informatyka",
                             "WF",
                             "Chemia",
                             "Historia",
                             "Fizyka",
                             "Religia",
                             "Geografia",
                             "WOS")).pack()

        ttk.Label(self,
                  text="Ocena",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.var_grade,
                     values=('6', '-6', '+5', '5', '-5',
                             '+4', '4', '-4', '+3', '3', '-3', '+2', '2', '-2', '+1', '1')).pack()

        ttk.Label(self,
                  text="Waga",
                  style="L.TLabel").pack(pady=30)

        ttk.Combobox(self,
                     state="readonly",
                     textvariable=self.var_weight,
                     values=[str(x) for x in tuple(range(11))]).pack()

        ttk.Label(self,
                  text="Opis",
                  style="L.TLabel").pack(pady=30)

        ttk.Entry(self,
                  width=40,
                  textvariable=self.var_des).pack()

        ttk.Button(self,
                   text="Wprowadź ocenę",
                   style="B.TButton",
                   command=self.add_grade).pack(pady=30)

    def add_grade(self) -> None:
        uid = self.id.get()
        sub = self.var_sub.get()
        grade = self.var_grade.get()
        weight = self.var_weight.get()
        des = self.var_des.get()
        date = datetime.datetime.now().strftime("%d/%m/%Y")

        if "" not in (uid, sub, grade, weight, des, date):
            col = pymongo.MongoClient("mongodb://localhost:27017/")["grades_db"]["lesson_journal"]

            col.insert_one({"uid": uid,
                            "Przedmiot": sub,
                            "Ocena": grade,
                            "Waga": int(weight),
                            "Opis": des,
                            "Data": date})

            self.id.set("")
            self.var_sub.set("")
            self.var_grade.set("-")
            self.var_weight.set(0)
            self.var_des.set("")
        else:
            messagebox.showinfo("Informacje", "Nie podano wszystkich informacji")


if __name__ == '__main__':
    app = App()
    app.mainloop()
