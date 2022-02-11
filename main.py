from tkinter import *
from tkinter import ttk
from dataBaseC import *
from threading import Thread
from time import time, sleep
from datetime import datetime


class Application:

    currentPage = None
    root = None
    loggedInUser = ""
    db = None

    def __init__(self, db):
        self.db = db
        self.root = Tk()

    def start(self):
        self.page1()
        self.root.mainloop()

    def loanHandle(self, accountID, amount, cycle):
        for i in range(10):
            sleep(cycle)
            account = self.db.Request(
                "SELECT FROM Accounts WHERE id==" + str(accountID) + " AND userNC==\"" + loggedInUser + "\";")
            self.db.Request("UPDATE Accounts WHERE id==" + str(accountID) + " VALUES (" + "\"" + account
                            .Result[0][1] + "\",\"" + account.Result[0][2] + "\",\"" + account.Result[0][
                                3] + "\"," + str(
                account.Result[0][4] - int(amount / 10)) + ");")
            print(account.Result)

    def createLoanThread(self, accountID, amount, cycle):
        try:
            amount = int(amount)
        except:
            self.loanRequest("Not valid value for amount")

        try:
            cycle = int(cycle)
        except:
            self.loanRequest("Not valid value for cycle")

        account = self.db.Request(
            "SELECT FROM Accounts WHERE id==" + str(accountID) + " AND userNC==\"" + loggedInUser + "\";")
        if len(account.Result) != 1:
            self.loanRequest("You dont have access to this account")
            return
        self.db.Request("UPDATE Accounts WHERE id==" + str(accountID) + " VALUES (" + "\"" + account
                        .Result[0][1] + "\",\"" + account.Result[0][2] + "\",\"" + account.Result[0][3] + "\"," + str(
            account.Result[0][4] + amount) + ");")
        Thread(target=self.loanHandle, args=(accountID, amount, cycle,)).start()
        self.menu()

    def loanRequest(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        loanPage = ttk.Frame(self.root, padding=100)
        loanPage.grid()
        self.currentPage = loanPage
        ttk.Label(loanPage, text="Register").grid(row=0, column=0)
        ttk.Label(loanPage, text="Account ID:").grid(row=1, column=0)
        input1 = ttk.Entry(loanPage)
        input1.grid(row=1, column=1)
        ttk.Label(loanPage, text="Amount:").grid(row=2, column=0)
        input2 = ttk.Entry(loanPage)
        input2.grid(row=2, column=1)
        ttk.Label(loanPage, text="Cycle:").grid(row=3, column=0)
        input3 = ttk.Entry(loanPage)
        input3.grid(row=3, column=1)
        ttk.Button(loanPage, text='Back', width=20, command=self.menu).grid(row=5, column=0)
        ttk.Button(loanPage, text='Create', width=20,
                   command=lambda: self.createLoanThread(input1.get(), input2.get(), input3.get())).grid(row=4,
                                                                                                         column=0)
        ttk.Label(loanPage, text=e1).grid(row=6, column=0)

    def login(self, nc, password):
        global loggedInUser
        result = self.db.Request("SELECT FROM Users WHERE nc==\"" + nc + "\" AND password==\"" + password + "\";")
        print(result.Result)
        if result.IsSuccess:
            if len(result.Result) == 1:
                loggedInUser = result.Result[0][1]
                self.menu()
            else:
                self.page1(e2="User not found")
        else:
            self.page1(e2=result.ErrorMessage)

    def newAccount(self, alias, password):
        checkAlias = self.db.Request(
            "SELECT FROM Accounts WHERE userNC==\"" + loggedInUser + "\" AND alias==\"" + alias + "\";")
        if len(checkAlias.Result) > 0:
            self.newAccountPage("Alias is Repeated")
            return
        result = self.db.Request(
            "INSERT INTO Accounts VALUES (\"" + loggedInUser + "\",\"" + alias + "\",\"" + password + "\",0);")
        if result.IsSuccess:
            self.menu()
        else:
            self.newAccountPage(e1=result.ErrorMessage)

    def signUp(self, nc, password, name, phone, email):
        result = self.db.Request(
            "INSERT INTO Users VALUES (" + "\"" + nc + "\",\"" + password + "\",\"" + name + "\",\"" + phone + "\",\"" + email + "\");")
        if result.IsSuccess:
            global loggedInUser
            loggedInUser = nc
            self.menu()
        else:
            self.page1(e1=result.ErrorMessage)

    def transferMoney(self, source, dest, amount, password):
        try:
            amount = int(amount)
        except:
            self.transferPage("Input a valid integer for amount")
            return
        account1 = self.db.Request("SELECT FROM Accounts WHERE userNC==\"" + loggedInUser + "\" AND id==" + str(
            source) + " AND password==\"" + password + "\";")
        if not account1.IsSuccess:
            self.transferPage(account1.ErrorMessage)
        if len(account1.Result) != 1:
            self.transferPage("source account ID or Password is wrong")
            return
        try:
            temp = int(dest)
            account2 = self.db.Request("SELECT FROM Accounts WHERE id==" + str(dest) + ";")
        except:
            account2 = self.db.Request("SELECT FROM MostlyUsed WHERE alias==\"" + str(dest) + "\";")
        if not account2.IsSuccess:
            self.transferPage(account2.ErrorMessage)
            return
        if len(account2.Result) != 1:
            self.transferPage("destination account not found")
            return
        account2 = self.db.Request("SELECT FROM Accounts WHERE id==" + str(account2.Result[0][3]) + ";")
        money = account1.Result[0][4]
        if money >= amount:
            self.db.Request("UPDATE Accounts WHERE id==" + str(source) + " VALUES (" + "\"" + account1
                            .Result[0][1] + "\",\"" + account1.Result[0][2] + "\",\"" + account1.Result[0][
                                3] + "\"," + str(
                money - amount) + ");")
            self.db.Request("UPDATE Accounts WHERE id==" + str(account2.Result[0][0]) + " VALUES (" + "\"" + account2
                            .Result[0][1] + "\",\"" + account2.Result[0][2] + "\",\"" + account2.Result[0][
                                3] + "\"," + str(
                account2.Result[0][4] + amount) + ");")
            self.db.Request("INSERT INTO Transactions VALUES (" + str(account2.Result[0][0]) + "," + source + "," + str(
                amount) + "," + str(int(time())) + ");")
            self.menu()
        else:
            self.transferPage("Not Enough Money")

    def transferPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        transferringPage = ttk.Frame(self.root, padding=100)
        transferringPage.grid()
        self.currentPage = transferringPage
        ttk.Label(transferringPage, text="alias/accountID").grid(row=1, column=0)
        ttk.Label(transferringPage, text="Most Used Accounts:").grid(row=0, column=0)
        mostlyUsed = self.db.Request("SELECT FROM MostlyUsed WHERE userNC==\"" + loggedInUser + "\";")
        scrollbar = Scrollbar(transferringPage)
        scrollbar.grid(row=2, column=1, sticky=NS)
        mylist = Listbox(transferringPage, yscrollcommand=scrollbar.set)
        for i in range(len(mostlyUsed.Result)):
            mylist.insert(END, str(mostlyUsed.Result[i][1]) + "/" + str(mostlyUsed.Result[i][3]))
        mylist.grid(row=2, column=0)
        scrollbar.config(command=mylist.yview)
        ttk.Label(transferringPage, text="Source account:").grid(row=3, column=0)
        input1 = ttk.Entry(transferringPage, width=5)
        input1.grid(row=3, column=1)
        ttk.Label(transferringPage, text="Destination account").grid(row=4, column=0)
        input2 = ttk.Entry(transferringPage, width=5)
        input2.grid(row=4, column=1)
        ttk.Label(transferringPage, text="Amount:").grid(row=5, column=0)
        input3 = ttk.Entry(transferringPage, width=5)
        input3.grid(row=5, column=1)
        ttk.Label(transferringPage, text="Password:").grid(row=6, column=0)
        input4 = ttk.Entry(transferringPage, width=5)
        input4.grid(row=6, column=1)
        ttk.Button(transferringPage, text="Transfer", width=20,
                   command=lambda: self.transferMoney(input1.get(), input2.get(), input3.get(), input4.get())).grid(
            row=7, column=0)
        ttk.Button(transferringPage, text='Back', width=20, command=self.menu).grid(row=8, column=0)
        ttk.Label(transferringPage, text=e1).grid(row=9, column=0)

    def mostUsed(self, accountID, alias):
        result = self.db.Request(
            "SELECT FROM MostlyUsed WHERE alias==\"" + alias + "\" AND userNC==\"" + loggedInUser + "\";")
        if len(result.Result) > 0:
            self.mostUsedPage("Alias Repeated")
            return
        result = self.db.Request(
            "SELECT FROM MostlyUsed WHERE accountID==" + accountID + " AND userNC==\"" + loggedInUser + "\";")
        if len(result.Result) > 0:
            self.mostUsedPage("Account is already in the list")
            return
        result = self.db.Request("SELECT FROM Accounts WHERE id==" + accountID + ";")
        if len(result.Result) != 1:
            self.mostUsedPage("Account not found")
            return
        self.db.Request("INSERT INTO MostlyUsed VALUES (\"" + alias + "\",\"" + loggedInUser + "\"," + accountID + ");")
        self.menu()

    def payBill(self, accountID, billCode, amount, password):
        try:
            amount = int(amount)
        except:
            self.billPage("Input a valid integer for amount")
            return
        account1 = self.db.Request("SELECT FROM Accounts WHERE userNC==\"" + loggedInUser + "\" AND id==" + str(
            accountID) + " AND password==\"" + password + "\";")
        if not account1.IsSuccess:
            self.billPage(account1.ErrorMessage)
        if len(account1.Result) != 1:
            self.billPage("source account ID or Password is wrong")
            return
        money = account1.Result[0][4]
        if money >= amount:
            self.db.Request("UPDATE Accounts WHERE id==" + str(accountID) + " VALUES (" + "\"" + account1
                            .Result[0][1] + "\",\"" + account1.Result[0][2] + "\",\"" + account1.Result[0][
                                3] + "\"," + str(
                money - amount) + ");")
            self.menu()
        else:
            self.billPage("Not Enough Money")

    def billPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        billingPage = ttk.Frame(self.root, padding=100)
        billingPage.grid()
        self.currentPage = billingPage
        ttk.Label(billingPage, text="Pay Bill:").grid(row=0, column=0)
        ttk.Label(billingPage, text="Paying account:").grid(row=3, column=0)
        input1 = ttk.Entry(billingPage, width=5)
        input1.grid(row=3, column=1)
        ttk.Label(billingPage, text="Bill Code:").grid(row=4, column=0)
        input2 = ttk.Entry(billingPage, width=5)
        input2.grid(row=4, column=1)
        ttk.Label(billingPage, text="Amount:").grid(row=5, column=0)
        input3 = ttk.Entry(billingPage, width=5)
        input3.grid(row=5, column=1)
        ttk.Label(billingPage, text="Password:").grid(row=6, column=0)
        input4 = ttk.Entry(billingPage, width=5)
        input4.grid(row=6, column=1)
        ttk.Button(billingPage, text="Pay", width=20,
                   command=lambda: self.payBill(input1.get(), input2.get(), input3.get(), input4.get())).grid(row=7,
                                                                                                              column=0)
        ttk.Button(billingPage, text='Back', width=20, command=self.menu).grid(row=8, column=0)
        ttk.Label(billingPage, text=e1).grid(row=9, column=0)

    def mostUsedPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        mostUsedFrame = ttk.Frame(self.root, padding=100)
        mostUsedFrame.grid()
        self.currentPage = mostUsedFrame
        ttk.Label(mostUsedFrame, text="alias/accountID").grid(row=1, column=0)
        ttk.Label(mostUsedFrame, text="Most Used Accounts:").grid(row=0, column=0)
        mostlyUsed = self.db.Request("SELECT FROM MostlyUsed WHERE userNC==\"" + loggedInUser + "\";")
        scrollbar = Scrollbar(mostUsedFrame)
        scrollbar.grid(row=2, column=1, sticky=NS)
        mylist = Listbox(mostUsedFrame, yscrollcommand=scrollbar.set)
        for i in range(len(mostlyUsed.Result)):
            mylist.insert(END, str(mostlyUsed.Result[i][1]) + "/" + str(mostlyUsed.Result[i][3]))
        mylist.grid(row=2, column=0)
        scrollbar.config(command=mylist.yview)
        ttk.Label(mostUsedFrame, text="Account ID:").grid(row=3, column=0)
        input1 = ttk.Entry(mostUsedFrame, width=5)
        input1.grid(row=3, column=1)
        ttk.Label(mostUsedFrame, text="alias:").grid(row=4, column=0)
        input2 = ttk.Entry(mostUsedFrame, width=5)
        input2.grid(row=4, column=1)
        ttk.Button(mostUsedFrame, text="Add", width=20,
                   command=lambda: self.mostUsed(input1.get(), input2.get())).grid(row=7, column=0)
        ttk.Button(mostUsedFrame, text='Back', width=20, command=self.menu).grid(row=8, column=0)
        ttk.Label(mostUsedFrame, text=e1).grid(row=9, column=0)

    def removeAccount(self, id, password, destination="0"):
        account = self.db.Request("SELECT FROM Accounts WHERE id==" + str(id) + " AND password==\"" + password + "\";")
        if len(account.Result) != 1:
            self.viewAccount(id, "wrong password")
            return
        if account.Result[0][4] > 0:
            account2 = self.db.Request("SELECT FROM Accounts WHERE id==" + destination + ";")
            if len(account2.Result) != 1:
                self.viewAccount(id, "destination account not found")
                return
            self.db.Request("UPDATE Accounts WHERE id==" + destination + " VALUES (\"" + account2
                            .Result[0][1] + "\",\"" + account2.Result[0][2] + "\",\"" + account2.Result[0][
                                3] + "\"," + str(
                account2.Result[0][4] + account.Result[0][4]) + ");")
        self.db.Request("DELETE FROM Accounts WHERE id==" + str(id) + ";")
        self.db.Request(
            "INSERT INTO Transactions VALUES (" + destination + "," + id + "," + str(account.Result[0][4]) + "," + str(
                int(time())) + ");")
        self.menu()

    def viewAccount(self, id, e1=""):
        self.currentPage.destroy()
        account = self.db.Request(
            "SELECT FROM Accounts WHERE id==" + str(id) + " AND userNC==\"" + loggedInUser + "\";")
        if len(account.Result) != 1:
            self.accounts("You dont have access to this account")
        else:
            result = self.db.Request("SELECT FROM Transactions WHERE source==" + str(id) + " OR dest==" + str(
                id) + ";")
            if result.IsSuccess:
                accountPage = ttk.Frame(self.root, padding=100)
                accountPage.grid()
                ttk.Label(accountPage, text="dest/source/amount/date").grid(row=0, column=0)
                self.currentPage = accountPage
                scrollbar = Scrollbar(accountPage)
                scrollbar.grid(row=1, column=1, sticky=NS)
                mylist = Listbox(accountPage, yscrollcommand=scrollbar.set, width=30)
                for i in range(len(result.Result)):
                    mylist.insert(END, str(result.Result[i][1]) + "/" + str(result.Result[i][2]) + "/" + str(
                        result.Result[i][3]) + "/" + datetime.utcfromtimestamp(result.Result[i][4]).strftime(
                        '%Y-%m-%d %H:%M:%S'))
                mylist.grid(row=1, column=0)
                scrollbar.config(command=mylist.yview)
                ttk.Label(accountPage, text="Password:").grid(row=2, column=0)
                input1 = ttk.Entry(accountPage, width=5)
                input1.grid(row=2, column=1)
                if account.Result[0][4] > 0:
                    ttk.Label(accountPage, text="Account To Move money:").grid(row=3, column=0)
                    input2 = ttk.Entry(accountPage, width=5)
                    input2.grid(row=3, column=1)
                    ttk.Button(accountPage, text='Remove Account', width=20,
                               command=lambda: self.removeAccount(id, input1.get(), input2.get())).grid(row=4, column=0)
                else:
                    ttk.Button(accountPage, text='Remove Account', width=20,
                               command=lambda: self.removeAccount(id, input1.get())).grid(row=4, column=0)
                ttk.Button(accountPage, text='Back', width=20, command=self.accounts).grid(row=5, column=0)
                ttk.Label(accountPage, text=e1).grid(row=6, column=0)
            else:
                self.accounts(result.ErrorMessage)

    def addUser(self, nc, password, name, phone, email):
        result = self.db.Request(
            "INSERT INTO Users VALUES (" + "\"" + nc + "\",\"" + password + "\",\"" + name + "\",\"" + phone + "\",\"" + email + "\");")
        if result.IsSuccess:
            global loggedInUser
            loggedInUser = nc
            self.adminMenu()
        else:
            self.editOrNewUserPage(False, "0", e1=result.ErrorMessage)

    def updateUser(self, userID, nc, password, name, phone, email):
        result = self.db.Request(
            "UPDATE Users WHERE id=="+userID+" VALUES (" + "\"" + nc + "\",\"" + password + "\",\"" + name + "\",\"" + phone + "\",\"" + email + "\");")
        if result.IsSuccess:
            global loggedInUser
            loggedInUser = nc
            self.adminMenu()
        else:
            self.editOrNewUserPage(True, userID, e1=result.ErrorMessage)

    def editOrNewUserPage(self, edit, userID, e1=""):
        account = None
        if edit:
            account = self.db.Request("SELECT FROM Users WHERE id=="+userID+";")
            if len(account.Result) != 1:
                self.usersPage("account not found")
                return
        if self.currentPage is not None:
            self.currentPage.destroy()
        page = ttk.Frame(self.root, padding=100)
        page.grid()
        self.currentPage = page
        if edit:
            ttk.Label(page, text=account.Result[0][1]+"/"+account.Result[0][2]+"/"+account.Result[0][3]+"/"+account.Result[0][4]+"/"+account.Result[0][5]).grid(row=0, column=0)
        ttk.Label(page, text="Change the inputs to update or create new user").grid(row=1, column=0)
        ttk.Label(page, text="NationalCode").grid(row=2, column=0)
        input1 = ttk.Entry(page)
        input1.grid(row=2, column=1)
        ttk.Label(page, text="Password").grid(row=3, column=0)
        input2 = ttk.Entry(page)
        input2.grid(row=3, column=1)
        ttk.Label(page, text="Name").grid(row=4, column=0)
        input3 = ttk.Entry(page)
        input3.grid(row=4, column=1)
        ttk.Label(page, text="Email").grid(row=5, column=0)
        input4 = ttk.Entry(page)
        input4.grid(row=5, column=1)
        ttk.Label(page, text="Phone").grid(row=6, column=0)
        input5 = ttk.Entry(page)
        input5.grid(row=6, column=1)
        if edit:
            ttk.Button(page, text='Confirm', width=10,
                       command=lambda: self.updateUser(userID, input1.get(), input2.get(), input3.get(), input4.get(),
                                                   input5.get())).grid(row=7, column=0)
        else:
            ttk.Button(page, text='Confirm', width=10,
                       command=lambda: self.addUser(input1.get(), input2.get(), input3.get(), input4.get(),
                                                   input5.get())).grid(row=7, column=0)
        ttk.Button(page, text='Back', width=20, command=self.usersPage).grid(row=8, column=0)
        ttk.Label(page, text=e1).grid(row=9, column=0)

    def usersPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        result = self.db.Request("SELECT FROM Users;")
        userPage = ttk.Frame(self.root, padding=100)
        userPage.grid()
        ttk.Label(userPage, text="ID/national code/password/name/phone/email").grid(row=0, column=0, columnspan=3)
        self.currentPage = userPage
        scrollbar = Scrollbar(userPage)
        scrollbar.grid(row=1, column=1, sticky=NS)
        mylist = Listbox(userPage, yscrollcommand=scrollbar.set, width=80)
        for i in range(len(result.Result)):
            mylist.insert(END,str(result.Result[i][0]) + "/" + result.Result[i][1] + "/" + result.Result[i][2] + "/" + result.Result[i][3]+ "/" + result.Result[i][4]+ "/" + result.Result[i][5])
        mylist.grid(row=1, column=0)
        scrollbar.config(command=mylist.yview)
        ttk.Label(userPage, text="Edit User By ID:").grid(row=2, column=0)
        input2 = ttk.Entry(userPage, width=5)
        input2.grid(row=2, column=1)
        ttk.Button(userPage, text='Edit User', width=20, command=lambda: self.editOrNewUserPage(True, input2.get())).grid(row=3,
                                                                                                          column=0)
        ttk.Button(userPage, text='New User', width=20, command=lambda: self.editOrNewUserPage(False, "0")).grid(row=4,
                                                                                                         column=0)
        ttk.Button(userPage, text='Back', width=20, command=self.adminMenu).grid(row=5, column=0)
        ttk.Label(userPage, text=e1).grid(row=6, column=0)

    def accountBalance(self, id, newBalance):
        try:
            newBalance = int(newBalance)
        except:
            self.manageAccounts("Invalid type for balance")
            return
        account = self.db.Request("SELECT FROM Accounts WHERE id=="+id+";")
        if len(account.Result) != 1:
            self.manageAccounts("Account not found")
            return
        db.Request("UPDATE Accounts WHERE id==" + id + " VALUES (\""+account.Result[0][1]+"\",\""+account.Result[0][2]+"\",\""+account.Result[0][3]+"\","+str(newBalance)+");")
        self.adminMenu()

    def manageAccounts(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        result = self.db.Request("SELECT FROM Accounts;")
        manageAccountPages = ttk.Frame(self.root, padding=100)
        manageAccountPages.grid()
        ttk.Label(manageAccountPages, text="ID/userNC/balance").grid(row=0, column=0, columnspan=3)
        self.currentPage = manageAccountPages
        scrollbar = Scrollbar(manageAccountPages)
        scrollbar.grid(row=1, column=1, sticky=NS)
        mylist = Listbox(manageAccountPages, yscrollcommand=scrollbar.set, width=80)
        for i in range(len(result.Result)):
            mylist.insert(END,str(result.Result[i][0]) + "/" + result.Result[i][1] + "/" + str(result.Result[i][4]))
        mylist.grid(row=1, column=0)
        scrollbar.config(command=mylist.yview)
        ttk.Label(manageAccountPages, text="Account ID:").grid(row=2, column=0)
        input1 = ttk.Entry(manageAccountPages, width=5)
        input1.grid(row=2, column=1)
        ttk.Label(manageAccountPages, text="Balance:").grid(row=3, column=0)
        input2 = ttk.Entry(manageAccountPages, width=5)
        input2.grid(row=3, column=1)
        ttk.Button(manageAccountPages, text='Edit Account Balance', width=20, command=lambda: self.accountBalance(input1.get(), input2.get())).grid(row=4,
                                                                                                          column=0)
        ttk.Button(manageAccountPages, text='Back', width=20, command=self.adminMenu).grid(row=6, column=0)
        ttk.Label(manageAccountPages, text=e1).grid(row=7, column=0)

    def adminMenu(self):
        if self.currentPage is not None:
            self.currentPage.destroy()
        adminPanel = ttk.Frame(self.root, padding=100)
        adminPanel.grid()
        self.currentPage = adminPanel
        ttk.Label(adminPanel, text="Admin Panel").grid(row=0, column=0)
        ttk.Button(adminPanel, text='Users', width=20, command=self.usersPage).grid(row=1, column=0)
        ttk.Button(adminPanel, text='Manage Accounts', width=20, command=self.manageAccounts).grid(row=2, column=0)
        ttk.Button(adminPanel, text='Logout', width=20, command=self.page1).grid(row=7, column=0)

    def adminLogin(self, username, password):
        result = self.db.Request("SELECT FROM Admins WHERE username==\"" + username + "\" AND password==\"" + password + "\";")
        if not result.IsSuccess:
            self.adminLoginPage(result.ErrorMessage)
            return
        if len(result.Result) != 1:
            self.adminLoginPage("Username or Password is wrong")
            return
        self.adminMenu()

    def adminLoginPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        adminPage = ttk.Frame(self.root, padding=100)
        adminPage.grid()
        self.currentPage = adminPage
        ttk.Label(adminPage, text="Admin Login").grid(row=0, column=0)
        ttk.Label(adminPage, text="Username:").grid(row=1, column=0)
        input1 = ttk.Entry(adminPage)
        input1.grid(row=1, column=1)
        ttk.Label(adminPage, text="Password:").grid(row=2, column=0)
        input2 = ttk.Entry(adminPage)
        input2.grid(row=2, column=1)
        ttk.Button(adminPage, text='Login', width=10,
                   command=lambda: self.adminLogin(input1.get(), input2.get())).grid(row=3, column=0)
        ttk.Button(adminPage, text="Login as a user", command=self.page1).grid(row=4, column=0)
        ttk.Label(adminPage, text=e1).grid(row=5, column=0)

    def page1(self, e1="", e2=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        firstPage = ttk.Frame(self.root, padding=100)
        firstPage.grid()
        self.currentPage = firstPage
        # Register Part
        ttk.Label(firstPage, text="Register").grid(row=0, column=0)
        registerFrame = ttk.Frame(firstPage, padding=10)
        registerFrame.grid(row=1, column=0)
        ttk.Label(registerFrame, text="NationalCode").grid(row=1, column=0)
        rInput1 = ttk.Entry(registerFrame)
        rInput1.grid(row=1, column=1)
        ttk.Label(registerFrame, text="Password").grid(row=2, column=0)
        rInput2 = ttk.Entry(registerFrame)
        rInput2.grid(row=2, column=1)
        ttk.Label(registerFrame, text="Name").grid(row=3, column=0)
        rInput3 = ttk.Entry(registerFrame)
        rInput3.grid(row=3, column=1)
        ttk.Label(registerFrame, text="Email").grid(row=4, column=0)
        rInput4 = ttk.Entry(registerFrame)
        rInput4.grid(row=4, column=1)
        ttk.Label(registerFrame, text="Phone").grid(row=5, column=0)
        rInput5 = ttk.Entry(registerFrame)
        rInput5.grid(row=5, column=1)
        ttk.Button(registerFrame, text='Register', width=10,
                   command=lambda: self.signUp(rInput1.get(), rInput2.get(), rInput3.get(), rInput4.get(),
                                               rInput5.get())).grid(row=6, column=0)
        ttk.Label(registerFrame, text=e1).grid(row=7, column=0)
        # Login Part
        ttk.Label(firstPage, text="Login").grid(row=0, column=1)
        loginFrame = ttk.Frame(firstPage, padding=10)
        loginFrame.grid(row=1, column=1)
        ttk.Label(loginFrame, text="NationalCode").grid(row=1, column=0)
        lInput1 = ttk.Entry(loginFrame)
        lInput1.grid(row=1, column=1)
        ttk.Label(loginFrame, text="Password").grid(row=2, column=0)
        lInput2 = ttk.Entry(loginFrame)
        lInput2.grid(row=2, column=1)
        ttk.Button(loginFrame, text='Login', width=10,
                   command=lambda: self.login(lInput1.get(), lInput2.get())).grid(row=3, column=0)
        ttk.Button(loginFrame, text="Login as an admin", command=self.adminLoginPage).grid(row=4, column=0)
        ttk.Label(loginFrame, text=e2).grid(row=5, column=0)

    def menu(self):
        if self.currentPage is not None:
            self.currentPage.destroy()
        secondPage = ttk.Frame(self.root, padding=100)
        secondPage.grid()
        self.currentPage = secondPage
        ttk.Label(secondPage, text="Menu").grid(row=0, column=0)
        ttk.Button(secondPage, text='New Account', width=20, command=self.newAccountPage).grid(row=1, column=0)
        ttk.Button(secondPage, text='Accounts Details', width=20, command=self.accounts).grid(row=2, column=0)
        ttk.Button(secondPage, text='Add Most Used Accounts', width=20, command=self.mostUsedPage).grid(row=3, column=0)
        ttk.Button(secondPage, text='Transfer Money', width=20, command=self.transferPage).grid(row=4, column=0)
        ttk.Button(secondPage, text='Pay Bill', width=20, command=self.billPage).grid(row=5, column=0)
        ttk.Button(secondPage, text='Request Loan', width=20, command=self.loanRequest).grid(row=6, column=0)
        ttk.Button(secondPage, text='Logout', width=20, command=self.page1).grid(row=7, column=0)

    def newAccountPage(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        thirdPage = ttk.Frame(self.root, padding=100)
        thirdPage.grid()
        self.currentPage = thirdPage
        ttk.Label(thirdPage, text="New Account").grid(row=0, column=0)
        ttk.Label(thirdPage, text="Alias").grid(row=1, column=0)
        input1 = ttk.Entry(thirdPage)
        input1.grid(row=1, column=1)
        ttk.Label(thirdPage, text="Passcode").grid(row=2, column=0)
        input2 = ttk.Entry(thirdPage)
        input2.grid(row=2, column=1)
        ttk.Button(thirdPage, text='Back', width=20, command=self.menu).grid(row=3, column=0)
        ttk.Button(thirdPage, text='Create', width=20,
                   command=lambda: self.newAccount(input1.get(), input2.get())).grid(row=4, column=0)
        ttk.Label(thirdPage, text=e1).grid(row=5, column=0)

    def accounts(self, e1=""):
        if self.currentPage is not None:
            self.currentPage.destroy()
        result = self.db.Request("SELECT FROM Accounts WHERE userNC==\"" + loggedInUser + "\";")
        forthPage = ttk.Frame(self.root, padding=100)
        forthPage.grid()
        ttk.Label(forthPage, text="ID/alias/password/balance").grid(row=0, column=0)
        self.currentPage = forthPage
        scrollbar = Scrollbar(forthPage)
        scrollbar.grid(row=1, column=1, sticky=NS)
        mylist = Listbox(forthPage, yscrollcommand=scrollbar.set)
        for i in range(len(result.Result)):
            mylist.insert(END,
                          str(result.Result[i][0]) + "/" + result.Result[i][2] + "/" + result.Result[i][3] + "/" + str(
                              result.Result[i][4]))
        mylist.grid(row=1, column=0)
        scrollbar.config(command=mylist.yview)
        ttk.Label(forthPage, text="View Account By ID:").grid(row=2, column=0)
        input2 = ttk.Entry(forthPage, width=5)
        input2.grid(row=2, column=1)
        ttk.Button(forthPage, text='View', width=20, command=lambda: self.viewAccount(input2.get())).grid(row=3,
                                                                                                          column=0)
        ttk.Button(forthPage, text='Back', width=20, command=self.menu).grid(row=4, column=0)
        ttk.Label(forthPage, text=e1).grid(row=5, column=0)


db = Database()
app = Application(db)
app.start()