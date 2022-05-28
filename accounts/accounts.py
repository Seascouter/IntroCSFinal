users = {}
unpw = {}

# a new user is created
def add_user(un, pw):
    line = f"{un},{pw},3000,3000"
    with open("accounts/accounts.csv", 'a') as f:
        f.write(line)

# gets all users from the file and adds them to dictionaries
def get_users():
    with open("accounts/accounts.csv", 'r') as f:
        for line in f:
            line = line.strip()
            line = line.split(',')
            users[line[0]] = [int(line[2]), int(line[3]), line[1]]
            unpw[line[0]] = line[1]

# sets users file to new data in dictionaries
def set_users():
    with open('accounts/accounts.csv', 'w') as f:
        for user in users:
            #print(len(users[user]))
            line = f"{user},{users[user][2]},{users[user][0]},{users[user][1]}\n"
            #print(line)
            f.write(line)

# adjusts the amounts of wallet and bank from arguments
def adjust_amounts(user, new_wallet, new_bank):
    old_wallet = users[user][0]
    old_bank = users[user][1]
    old_total = old_wallet+old_bank

    if new_wallet + new_bank == old_total:
        users[user][0] = new_wallet
        users[user][1] = new_bank
        return [new_wallet, new_bank]
    else:
        return False

