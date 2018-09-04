#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time, gmtime, strftime, sleep
from guizero import App, Picture, Waffle, Text,TextBox, Window, warn, info, PushButton, yesno
from pyfingerprint.pyfingerprint import PyFingerprint
import multiprocessing
import csv

# initialise fingerprint module
f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

#search for ID in a file when user logins
#this is to avoid duplicate login
def searchID(IDD):
    stat = False # flag to check the search status
    print(IDD)
    remFile = open('remdata.csv', 'r') # open the file in read mode
    csvReader = csv.reader(remFile) # pass file to csv reader
    #print(csvReader)
    data = list(csvReader) # convert the contents to a list
    print(data)
    for i in data: #iterate through the list
        # update attendance text with the number of logins in the file
        attendance_text.value = str(len(i)) +' out of ' + str(f.getTemplateCount()) 
        for j in range(len(i)):
            if i[j] == IDD: # if user ID is found, stat is true
                stat = True
     
    # close the file
    remFile.close()
    return stat       
 
# write password
def updatePassword(pwd): #updates password in the file
    print(pwd)
    with open("pwdData.txt", "w") as log: #open file in write mode
                    log.write("{0}".format(pwd))
    

#read password
def readPwd(): #reads password from file during authenication
    pwd = "" # create an empty variable to hold retrieved password
    f = open("pwdData.txt") #open file with default read mode
    
    # read file content line by line
    # but this file should have only one line
    pwd = f.readline()
    f.close() #make sure you close the file
    
    return pwd
            
            
# this file is written to when a user logs in
# this stops the user from login in more than once
def writeRemToCSV(IDD):
    print(IDD)
    with open("remdata.csv", "a") as log:
                    log.write("{0},".format(IDD))
                    
# this file saves timestamp of logins in csv format with user ID                    
def writeLoginData(IDD):
    print(IDD)
    with open("login.csv", "a") as log:
                    log.write("{0},{1},{2}\n".format(strftime("%Y-%m-%d %H:%M:%S"), IDD, 'i'))

# this file saves timestamp of logouts in csv format with user ID 
def writeLogoutData(IDD):
    with open("logout.csv", "a") as log:
                    log.write("{0},{1},{2}\n".format(strftime("%Y-%m-%d %H:%M:%S"), IDD, 'o'))
    
  
# this method performs two functions
# 1 - updates the dashboard time
# 2 - holds code for login, it repeats every 100ms 
# just like a loop
def update_time():
    main_window_time.value = strftime("%H:%M:%S", gmtime()) #updates time
    ## Tries to search the finger
    try:
            print('Waiting for finger...')

            ## Wait that finger is read
            if( f.readImage() == True ):
                ## Converts read image to characteristics and stores it in charbuffer 1
                f.convertImage(0x01)
                ## Searchs template
                result = f.searchTemplate()

                positionNumber = result[0]
                accuracyScore = result[1]
                
                if ( positionNumber == -1 ):
                    print('No match found!')
                    return
                #exit(0)
                else:
                    #add to remember_data array for welcome and goodbye
                    if searchID(str(positionNumber)): #search if user have logged in before
                        print('bye')
                        msg_text.value = 'bye' # if true, log user out with bye
                        writeLogoutData(str(positionNumber)) # update file with user logout stamp
                        sleep(2) #delay for 2 seconds so user can remove his/her finger
                        msg_text.value = '' #empty message text
                    else:
                        print('welcome')
                        msg_text.value = 'welcome' #if false, log user in with welcome
                        writeRemToCSV(str(positionNumber)) #enter user ID into file to avoid double login
                        writeLoginData(str(positionNumber)) # update file with user login stamp
                        sleep(2) #delay for 2 seconds so user can remove his/her finger
                        msg_text.value = ''  #empty message text
                        
                    print('Found template at position #' + str(positionNumber))
                    print('The accuracy score is: ' + str(accuracyScore))
                    sleep(2)

            else:
                 return
            
    except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
    return
        #exit(1)
 
# function to update date on the dashboard 
def update_date():
    main_window_date.value = strftime("%d,%b,%Y", gmtime())

def update_attendance():
    pass

# function to initalise the fingerprint module
def module_init():
    try:           

        if ( f.verifyPassword() == False ):
            module_test.value =  'The given fingerprint sensor password is wrong!'
            raise ValueError('The given fingerprint sensor password is wrong!')
        else:
            module_test.value =  'Module successfully loaded'
            
            
    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        module_test.append('Exception message: ' + str(e));
        exit(1)


# function notifies user if attempting to enter restricted areas
def admin_warn():
    warn("NOTE!!", "You will need to provide authenications from here!")
    admin_menu_window.show(wait=True) # if user continues, show new window in modal mode 
    app.hide() # hide app or main window

# function notifies user if attempting to enter restricted areas
def admin_mainmenu_warn():
    info("INFO!!", "Please provide authenication!")

# switches windows on button click
def change_password_auth():
    change_pass_password_window.show(wait=True)
    admin_menu_window.hide()
    
# returns back to app or main window    
def admin_back():
    app.show()
    admin_menu_window.hide()

# switches windows on button click
def check_admin_pass():
    admin_mainmenu_pass_window.show(wait=True)
    admin_menu_window.hide()
    
def update_msg():
    msg_text.value = ''
    
    
#windows starts
# all the windows are created here and are hidden immediately    
app = App(title="Biometeric System", width=210, height=210,layout="grid")

admin_menu_window = Window(app, title="Admin Menu", width=210, height=210,layout="grid")
admin_menu_window.hide()

admin_mainmenu_pass_window = Window(app, title="Authenication yourself", width=210, height=210)
admin_mainmenu_pass_window.hide()

mainmenu_window = Window(app, title="Main Menu", width=210, height=210)
mainmenu_window.hide()

enroll_window = Window(app, title="Enroll", width=210, height=210)
enroll_window.hide()

change_pass_password_window = Window(app, title="Provide authenication", width=210, height=210)
change_pass_password_window.hide()

change_password_window = Window(app, title="Change Password", width=210, height=210)
change_password_window.hide()

delete_menu_window = Window(app, title="Delete Menu", width=210, height=210)
delete_menu_window.hide() 
#windows ends

#main window starts
# user can login or logout on this window
# admin menu can be accessed from here

main_window_time = Text(app, text=strftime("%H:%M:%S", gmtime()), grid=[0,0])
main_window_time.repeat(100, update_time)  # Schedule call to update time

main_window_date = Text (app, text=strftime("%d,%b,%Y", gmtime()), grid=[0,1]) 
main_window_date.repeat(10800000, update_date)  #repeat every 3hrs

module_test = Text(app, text="checking modules...", grid=[0,2])


admin_menu_btn = PushButton(app, text="ADMIN MENU" ,command=admin_warn, grid=[0,4])
admin_menu_btn.bg = "blue"

msg_text = Text(app, text="####", grid=[0,5])
#msg_text.repeat(5000, update_msg)

attendance_text = Text(app, text="####", grid=[0,6])
picture1 = Picture(app, image="28.jpg", grid=[1,0,3,6])
module_init() #initialize module
#main window ends

#admin menu window starts
admin_main_menu_btn = PushButton(admin_menu_window, text="Main Menu" ,command=check_admin_pass, grid=[0,0])
admin_main_menu_btn.bg = "blue"

back_btn = PushButton(admin_menu_window, text="Back" ,command=admin_back, grid=[1,0])
back_btn.bg = "blue"

chgPassword_btn = PushButton(admin_menu_window, text="change Password", command=change_password_auth, grid=[2,0])
chgPassword_btn .bg = "blue"
#admin menu window ends

#admin menu password window starts
def chk_password():
    global admin_password
    
    if len(password_box.value) == 8:
        if password_box.value == readPwd():#admin_password:
            password_chk_text.value = "correct"
            sleep(.2)
            mainmenu_window.show(wait=True)
            admin_mainmenu_pass_window.hide()
            password_box.value = ""
        else:
            password_chk_text.value = "incorrect"
            password_box.value = ""
    
    elif not password_box.value == admin_password:
         password_chk_text.value = "incomplete and incorrect"
         
    
    
password_box = TextBox(admin_mainmenu_pass_window,  grid=[0,0])
password_box.height=30
password_box.width=20
password_box.update_command(chk_password)
password_chk_text = Text (admin_mainmenu_pass_window, text="", grid=[1,0])
#admin menu password window ends

#change admin password password window starts
def chk_chg_password():
    passw = readPwd()
    if len(pass_box.value) == 8:
        if pass_box.value == passw:#admin_password:
            pass_chk_text.value = "correct"
            sleep(.2)
            change_password_window.show(wait=True)
            change_pass_password_window.hide()
        else:
            pass_chk_text.value = "incorrect"
    
    elif not pass_box.value == passw:
         pass_chk_text.value = "incomplete and incorrect"

pass_box = TextBox(change_pass_password_window)
pass_box.update_command(chk_chg_password)
check_btn = PushButton(change_pass_password_window, text="check" ,command=chk_chg_password)
pass_chk_text = Text (change_pass_password_window, text="")
#change admin password password window ends

#change admin password window starts
def pass_operation():
    passw = readPwd()
    if not pass1_box.value ==  passw:
       passw_chk_text.value =  "this is not the current password" 
    elif not pass2_box.value == vpass2_box.value:
       passw_chk_text.value =  "new password doesnt match verify password" 
    elif not len(vpass2_box.value) <= 8:
        passw_chk_text.value =  "password length is less than 8 characters"
    else:
        updatePassword(vpass2_box.value)
        passw_chk_text.value =  "Operation was successful"
        
def back_to_main():
    passw_chk_text.value =  "Going back..."
    sleep(2)
    app.show()
    change_password_window.hide()
    
    
pass1_box = TextBox(change_password_window)
pass2_box = TextBox(change_password_window) 
vpass2_box = TextBox(change_password_window)
vpass2_box.update_command(pass_operation)
passw_chk_text = Text (change_password_window, text="")
back_main_btn = PushButton(change_password_window, text="BACK" ,command=back_to_main)
#change admin password window ends 

#main menu starts
def enroll_PF():
    enroll_window.show(wait=True)
    admin_mainmenu_pass_window.hide()
    mainmenu_window.hide()
    
def _back():
    mainmenu_window.hide()
    enroll_window.show()
    
def delete_menu():
    delete_menu_window.show(wait=True)
    mainmenu_window.hide()
    
enroll_btn = PushButton(mainmenu_window, text="Start Enrolling", command=enroll_PF)
b_btn = PushButton(mainmenu_window, text="Back", command=_back)
delete_menu_btn = PushButton(mainmenu_window, text="Delete Menu", command=delete_menu)
#main menu ends

#delete menu window starts
def clear():
    ## Tries to delete the template of the finger
    try:
        for i in range(f.getStorageCapacity()):
            f.deleteTemplate(i)

    except Exception as e:
        clearDB_text.value = "Operation failed! " + 'Exception message: ' + str(e)
        print('Operation failed!')
        print('Exception message: ' + str(e))
    return

def clear_FDB():
    clearDB = yesno("HEY!!!", "Are you sure?")
    if clearDB == True:
        clear()
        info("HEY!!", "Operation was successful")
    else:
        info("NOTE!!", "Going back to main window ")
        delete_menu_window.hide()
        app.show()
        
clear_FDB_btn = PushButton(delete_menu_window, text="Clear FDB", command=clear_FDB)
clearDB_text = Text (delete_menu_window, text='Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
#delete menu window ends

#enroll window starts
def enroll():
    ## Gets some sensor information
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    enroll_status_text1.value =  'Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity())
    ## Tries to enroll new finger
    try:
        print('Waiting for finger...')
        enroll_status_text2.value = 'Waiting for finger...'
        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Checks if finger is already enrolled
        result = f.searchTemplate()
        positionNumber = result[0]
        

        #if ( positionNumber >= 0 ):
        if(positionNumber >= 0):
            print('Template already exists at position #' + str(positionNumber))
            enroll_status_text2.value = 'Template already exists at position #' + str(positionNumber)
            return
            #exit(0)
        else:
            positionNumber = int(pf_box.value)

        print('Remove finger...')
        enroll_status_text2.value = 'Remove finger...'
        sleep(2)

        print('Waiting for same finger again...')
        enroll_status_text2.value = 'Waiting for same finger again...'

        ## Wait that finger is read again
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 2
        f.convertImage(0x02)

        ## Compares the charbuffers
        if ( f.compareCharacteristics() == 0 ):
            enroll_status_text2.value = 'Fingers do not match'
            raise Exception('Fingers do not match')

        ## Creates a template
        f.createTemplate()

        ## Saves template at new position number
        positionNumber = f.storeTemplate(int(pf_box.value), 0x01)
        enroll_status_text2.value = 'Finger enrolled successfully!'
        print('Finger enrolled successfully!')
        enroll_status_text2.value = 'New template position #' + str(positionNumber)
        print('New template position #' + str(positionNumber))
        sleep(5)

    except Exception as e:
        print('Operation failed!')
        enroll_status_text2.value = 'Operation failed!'
        print('Exception message: ' + str(e))
        sleep(2)
        enroll_status_text2.value = 'Exception message: ' + str(e)
    return
    #exit(1)
    pass
def back_M():
    enroll_window.hide()
    app.show()
    
pf_box = TextBox(enroll_window, text="Enter PF number")
enroll_status_text1 = Text (enroll_window, text="")
enroll_status_text2 = Text (enroll_window, text="")
enrollP_btn = PushButton(enroll_window, text="Start", command=enroll)
backP_btn = PushButton(enroll_window, text="Back", command=back_M)

#enroll window ends
app.display()