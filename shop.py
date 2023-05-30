import component
import json

def login_with_email(hash):
    try:
        with open('data.json', 'r') as usr:
            json_data =  usr.read() 
            users = json.loads(json_data) if json_data else None
        return users['id'] == hash if users else None
    except:
       return None
       
def login(creds):
    current_user = component.getUserinfos(creds)
    print()
    return login_with_email(current_user['id'])
def register(creds):
    try:
        with open('data.json', 'w') as usr:
            usr.write(json.dump(component.getUserinfos(creds),usr, indent=4))
    except:
        return
user_input=''
while user_input.lower() != 'login' and user_input.lower() != 'register':
    user_input = input("do you want to login or register ? (login/register)")
    if(user_input == 'login'):
        creds = component.auth()
        if not login(creds):
            print('email not found')
            user_input = ''

        else :
            with open('data.json', 'r') as usr:
                json_data =  usr.read() 
                users = json.loads(json_data) if json_data else None
                print('Hello, ' + users['firstname'])
    elif(user_input == 'register'):
        creds = component.auth()
        register(creds)


