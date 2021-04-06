from random import randint, sample
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
#cur.execute("DROP TABLE card")
cur.execute("""CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0)""")
conn.commit()


class BankingSystem:
    def __init__(self):
        self.IIN = 400000

    def luna(self, card):
        card = list(card)
        summ = 0
        for i in range(len(card)):
            if int(i) % 2 == 0:
                x = int(card[i]) * 2
                if x > 9:
                    x -= 9
                summ += x
            else:
                summ += int(card[i])
        if summ % 10 == 0:
            return 0
        return 10 - summ % 10

    def create_card(self):
        print('Your card has been created')
        cust_number = randint(100000000, 999999999)
        card = list(str(self.IIN) + str(cust_number))
        checksum = self.luna(card)
        credit_card = str(self.IIN) + str(cust_number) + str(checksum)
        PIN = sample(range(10), 4)
        PIN = ''.join(map(str, PIN))
        person = [111, credit_card, PIN, 0]
        cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", person)
        conn.commit()
        print(f'''Your card number:
{credit_card}
Your card PIN:
{PIN}
''')

    def into_acc(self, credit_card):
        while True:
            print('''
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit''')
            user_input = int(input())
            print()
            if user_input == 1:
                self.balance(credit_card)
            elif user_input == 2:
                print('Enter income:')
                money = int(input())
                cur.execute("SELECT * FROM card WHERE number = '%s'" % credit_card)
                check_number = cur.fetchone()
                cur.execute("UPDATE card SET number = %s, pin = %s, balance = %s" %
                            (credit_card, check_number[2], check_number[3] + money))
                conn.commit()
                print('Income was added!')
            elif user_input == 3:
                print("""Transfer
Enter card number:""")
                card_input = input()
                card = int(card_input) // 10
                checksum = int(card_input) % 10
                cur.execute("SELECT * FROM card WHERE number = '%s'" % credit_card)
                check_card = cur.fetchone()
                cur.execute("SELECT * FROM card WHERE number = '%s'" % card)
                card_transfer = cur.fetchone()
                if card_input.startswith('4') == False:
                    print("\nSuch a card does not exist.")
                elif checksum != self.luna(str(card)):
                    print('\nProbably you made mistake in the card number. Please try again!')
                elif card_input == credit_card:
                    print("\nYou can't transfer money to the same account!")
                else:
                    print("Enter how much money you want to transfer:")
                    money_transf = int(input())
                    if money_transf > check_card[3]:
                        print("Not enough money!")
                    else:
                        cur.execute("UPDATE card SET number = %s, pin = %s, balance = %s" %
                                    (check_card[1], check_card[2], check_card[3] - money_transf))
                        conn.commit()
                        if card_transfer is None:
                            person = [111, card_input, 2222, money_transf]
                            cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", person)
                            conn.commit()
                        print("Success!")
            elif user_input == 4:
                cur.execute("DELETE FROM card WHERE number = %s" % credit_card)
                conn.commit()
                print('The account has been closed!')
                print()
                break
            elif user_input == 5:
                print('You have successfully logged out!')
                print()
                break
            elif user_input == 0:
                print('Bye!')
                break

    def balance(self, credit_card):
        cur.execute("SELECT * FROM card WHERE number = '%s'" % credit_card)
        check_number = cur.fetchone()
        balance = check_number[3]
        print(balance)
        self.into_acc(credit_card)

    def main(self):
        while True:
            print('''1. Create an account
2. Log into account
0. Exit''')
            user_input = int(input())
            print()
            if user_input == 1:
                self.create_card()
            elif user_input == 2:
                print('Enter your card number:')
                credit_card = input()
                print('Enter your PIN:')
                PIN = input()
                cur.execute("SELECT * FROM card WHERE number = '%s'" % credit_card)
                check_number = cur.fetchone()
                if check_number is not None and credit_card in check_number and PIN in check_number:
                    print()
                    print('You have successfully logged in!')
                    self.into_acc(credit_card)
                else:
                    print()
                    print('Wrong card number or PIN!')
                    print()
            elif user_input == 0:
                print('Bye!')
                break


if __name__ == '__main__':
    BankingSystem().main()
