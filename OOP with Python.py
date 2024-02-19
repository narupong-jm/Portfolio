import random

class ATM:
    def __init__(self, name, typeCard, cardNo, expired, cvv, username, balance):
        self.name = name
        self.typeCard = typeCard
        self.cardNo = cardNo
        self.expired = expired
        self.cvv = cvv
        self.username = username
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
        print(f"You deposit {amount} baht, your balance is {self.balance}.")
    def withdraw(self,amount):
        self.balance -= amount
        print(f"You withdraw {amount} baht, your balance is {self.balance}.")
    def requestOTP(self, phone):
        number = [0,1,2,3,4,5,6,7,8,9]
        otp_list = []
        for i in range(4):
            digit = str(random.choice(number))
            otp_list.append(digit)
        otp = otp_list[0] + otp_list[1] + otp_list[2] + otp_list[3]
        print(f"Your OTP will send to Phone: {phone}.")
        print(f"The OTP is {otp}")
    def transfer(self, amount, account):
        self.balance -= amount
        print(f"You transfer {amount} baht to account no: {account}, your balance is {self.balance}.")
    def loan(self,amount):
        self.balance += amount
        print(f"You loan {amount} baht, your balance is {self.balance}.")

atm1 = ATM("shoppee", "VISA", "1234-5678-4321-9876", "2023-09", "555", "Johnny_fun", 5000)

info = f"""
    Card name: {atm1.name} \n
    Card Type: {atm1.typeCard} \n
    Card No: {atm1.cardNo} \n
    Username: {atm1.username} \n
    balance: {atm1.balance}
    """
print(info)

atm1.deposit(500)

atm1.withdraw(500)

atm1.transfer(1000, "7654-1234-5633-0987")

atm1.loan(1000)

atm1.requestOTP("099-999-9999")
