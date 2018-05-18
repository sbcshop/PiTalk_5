#!/usr/bin/python3
#coding = utf-8


import tkinter as tk
import pitalk
import picamera
import datetime
import math
import calendar
import logging
from PIL import Image, ImageTk
import subprocess
import shlex
import time
import os
import sys

############################  Icon  ############################################
class Icon:
    def __init__(self):
        try:
            for file in sorted(os.listdir(path+'/Icons')):
                icons.append(tk.PhotoImage(file=path + "/Icons/" + file))
        except:
            pass

###################################  MainApp  ##################################
class MainApp(pitalk.PiTalk, tk.Tk):
    """
    This is a class for Creating Frames, Key Press Handling, Flags Checking,
    Network Update and Call/SMS Logs
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.ws = tk.Tk.winfo_screenwidth(self)
        self.hs = tk.Tk.winfo_screenheight(self)
        self.w = 480  #screen width
        self.h = 800  #screen height
        self.bar_width = 30 #width of the signal bar
        self.bar_height = 20 #height of the signal bar
        self.x = (self.ws/2) - (self.w/2) # x coordinate of the screen edge
        self.y = (self.hs/2) - (self.h/2)

        self.Fl_incoming = False
        self.Fl_Auto_Answer = False
        self.Fl_initialize = False
        self.networkName = None
        self.imei = None
        
        self.geometry("%dx%d+%d+%d" %(self.w, self.h, self.x, self.y))
        self.title("PiTalk")
        if not self.ws > self.w:
            self.attributes('-fullscreen', True)
            self.config(cursor="none")

        self.Topframe = tk.Frame(self, bg = "black")
        self.Topframe.pack(side='top', fill = 'x', anchor = 'w')
        for i in range(8):
            self.Topframe.grid_columnconfigure(i, weight = 1)
            
        self.networkLabel = tk.Label(self.Topframe, text ="",bg = "black",
                                     fg = "OliveDrab1", font = ("Helvetica",14))
        self.networkLabel.grid(row = 0, column = 0, columnspan = 3 ,
                               sticky = "w")
        
        self.timeLabelTop = tk.Label(self.Topframe, text = "",bg = "black",
                                     fg = "tomato", font = ("Helvetica",14))
        self.timeLabelTop.grid(row = 0, column = 3, columnspan = 3,
                               padx = (0, 70))
        
        self.callLabelTop = tk.Label(self.Topframe,bg = "black")
        self.callLabelTop.place(x=350, y=0)

        
        self.msgLabelTop = tk.Label(self.Topframe, bg = "black")
        self.msgLabelTop.place(x=390,y=0)


        self.signal = tk.Canvas(self.Topframe, width=self.bar_width,
                                height=self.bar_height, bg= "black",
                                highlightthickness=0, bd=0)
        self.signal.grid(row = 0, column = 7, sticky = "e")

        container = tk.Frame(self,height=800, width=480, bg = "black")
        container.pack(fill = 'both', expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        Icon()
        self.messageData=[]
        self.frames = {}
        for F in (HomeFrame, Menu1Frame, Menu2Frame, CallFrame,
                  CallIncomingFrame, CamFrame, MessageFrame, InboxBodyFrame,
                  InboxFrame, CreateSMSFrame,DeleteSMSFrame, StopwatchFrame,
                  SettingsFrame, GUIRotateFrame, CallSettingFrame,
                  CalendarFrame, AudioFrame, AboutFrame, SIMFrame, GalleryFrame,
                  CalculatorFrame, SensorFrame, PiFrame, InternetFrame,
                  ShutdownFrame, HDMIFrame, LogFrame, LocationFrame,
                  TemplateFrame):
            frame_name = F.__name__
            frame = F(parent = container, controller = self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("HomeFrame")
        self.logframe = self.get_frame("LogFrame")
        self.update_network()
        self.check_flags()

    def show_frame(self, frame_name):
        """
        This function raise the frame on Top

        Args:
            frame_name: Name of the Frame
        """

        global Gframename
        Gframename = frame_name
        frame = self.frames[frame_name]
        frame.tkraise()

    def get_frame(self, frame_name):
        """
        This function returns the address of given frame

        Args:
            frame_name: Name of the Frame

        Return:
            Address of frame_name
        """
        return self.frames[frame_name]

    def check_flags(self):
        """ This function handles incoming call, call disconnect and SMS """

        if phone.incomingCall == True:
            self.Fl_incoming = True
            self.retFrame = self.get_frame("CallIncomingFrame")
            self.retFrame.number.config(text = phone.callerID)
            self.show_frame("CallIncomingFrame")

        if phone.callConnected == True and self.Fl_Auto_Answer == True:
            self.Fl_Auto_Answer = False
            frame = self.get_frame("CallIncomingFrame")
            frame.call_connect()
            
        elif phone.callDisconnected and self.Fl_incoming:
            self.retFrame.Fl_incoming_call_start = False
            self.retFrame.timer.config(text="00:00:00")
            self.retFrame.hour = 0
            self.retFrame.min = 0
            self.retFrame.second = 0
            self.retFrame.connect.config(state = "normal")
            phone.callDisconnected = False
            self.Fl_incoming = False
            self.show_frame("HomeFrame")

        elif (phone.flag_newSMS):
            phone.flag_newSMS = False
            self.messageData.append(phone.messageList)
            self.retFrame = self.get_frame("InboxFrame")
            self.retFrame.update_inbox()
            self.msgLabelTop.configure(image = icons[26])
            self.Fl_newSMS = True
            phone.messageList = []

        else:
            pass
        self.after(1000, self.check_flags)

    def update_network(self):
        """ Update network and status bar after every 5 seconds"""
        if self.Fl_initialize == False and phone.alive == False:
            phone.connect()
            self.signal.config(bg="black")
        
        if self.Fl_initialize == False and phone.alive == True:
            self.networkName = phone.networkName()
            self.networkLabel.config(text = self.networkName)
            self.imei = int(phone.imei())
            self.Fl_initialize = True

        if self.Fl_initialize == True and phone.alive == False:
            self.networkLabel.config(text="No Power", fg="tomato")
            self.signal.config(bg="red4")
            self.Fl_initialize = False

        elif self.Fl_initialize == True:
            network = phone.signalStrength()
        
            if int(network) >= 2 and int(network) <= 9:
                signal = [1]
            elif int(network) >= 10 and int(network) <= 14:
                signal = [1, 2]
            elif int(network) >= 15 and int(network) <= 19:
                signal = [1, 2, 3]
            elif int(network) >= 20 and int(network) <= 24:
                signal = [1, 2, 3, 4]
            elif int(network) >= 25 and int(network) <= 30:
                signal = [1, 2, 3, 4, 5]
                
            y_stretch = 4
            y_gap = 1

            x_stretch = 2
            x_width = 5
            x_gap = 1
            for x, y in enumerate (signal):
              
                x0 = x * x_stretch + x * x_width + x_gap
                y0 = self.bar_height - (y * y_stretch + y_gap)
                x1 = x * x_stretch + x * x_width + x_width + x_gap
                y1 = self.bar_height - y_gap
              
                self.signal.create_rectangle(x0, y0, x1, y1, fill="OliveDrab1")

        self.after(5000, self.update_network)

    def call_log(self, logPath, data):
        """ This function make the call logs """
        if self.logframe.Fl_logs:
            
            file = open(logPath,"a")
            width = (1,15,14,22)
            data = ('\n', data, time.strftime('%H:%M:%S'),
                    time.strftime('%A  %d/%m/%Y'))
            number = "".join("%*s" % i for i in zip(width,data))
            file.write(number)
            file.close()

    def message_log(self, logPath, data):
        """ This function make the SMS logs """
        if self.logframe.Fl_logs:
            file = open(logPath,"a")
            file.write(data[0] + '\t\t')
            file.write(data[1] + '\n')
            file.write(data[2])
            file.write('\n\n\n')
            file.close()
        
###############################  HomeFrame  ####################################
class HomeFrame(tk.Frame):
    """ This class handles HomeFrame, Clock update and color change of box """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller
        self.index = 0
        
        self.COLOR = ['RoyalBlue1', 'gray60', 'violet', 'cyan2']

        self.canvas = tk.Canvas(self,bg="black",width = 480, height = 480,
                                highlightthickness=0,bd=0)
        self.circle = self.canvas.create_rectangle(99,140,370,350,
                                                   outline="tomato",width=7)     
        self.canvas.grid(row = 0, column = 0, rowspan = 3,columnspan = 3)
        
        for i in range(3):
            self.grid_rowconfigure(i, weight = 1)
            self.grid_columnconfigure(i, weight = 1)
        
        self.dateLabel = tk.Text(self,bg = "black", fg = "yellow" ,height = 8,
                                 width = 25, bd  = 0, highlightthickness = 0,
                                 font = 20)
        self.dateLabel.grid(row = 1, column = 1, padx = (7,0), pady = (13,0))

        self.call = tk.Button(self, text = "Call", image=icons[4],bg = "black",
                              fg = "white", font = ("bold", 15), bd = 0,
                              highlightbackground = "black", compound="top",
                              activebackground = "black",
                              activeforeground = "white",
                              command = lambda:
                              controller.show_frame("CallFrame"))
        self.call.grid(row = 3, column = 0, pady=(0,5))

        self.menu = tk.Button(self, image=icons[22],text = "Menu",bg = "black",
                              fg = "white",font = ("bold", 15), bd = 0,
                              highlightbackground = "black",compound="top",
                              activebackground = "black",
                              activeforeground = "white",
                              command = lambda:
                              controller.show_frame("Menu1Frame"))
        self.menu.grid(row=3, column = 1,pady=(0,5))

        self.camera = tk.Button(self,image=icons[8], text = "Camera",
                                bg = "black", fg = "white", font = ("bold", 15),
                                bd = 0, highlightbackground = "black",
                                compound="top", activebackground = "black",
                                activeforeground = "white",
                                command =lambda:
                                controller.show_frame("CamFrame"))
        self.camera.grid(row = 3, column = 2, pady=(0,5))

        self.update_Clock()
        self.update_color()

    def update_Clock(self):
        '''Updates the clock per second ''' 
        timeNow = time.strftime('%H:%M:%S')
        if Gframename != "HomeFrame":
            self.controller.timeLabelTop.configure(text= timeNow)
        else:
            self.controller.timeLabelTop.configure(text="")

        dateNow = time.strftime('%A\n %d/%m/%Y')
        self.dateLabel.delete(1.0, "end")
        self.dateLabel.insert(1.0, "\n"+timeNow+"\n\n"+dateNow)
        self.dateLabel.tag_add("time", "2.0", "2.12")
        self.dateLabel.tag_config("time" ,foreground = "tomato",
                                  background = "black",font = ("bold",30),
                                  justify = "center")
        self.dateLabel.tag_add("date", "3.0", "end")
        self.dateLabel.tag_config("date" ,justify = "center",
                                  foreground = "gold", font = ("bold",15))
                
        self.after(1000, self.update_Clock)

    def update_color(self):
        self.canvas.itemconfig(self.circle, outline=self.COLOR[self.index])
        self.index += 1
        if self.index >= len(self.COLOR):
            self.index = 0
        self.after(10000, self.update_color)
        
############################  Menu1Frame  ######################################
class Menu1Frame(tk.Frame):
    """ This class handle Menu1 Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        BUTTON = [# Text          Image       Frame           Row Col
                  ("Call",       icons[4],  "CallFrame"      , 0, 0),
                  ("Message",    icons[17], "MessageFrame"   , 0, 1),
                  ("Camera",     icons[8],  "CamFrame"       , 0, 2),
                  ("Internet",   icons[19], "InternetFrame"  , 1, 0),
                  ("Gallery",    icons[13], "GalleryFrame"   , 1, 1),
                  ("Settings",   icons[32], "SettingsFrame"  , 1, 2),
                  ("Stopwatch",  icons[38], "StopwatchFrame" , 2, 0),
                  ("Location",      icons[14], "LocationFrame"     , 2, 1),
                  ("Calculator", icons[2],  "CalculatorFrame", 2, 2),
                  ("<<",         None,      "HomeFrame"      , 3, 0),
                  (None,         icons[16], "HomeFrame"      , 3, 1),
                  (">>",         None,      "Menu2Frame"     , 3, 2),
                   ]
        
        for i in range(4):
            self.grid_rowconfigure(i, weight = 1)
            if i <= 2:
                self.grid_columnconfigure(i, weight = 1)
            
        for b in range(len(BUTTON)):
            cmd = lambda x=BUTTON[b][2]: controller.show_frame(x)
            tk.Button(self, text = BUTTON[b][0],bg = "white", fg = "black",
                      font = ("Helvetica", 15), bd = 0,
                      highlightbackground = "white",activebackground = "white",
                      activeforeground = "black", image = BUTTON[b][1],
                      compound = 'top',
                      command = cmd).grid(row = BUTTON[b][3],
                                          column = BUTTON[b][4],
                                          sticky ="nsew",ipadx = 0, ipady = 0) 

#################################  Menu2Frame  #################################
class Menu2Frame(tk.Frame):
    """ This class handle Menu2 Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="white")

        BUTTON = [# Text          Image       Frame        Row Col
                  ("Audio",     icons[1],  "AudioFrame",    0, 0),
                  ("Sensor",    icons[50], "SensorFrame",   0, 1),
                  ("Inside Pi", icons[18],  "PiFrame",      0, 2),
                  ("Calendar",  icons[3],  "CalendarFrame", 1, 0),
                  ("SIM Info",  icons[33], "SIMFrame",      1, 1),
                  ("About Us",  icons[0],  "AboutFrame",    1, 2),
                  ("Your Apps",  icons[45], "TemplateFrame", 2, 0),
                  ("<<",        None,      "Menu1Frame",    3, 0),
                  (None,        icons[16], "HomeFrame",     3, 1),
                  (">>",        None,      "Menu2Frame",    3, 2),
                   ]
        
        for i in range(4):
            self.grid_rowconfigure(i, weight = 1)
            if i <= 2:
                self.grid_columnconfigure(i, weight = 1)
            
        for b in range(len(BUTTON)):
            cmd = lambda x=BUTTON[b][2]: controller.show_frame(x)
            tk.Button(self, text = BUTTON[b][0],bg = "white", fg = "black",
                      font = ("Helvetica", 15), bd = 0,
                      highlightbackground = "white",activebackground = "white",
                      activeforeground = "black", image = BUTTON[b][1],
                      compound = 'top',
                      command = cmd).grid(row = BUTTON[b][3],
                                         column = BUTTON[b][4],
                                         sticky ="nsew" ,ipadx = 0, ipady = 0)
            
##############################  CallFrame  #####################################
class CallFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller
        self.buttons = []
        BUTTON = [# text  anchor row col
                  ("1",   "e",   1,  0), ("2", "center", 1, 1), ("3", "w", 1, 2),
                  ("4",   "e",   2,  0), ("5", "center", 2, 1), ("6", "w", 2, 2),
                  ("7",   "e",   3,  0), ("8", "center", 3, 1), ("9", "w", 3, 2),
                  ("*",   "e",   4,  0), ("0", "center", 4, 1), ("#", "w", 4, 2)]

        for i in range(6):
            self.grid_rowconfigure(i, weight = 1)
            if i <= 2:
                self.grid_columnconfigure(i, weight = 1)

        self.diallednumber = tk.Entry(self, font = ('bold', 30),
                                      justify="right",fg='RoyalBlue1')
        self.diallednumber.grid(row = 0, column = 0, columnspan =3,
                                sticky = "nsew")

        for b in range(12):
            cmd = lambda x=BUTTON[b][0]: self.dial_Entry(x)
            self.buttons.append(tk.Button(self,text=BUTTON[b][0],
                                          font=('bold',20),
                                          highlightbackground="black",
                                          activebackground = "black",
                                          anchor = BUTTON[b][1],
                                          activeforeground="white",
                                          bg="black",fg="white",bd=0,
                                          command = cmd))
            self.buttons[b].grid(row=BUTTON[b][2],column=BUTTON[b][3],
                                 sticky="nsew")
        
        self.buttons.append(tk.Button(self, image = icons[5],bd=0,
                                      bg = "black", fg = "white",
                                      highlightbackground = "black",
                                      activebackground = "black",
                                      activeforeground = "white",
                                      command = self.outgoing_Call))
        self.buttons[-1].grid(row = 5, column = 0, sticky ="nsew", pady=(0,10))

        self.buttons.append(tk.Button(self, image = icons[16],bd=0,bg = "black",
                                      fg = "white",
                                      highlightbackground = "black",
                                      activebackground = "black",
                                      activeforeground = "white",
                                      command = lambda:
                                      controller.show_frame("HomeFrame")))
        self.buttons[-1].grid(row = 5, column = 1, sticky ="nsew", pady=(0,10))

        self.buttons.append(tk.Button(self, image = icons[11],bd=0,bg = "black",
                                      fg = "white",highlightbackground = "black",
                                      activebackground = "black",
                                      activeforeground = "white",
                                      command = self.dial_Delete))
        self.buttons[-1].grid(row = 5, column = 2, sticky ="nsew", pady=(0,10))
    
   
    def dial_Entry(self, args):
        ''' Enables the entry widget to get values from the dialpad '''
        self.diallednumber.insert("end", args)
        
    def dial_Delete(self):
        ''' deletes a single character in the dialler entry '''
        self.txt=self.diallednumber.get()[:-1]
        self.diallednumber.delete(0,"end")
        self.diallednumber.insert(0,self.txt)

    def outgoing_Call(self):
        """ This function handle outgoing call and logging of outgoing call """
        global Fl_outgoing_Call
        if len(self.diallednumber.get()):
            self.number = self.diallednumber.get()
            self.diallednumber.delete(0,"end")
            self.diallednumber.grid_remove()
        
            for index in range(len(self.buttons)):
                self.buttons[index].grid_remove()
            tk.Frame.config(self, bg="white")
            phone.dial(self.number)

            self.controller.callLabelTop.config(image = icons[52])

            self.outgoingcall = tk.Label(self, text = "Outgoing Call",
                                         font = ("bold",25), fg = "tomato",
                                         bg = "white")
            self.outgoingcall.grid(row = 0, column = 0, columnspan = 7,
                                   sticky = "s")

            self.dialnumber = tk.Label(self, text = self.number,
                                       font = ("normal",20), fg = "gray30",
                                       bg = "white")
            self.dialnumber.grid(row = 1, column = 0, columnspan = 7,padx=50,
                                 pady=20, sticky = "n")
            
            self.hangup = tk.Button(self, image = icons[6],bd=0,bg = "white",
                                    fg = "black",highlightbackground = "white",
                                    activebackground = "white",
                                    activeforeground = "white",
                                    command = self.call_Hangup)
            self.hangup.grid(row = 3, column = 0, pady = (0, 20))

            self.headfone = tk.Button(self,image = icons[15],bd=0, bg = "white",
                                      fg = "black",highlightbackground = "white",
                                      activebackground = "white",
                                      activeforeground = "white",
                                      command = lambda: self.audio_mode(1))
            self.headfone.grid(row = 3, column = 1, pady = (0, 20))

            self.speaker = tk.Button(self, image = icons[34],bd=0, bg = "white",
                                     fg = "black",highlightbackground = "white",
                                     activebackground = "white",
                                     activeforeground = "white",
                                     command = lambda :self.audio_mode(2))
            self.speaker.grid(row = 3, column = 2,pady = (0, 20))

            self.controller.call_log(path + '/Logs/Call/Outgoing.txt', self.number)

            self.label = tk.Label(self, text = "", fg = "white", bg = "white",
                                  font=("Helvetica", 15))
            self.label.place(x = 170, y =600 )

    def audio_mode(self, args):
        """ Handle audio mode selection during outgoing call """
        if args == 1:
            self.label.place(x = 170, y =600 )
            phone.jackMode()
            self.label.config(text = "Headphone Mode", fg = "gold3")
            self.label.after(1000, self.label.place_forget)
        else:
            self.label.place(x = 170, y =600 )
            phone.speakerMode()
            self.label.config(text = "Speaker Mode", fg = "green")
            self.label.after(1000, self.label.place_forget)
        
    def call_Hangup(self):
        """ Disconnect the Incoming Call and back to HomeFrame """
        phone.hangup()
        self.controller.callLabelTop.config(image = "")
        Fl_outgoing_Call = False
        self.outgoingcall.grid_forget()
        self.dialnumber.grid_forget()
        self.hangup.grid_forget()
        self.headfone.grid_forget()
        self.speaker.grid_forget()
        self.label.grid_forget()
        tk.Frame.config(self, bg="black")

        self.diallednumber.grid()
        for index in range(len(self.buttons)):
            self.buttons[index].grid()
            
        self.controller.show_frame("HomeFrame")

################################  CallIncomingFrame  ###########################
class CallIncomingFrame(tk.Frame):
    """ This class handle the Incoming Calls and Logging of Incoming Call """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller

        self.hour = 00
        self.minute = 00
        self.second = 00
        self.Fl_incoming_call_start = False
            
        for j in range (5):
            self.grid_columnconfigure(j, weight = 1)
            if j <= 4:
                self.grid_rowconfigure(j, weight = 1)

        self.incominglabel = tk.Label(self, text = "Incoming Call", fg = "gold3",
                                      bg = "black", font = ("bold",20))
        self.incominglabel.grid(row = 0, column = 0, columnspan = 5)

        self.number = tk.Label(self, text = "",fg = "red4", bg = "black" ,
                               font = ("bold", 22))
        self.number.grid(row = 1, column = 0, columnspan = 5)

        self.timer = tk.Label(self, text = "00:00:00", font = ("bold",18),
                              bg = "black", fg = "white")
        self.timer.grid(row = 2, column = 0, columnspan =5)

        self.hangup = tk.Button(self, image = icons[6],bg = "black",fg = "black",
                                bd = 0, highlightbackground = "black",
                                activebackground = "black",
                                command = self.call_hangup)
        self.hangup.grid(row = 4, column = 4)

        self.headfone = tk.Button(self,image = icons[15],bd=0, bg = "black",
                                  fg = "black",highlightbackground = "black",
                                  activebackground = "black",
                                  activeforeground = "black",
                                  command = lambda: self.audio_mode(1))
        self.headfone.grid(row = 4, column = 1)

        self.speaker = tk.Button(self, image = icons[34],bd=0, bg = "black",
                                 fg = "black",highlightbackground = "black",
                                 activebackground = "black",
                                 activeforeground = "black",
                                 command = lambda :self.audio_mode(2))
        self.speaker.grid(row = 4, column = 3)

        self.connect = tk.Button(self, image = icons[51],bg = "black",
                                 fg = "black", bd = 0,
                                 highlightbackground = "black",
                                 activebackground = "black",
                                 command = self.call_connect)
        self.connect.grid(row = 4, column = 0)

        self.label = tk.Label(self, text = "", fg = "black", bg = "black",
                              font=("Helvetica", 15))
        self.label.place(x = 170, y =600 )

    def audio_mode(self, args):
        """ Handle audio mode selection during Incoming Call """
        if args == 1:
            self.label.place(x = 170, y =600 )
            phone.jackMode()
            self.label.config(text = "Headphone Mode", fg = "gold3")
            self.label.after(1000, self.label.place_forget)
        else:
            self.label.place(x = 170, y =600 )
            phone.speakerMode()
            self.label.config(text = "Speaker Mode", fg = "Deep sky blue")
            self.label.after(1000, self.label.place_forget)
        
    def call_hangup(self):
        """ Disconnect the Incoming Call and back to HomeFrame """
        phone.hangup()
        phone.incomingCall = False
        self.Fl_incoming_call_start = False
        self.timer.config(text="00:00:00")
        self.hour = 00
        self.minute = 00
        self.second = 00
        self.connect.config(state = "normal")
        self.controller.show_frame("HomeFrame")

    def call_connect(self):
        """ Function connec the incoming call  and make log """
        self.Fl_incoming_call_start = True
        self.connect.config(state = "disable")
        phone.connectCall()
        self.call_time_counter()
        self.controller.call_log(path+'/Logs/Call/Incoming.txt',phone.callerID)

    def call_time_counter(self):
        """ Call time counter """
        if(self.Fl_incoming_call_start):
            self.timer.configure(text="%02d:%02d:%02d"\
                                 %(self.hour,self.minute, self.second))
            self.second=self.second+1
            if self.second == 60:
                self.minute=self.minute+1 ; self.second = 0
            elif self.minute == 60:
                self.hour = self.hour + 1; self.minute = 0

            self.after(999, self.call_time_counter)
        else:
            self.hour = 00
            self.minute = 00
            self.second = 00
        
#############################  MessageFrame  ###################################
class MessageFrame(tk.Frame):
    """ This class handle Message Frame and makes buttons """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="white")
        self.controller = controller

        self.grid_columnconfigure(0, weight = 1)
        for i in range(6):
            self.grid_rowconfigure(i, weight = 1)

        BUTTON = [# Text            Image       Frame          Row Col
                  ("Create New",   icons[20], "CreateSMSFrame", 0, 0),
                  ("Inbox",        icons[23], "InboxFrame",     1, 0),
                  ("Sent Message", icons[25], "PiFrame",        2, 0),
                  ("Delete",       icons[21], "DeleteSMSFrame", 3, 0),
                   ]
            
        for b in range(len(BUTTON)):
            cmd = lambda x=BUTTON[b][2]: controller.show_frame(x)
            tk.Button(self,text=BUTTON[b][0],bg="white", fg = "black",bd = 0,\
                      highlightbackground = "white", activebackground = "white",\
                      activeforeground="black",image=BUTTON[b][1],
                      compound = 'left',anchor = "w",font=("Helvetica", 15),
                      command = cmd).grid(row = BUTTON[b][3],
                                          column=BUTTON[b][4], sticky ="nsew") 
       
        home=tk.Button(self,bg="white",fg="white",bd=0,
                                   highlightbackground="white",
                                   activebackground="white",
                                   activeforeground="black",
                                   command=lambda:
                                   controller.show_frame("HomeFrame"),
                                   image=icons[16])
        home.grid(row=5,column=0,sticky="new")

################################  InboxFrame  ##################################
class InboxFrame(tk.Frame):
    """ This class handle Message Frame and makes buttons """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self,bg="black")
        self.controller = controller
        self.canvas = tk.Canvas(self, bg = "black", borderwidth = 0)
        canvas = self.canvas
        
        self.frame = tk.Frame(canvas, bg = "black")
        self.vsb = tk.Scrollbar(self, orient = "vertical",
                                command = canvas.yview, width = 20)
        canvas.configure(yscrollcommand = self.vsb.set)

        self.vsb.pack(side = "right", fill = "y")
        canvas.pack(side = "left", fill = "both", expand = True)
        canvas.create_window((0,0), window = self.frame, width = 480,
                             anchor = "nw")

        self.frame.bind("<Configure>", lambda event, canvas = canvas:
                        self.onFrameConfigure(canvas))
        self.index = 0

        self.incomingSMS = []

        self.frame.grid_columnconfigure(0, weight = 1)
        
        self.home = tk.Button(self.frame,image=icons[16],bg="black",
                              anchor="center",bd = 0,
                              highlightbackground = "black",
                              activeforeground = "black",
                              activebackground = "black",
                              command = lambda:
                              controller.show_frame("HomeFrame"))
        self.home.grid(row = self.index+1, column = 0)
        
        self.textframe = self.controller.get_frame("InboxBodyFrame")


    def onFrameConfigure(self, canvas):
        """ Scrolling of messages """
        canvas.configure(scrollregion = canvas.bbox("all"))

    def update_inbox(self):
        """ Update inbox list and make log """

        self.controller.message_log(path + '/Logs/Message/Inbox.txt',
                                    self.controller.messageData[-1])

        self.incomingSMS.append(tk.Button(self.frame,font = ("Helvetica", 15),
                                          bg = "gold2",fg = "black",
                                          activeforeground = "white",
                                          activebackground = "black",
                                          text = self.controller.messageData\
                                          [self.index][0]+"\t  "+\
                                          self.controller.messageData\
                                          [self.index][1],
                                          command = lambda index=self.index:
                                          self.textframe.opne_sms(index)))
        self.incomingSMS[-1].grid(row = self.index, column = 0, sticky = "nsew")
            
        self.home.grid(row = self.index+1, column = 0, sticky = "nsew")
        self.index = self.index+1

################################  InboxBodyFrame  ##############################
class InboxBodyFrame(tk.Frame):
    """ This class handle reading of Inbox SMS """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self,bg="black")
        self.controller = controller
        self.index = 0
        
        for i in range(4):
            self.grid_rowconfigure(i, weight = 1)
            if i < 3:
                self.grid_columnconfigure(i, weight = 1)
        
    def opne_sms(self, args):
        """ Open message text, Number and date-time """
        self.controller.show_frame("InboxBodyFrame")
        
        inbox = self.controller.get_frame("InboxFrame")
        inbox.incomingSMS[args].config(fg = "white", bg = "black")
    
        
        self.numberSMS = tk.Label(self, text = self.controller.messageData[args][0],\
                                  bg = "black", fg= "DarkGoldenrod3", font = ("bold",18))
        self.numberSMS.grid(row = 0, column = 0,columnspan = 3,sticky = "nsew")

        self.datetime=tk.Label(self,text=self.controller.messageData[args][1],
                               bg = "black", fg= "tomato", font = ("bold",14))
        self.datetime.grid(row = 1, column = 0,columnspan = 3,sticky = "nsew")
        
        self.bodySMS = tk.Text(self,bg = "white", fg= "black", height = 10,
                               width = 35,font = ("Helvetica", 10))
        self.bodySMS.delete(1.0, "end")
        self.bodySMS.insert(1.0, self.controller.messageData[args][2])
        self.bodySMS.grid(row = 2, column = 0, columnspan = 3,
                          padx=40, sticky = "nsew")

        self.reply = tk.Button(self,text = "Reply",font= ("bold", 15),
                               bg = "white",bd = 0,highlightbackground="white",
                               activeforeground = "black",
                               activebackground = "white",command=lambda
                               args=args: self.reply_msg(args))
        self.reply.grid(row = 3, column = 1)

        self.back = tk.Button(self, bg="black",bd=0,highlightbackground="black",
                              activeforeground="black",activebackground="black",
                              image = icons[30], command = lambda :
                              self.controller.show_frame("InboxFrame"))
        self.back.grid(row = 3, column = 0)

        self.backtohome = tk.Button(self, image = icons[16], bg="black",bd = 0,
                                    highlightbackground = "black",
                                    activeforeground = "black",
                                    activebackground = "black",
                                    command = lambda:
                                    self.controller.show_frame("HomeFrame"))
        self.backtohome.grid(row = 3, column = 2)

        self.controller.msgLabelTop.configure(image = "")

    def reply_msg(self, args):
        reply = self.controller.get_frame("CreateSMSFrame")
        reply.recipient.insert("end", self.controller.messageData[args][0])
        self.controller.show_frame("CreateSMSFrame")

##################################  CreateSMSFrame  ############################
class CreateSMSFrame(tk.Frame):
    """ This class create new SMS and make qwerty keypad """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.buttonData = []
        self.buttonCharData = []
        self.buttonCapsData = []
        self._buttoncount = 0
        self._buttonCharcount = 0

        self.letter = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                       "a", "s", "d", "f", "g", "h", "j", "k", "l", ":",
                       ".", "z", "x", "c", "v", "b", "n", "m", "$", ","]

        
        self.letterCaps = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
                           "A", "S", "D", "F", "G", "H", "J", "K", "L", ":",
                           ".", "Z", "X", "C", "V", "B", "N", "M", "$", ","]

        self.specialChar = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                            "~", "!", "@", "#", "%", "^", "&", "(", ")", ":",
                            '"', "+", "=", "/", ";", "[", "]", "?", "<", ">"]

        for j in range(10):
            self.grid_columnconfigure(j, weight = 1)
            if j <= 5:
                self.grid_rowconfigure(j, weight = 1)
        
        self.Label = tk.Label(self, font = ('bold', 18),text = "To: ")
        self.Label.grid(row = 0, column = 0)

        self.recipient = tk.Entry(self, justify="right",font = ('bold', 18),
                                  width = 25)
        self.recipient.grid(row = 0, column = 1, columnspan = 6,sticky = "nsew")
        self.recipient.bind("<FocusIn>", self.remember_Focus)
        self.recipient.focus()

        self.messageSend = tk.Button(self, text = "SEND",font = ('bold', 20),
                                     fg = "gold",bg = "green4",
                                     command = self.send_Message)
        self.messageSend.grid(row = 0, column = 8, columnspan = 2,
                              sticky = "nsew")

        self.messageBody = tk.Text(self,font = ('Helvetica', 16),
                                   height = 15, width = 35)
        self.messageBody.grid(row = 1, column = 0, columnspan = 10,
                              sticky = "nsew")
        self.messageBody.bind("<FocusIn>", self.remember_Focus)
        c = 0
        r = 2
        for k in range(30):
            
            self.buttonCharData.append(0)
            self.buttonCapsData.append(0)
            self.buttonData.append(0)
            
            self.buttonCharData[k] = tk.Button(self,font = ('Helvetica', 14),
                                               text = self.specialChar[k],
                                               command = lambda k=k:
                                               self.messageEntry
                                               (self.specialChar[k]))
            self.buttonCapsData[k] = tk.Button(self, font = ('Helvetica',14),
                                               text = self.letterCaps[k],
                                               command = lambda k=k:
                                               self.messageEntry
                                               (self.letterCaps[k]))
            self.buttonData[k] = tk.Button(self, font=('Helvetica',14),
                                           text=self.letter[k],command=lambda
                                           k=k:self.messageEntry(self.letter[k]))
            
            self.buttonCharData[k].grid(row = r, column = c, sticky = "nsew")
            self.buttonCapsData[k].grid(row = r , column = c, sticky = "nsew")
            self.buttonData[k].grid(row = r , column = c, sticky = "nsew")
            
            c = c + 1
            if(c == 10):
                r = r + 1
                c = 0

        home = tk.Button(self, text = "HOME", fg = "Deep Sky Blue",font=("bold",10),
                         command = lambda: controller.show_frame("HomeFrame"))
        home.grid(row = 5, column = 0, columnspan = 2 , sticky = "nsew")
        
        capital_char = tk.Button(self, text = "UP",font=("bold",10),
                                 command = self.capitalLetters)
        capital_char.grid(row = 5, column = 2 ,sticky = "nsew")

        space = tk.Button(self, text = "space", bg = "gray60",font=("bold",10),
                          command = lambda:self.messageEntry(" "))
        space.grid(row = 5, column = 3, columnspan = 4, sticky = "nsew")

        symbols = tk.Button(self, text = "SYM",font=("bold",10),
                            command = self.specialCharacters)
        symbols.grid(row = 5, column = 7,sticky = "nsew")

        delete = tk.Button(self, text = "DEL",fg="red4",font=("bold",10),
                           command = self.single_Char_Delete)
        delete.grid(row = 5, column = 8, columnspan = 2 ,sticky = "nsew")

  
    def remember_Focus(self,event):
        """ Keeps the focussed widget global for the keyboard to input values in """
        self.focused_entry = event.widget

    def single_Char_Delete(self):
        """ Deletes a single character in the focussed widget """
        if(self.focused_entry == self.recipient):
            self.num=self.recipient.get()[:-1]
            self.recipient.delete(0,"end")
            self.recipient.insert(0,self.num)
        else:
            self.messageBody.delete("%s-1c"% 'insert', 'insert')
         
    def messageEntry(self, args):
        """ Message Entry """
        self.focused_entry.insert("end", args)
     
    def specialCharacters(self):
        """ Enables numbers(0-9) and special characters on the keyboard """
        self._buttonCharcount = self._buttonCharcount+1
        if(self._buttonCharcount == 1):
            for i in range(30):
                self.buttonData[i].grid_remove()
                self.buttonCapsData[i].grid_remove()
                self.buttonCharData[i].grid()

        else:
            for j in range(30):
                self.buttonCharData[j].grid_remove()
                self.buttonData[j].grid()
                self._buttonCharcount = 0
            
    def capitalLetters(self):
        """ Enables Capital Letters on the keyboard """ 
        self._buttoncount = self._buttoncount+1
        if(self._buttoncount == 1):
            for i in range(30):
                self.buttonData[i].grid_remove()
                self.buttonCapsData[i].grid()
                
        else:
            for j in range(30):
                self.buttonCapsData[j].grid_remove()
                self.buttonData[j].grid()
                self._buttoncount = 0

 
    def send_Message(self):
        """ This fucntion is used for Sending SMS """
        label = tk.Label(self)
        label.grid(row = 0, column = 7)
        if self.recipient.get():
            status = phone.sendSMS(self.recipient.get(),
                                   self.messageBody.get(1.0, "end") )
            if status[-1] == 'OK\r\n':
                self.recipient.delete(0,"end")
                self.messageBody.delete(1.0, "end")
                label.config(text = "Sent")
                label.after(1000, label.grid_forget)
            else:
                label.config(text = "Error", bg = "red")
                label.after(1000, label.grid_forget)
        else:
            pass
        
##################################  DeleteSMSFrame  ############################
class DeleteSMSFrame(tk.Frame):
    """ This class Delete SMS from Module """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self,bg="black")
        self.controller = controller

        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=2:
                self.grid_columnconfigure(j, weight = 1)
           

        self.warningLabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text = "Selecting this deletes "
                                     "messages from \nyour GSM Module only",
                                     font = ("Helvetica", 20))
        self.warningLabel.grid(row = 0, column = 0, columnspan = 3)
        tk.Label(self, text = "Press OK to confirm", fg = "yellow",
                 bg = "black",
                 font = ("Helvetica", 20)).grid(row = 1, column = 1)
        
        ok = tk.Button(self, text = "OK" ,fg = "yellow",image = icons[21],
                       font = ("Helvetica", 15), anchor = "center",
                       highlightbackground = "white", bg = "black",
                       activebackground = "black",activeforeground = "white",
                       compound = "top", command = self.deletesms)
        ok.grid(row = 2, column = 1)

        back = tk.Button(self, text = "Back",image = icons[30],
                         bd = 0,highlightbackground = "black",
                         bg = "black", activebackground = "black",
                         anchor = "center", command = lambda :
                         self.controller.show_frame("MessageFrame"))
        back.grid(row = 3, column = 0)

        tk.Button(self, text = "Go Home", image = icons[16],
                  anchor = "center",bd = 0,highlightbackground = "black",
                  bg = "black", activebackground = "black",
                  command = lambda:
                  controller.show_frame("HomeFrame")).grid(row = 3, column = 2)

    def deletesms(self):
        phone.deleteSMS()
        self.controller.msgLabelTop.configure(image = "")
        label = tk.Label(self, text =" SIM messages Deleted", fg = "black",
                         bg = "yellow", font=("Helvetica", 14))
        label.grid(row = 3, column = 1)
        label.after(2000, label.grid_forget)
    
##################################  CamFrame  ##################################     
class CamFrame(tk.Frame):
    """ This class handle Camera """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")
                
        self.Fl_VideoRecord = False
        
        tk.Button(self,text="Photo", bg = "black", fg = "white", bd = 0,
                  font=("Helvetica",16), highlightbackground = "black",
                  activebackground = "black",activeforeground = "white",
                  image = icons[9], compound="top", command = lambda:
                  self.startPreview("Picture")).place(x = 140, y = 100)
        
        tk.Button(self,text="Video", bg = "black", fg = "white", bd = 0,
                  font=("Helvetica",16), highlightbackground = "black",
                  activebackground = "black",
                  activeforeground = "white", image = icons[10],
                  compound="top", command = lambda:
                  self.startPreview("Video")).place(x = 140, y = 350)
        
        self.home = tk.Button(self, bg = "black", fg = "black", bd = 0,
                              highlightbackground = "black",image = icons[16],
                              activebackground = "black",
                              activeforeground = "black",command = lambda:
                              controller.show_frame("HomeFrame"))
        self.home.place(x=10,y=700)

        self.back = tk.Button(self,text = "Home", bg = "black", fg = "black",
                              bd = 0, image = icons[30],
                              highlightbackground = "black",
                              activebackground = "black",
                              activeforeground = "black",state="disable",
                              command = self.camBack)
        self.back.place(x=410,y=700)

        self.click = tk.Button(self, image=icons[36],bg = "black", fg = "black",
                               bd = 0,font=("bold",12),
                               highlightbackground = "black",
                               activebackground = "black",
                               activeforeground = "black",compound="center",
                               state="disable", command = self.camClick)
        self.click.place(x=210,y=700)

    def startPreview(self, arg):
        """ Start Preview of Camera """
        self.cameraMode = arg
        label = tk.Label(self, text="",font=10, bg='black')
        label.place(x=140, y=650)

        response = subprocess.check_output(["sudo","vcgencmd","get_camera"])
        
        if(response == b'supported=1 detected=1\n'):
            self.camera = picamera.PiCamera()
            self.back.config(state="normal")
            self.click.config(state="normal")
            
            if arg == "Picture":
                self.click.config(text="Photo")
            else:
                self.click.config(text="Video")
                
            self.camera.preview_fullscreen=False
            self.camera.preview_window=(400, 260, 730, 480)
            self.camera.resolution=(800,480)
            self.camera.start_preview()
            self.home.config(state="disable")
            
        elif(response == b'supported=0 detected=0\n'):
            label.config(text="Error: Camera is not enabled", bg="yellow")
            label.after(4000, label.place_forget)
        else:
            label.config(text="Error: Camera is not connected properly",
                         bg="yellow")
            label.after(3000, label.place_forget)
            
    def camClick(self):
        """ Click Photos and Videos """
        if(self.cameraMode == "Picture"):
            self.camera.capture(path + '/Gallery/Photos/' + 'img_' +
                                time.strftime('%d%m%Y_')+time.strftime('%H%M%S')
                                + '.jpg')
        elif (self.cameraMode == "Video") and self.Fl_VideoRecord == False:
            self.click.config(text="Record", fg="red")
            self.back.config(state="disable")
            self.Fl_VideoRecord = True
            self.camera.start_recording(path + '/Gallery/Videos/' + 'vid_' +
                                        time.strftime('%d%m%Y_')+
                                        time.strftime('%H%M%S') + '.h264')
        elif self.Fl_VideoRecord == True:
            self.Fl_VideoRecord = False
            self.cameraMode = None
            self.camera.stop_recording()
            self.camera.stop_preview()
            self.camera.close()
            self.click.config(text="",fg="black")
            self.back.config(state="disable")
            self.click.config(state="disable")
            self.home.config(state="normal")
                
    def camBack(self):
        """ Back to Frame """
        self.camera.stop_preview()
        self.camera.close()
        self.click.config(text="",fg="black")
        self.back.config(state="disable")
        self.click.config(state="disable")
        self.home.config(state="normal")

#################################  InternetFrame  ##############################
class InternetFrame(tk.Frame):
    """ This class handle Internet and make PPP connection """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")

        self.buttonData = []
        self.buttonCharData = []
        self.buttonCapsData = []
        self._buttoncount = 0
        self._buttonCharcount = 0

        self.letter = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                       "a", "s", "d", "f", "g", "h", "j", "k", "l", ":",
                       ".", "z", "x", "c", "v", "b", "n", "m", "$", ","]

        
        self.letterCaps = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
                           "A", "S", "D", "F", "G", "H", "J", "K", "L", ":",
                           ".", "Z", "X", "C", "V", "B", "N", "M", "$", ","]

        self.specialChar = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                            "~", "!", "@", "#", "%", "^", "&", "(", ")", ":",
                            '"', "+", "=", "/", ";", "[", "]", "?", "<",">"]

        for j in range(10):
            self.columnconfigure(j, weight = 1)
            if j <= 6:
                self.rowconfigure(j, weight = 1)
        
        Label = tk.Label(self, font = ('bold', 18),text = "APN : ",
                         bg = "black", fg = "deep sky blue")
        Label.grid(row = 0, column = 0, columnspan = 2)

        self.APN = tk.Entry(self,font = ("Helvetica", 18), width = 25)
        self.APN.grid(row = 0, column = 2, columnspan = 6)
        self.APN.bind("<FocusIn>", self.remember_Focus)
        self.APN.focus()

        Label = tk.Label(self, font = ('bold', 18),text = " PORT : ",
                         bg = "black",  fg = "deep sky blue")
        Label.grid(row = 1, column = 0, columnspan = 2, pady = 20, padx = 5)

        self.Port = tk.Entry(self,font = ("Helvetica", 18), width = 25)
        self.Port.grid(row = 1, column = 2, columnspan = 6)
        self.Port.bind("<FocusIn>", self.remember_Focus)
        self.Port.focus()

        self.connect = tk.Button(self, text = "Connect",font=("Helvetica", 14),
                                 image = icons[19], compound = "top",
                                 fg = "green", command = self.connect)
        self.connect.grid(row = 0, column = 8, columnspan = 2, sticky = "nsew", padx = 20)

        self.disconnect = tk.Button(self, text = "Disconnect",
                                    font=("Helvetica", 14), image = icons[19],
                                    compound = "top", fg = "red",
                                    command = self.disconnect)
        self.disconnect.grid(row = 1, column = 8, columnspan = 2,
                             sticky = "nsew", padx = 20,pady = (5,0))

        self.status = tk.Button(self, text = "Check Status",
                                font=("Helvetica", 12),
                                command = self.check_status)
        self.status.grid(row = 2, column = 8, columnspan = 2,
                         sticky = "nsew", pady = 5, padx = 20)

        c = 0
        r = 3
        for k in range(30):
            self.buttonData.append(0)
            self.buttonCharData.append(0)
            self.buttonCapsData.append(0)

            
            self.buttonCharData[k] = tk.Button(self,font = 1,
                                               text = self.specialChar[k],
                                               command = lambda k=k:
                                               self.messageEntry
                                               (self.specialChar[k]))
            self.buttonCapsData[k] = tk.Button(self, font = 1,
                                               text = self.letterCaps[k],
                                               command = lambda k=k:
                                               self.messageEntry
                                               (self.letterCaps[k]))
            self.buttonData[k] = tk.Button(self, font = 1,
                                           text = self.letter[k],
                                           command = lambda k=k:
                                           self.messageEntry(self.letter[k]))

            self.buttonData[k].grid(row = r , column = c, sticky = "nsew")
            self.buttonCharData[k].grid(row = r, column = c, sticky = "nsew")
            self.buttonCapsData[k].grid(row = r , column = c, sticky = "nsew")
            
            c = c + 1
            if(c == 10):
                r = r + 1
                c = 0

        home = tk.Button(self, text = "HOME", fg = "red4", command = lambda:
                         controller.show_frame("HomeFrame"))
        home.grid(row = 6, column = 0, columnspan = 2 , sticky = "nsew")
        
        capital_char = tk.Button(self, text = "UP",
                                 command = self.capitalLetters)
        capital_char.grid(row = 6, column = 2 ,sticky = "nsew")

        space = tk.Button(self, text = "space", bg = "gray60",command = lambda:
                          self.messageEntry(" "))
        space.grid(row = 6, column = 3, columnspan = 4, sticky = "nsew")

        symbols = tk.Button(self, text = "SYM",
                            command = self.specialCharacters)
        symbols.grid(row = 6, column = 7,sticky = "nsew")

        delete = tk.Button(self, text = "DEL",
                           command = self.single_Char_Delete)
        delete.grid(row = 6, column = 8, columnspan = 2 ,sticky = "nsew")

    def connect(self):
        """ Send APN and Port number to start internet """
        if (len(self.APN.get()) and len(self.Port.get())):
            subprocess.call(shlex.split
                            ('sudo ' + path+'/PPP/ppp_create.sh '+
                             str(self.APN.get())+" "+str(self.Port.get())))
            subprocess.Popen('sudo ' + path + '/PPP/ppp_start.sh', shell=True)
            self.status.config(state = "normal")
            self.connect.config(state = "disable")

        else:
            label = tk.Label(self, text = "Enter values", bg = "yellow",
                             fg = "black")
            label.grid(row = 2, column = 0, columnspan = 2)
            label.after(2000, label.grid_forget)
            
    def disconnect(self):
        """ Disconnect Internet """
        try:
            subprocess.check_output(["sudo", "killall", "-9", "pppd"])
            self.connect.config(state = "normal")
            
        except:
            self.connect.config(state = "normal")

    def check_status(self):
        """ Update internet status """
        if "ppp0" in str(subprocess.check_output(["ifconfig"])):
            label = tk.Label(self, text = "Connected", bg = "OliveDrab",
                             fg = "white", font = 12)
            label.grid(row = 2, column = 0, columnspan = 2)
            label.after(2000, label.grid_forget)

        else:
            label = tk.Label(self, text = "Not Connected", bg = "red",
                             fg = "black", font = 12)
            label.grid(row = 2, column = 0, columnspan = 3)
            label.after(2000, label.grid_forget)
        

    def remember_Focus(self,event):
        """ Keeps the focussed widget global for the keyboard to input values in """
        self.focused_entry = event.widget


    def single_Char_Delete(self):
        """ Deletes a single character in the focussed widget """
        if(self.focused_entry == self.APN):
            self.num=self.APN.get()[:-1]
            self.APN.delete(0,"end")
            self.APN.insert(0,self.num)
        else:
            self.num=self.Port.get()[:-1]
            self.Port.delete(0,"end")
            self.Port.insert(0,self.num)
            
          
    def messageEntry(self, args):
        """ Message Entry """
        self.focused_entry.insert("end", args)

    
    def specialCharacters(self):
        """ Enables numbers(0-9) and special characters on the keyboard """
        self._buttonCharcount = self._buttonCharcount+1
        if(self._buttonCharcount == 1):
            for i in range(30):
                self.buttonData[i].grid_remove()
                self.buttonCapsData[i].grid_remove()
                self.buttonCharData[i].grid()

        else:
            for j in range(30):
                self.buttonCharData[j].grid_remove()
                self.buttonData[j].grid()
                self._buttonCharcount = 0
             
    def capitalLetters(self):
        """ Enables Capital Letters on the keyboard """
        self._buttoncount = self._buttoncount+1
        if(self._buttoncount == 1):
            for i in range(30):
                self.buttonData[i].grid_remove()
                self.buttonCharData[i].grid_remove()
                self.buttonCapsData[i].grid()
                
        else:
            for j in range(30):
                self.buttonCapsData[j].grid_remove()
                self.buttonCharData[j].grid_remove()
                self.buttonData[j].grid()
                self._buttoncount = 0

##############################  GalleryFrame  ##################################
class GalleryFrame(tk.Frame):
    """ This class handle Gallery """ 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)                                                         
        tk.Frame.config(self, bg="white")
        self.controller = controller
        self.images = []
        self.index = 0
        self.totalImages = 0
        self.homestate = None
        self.canvas = tk.Canvas(self, bg = "white", bd = 0)

        
        self.frame = tk.Frame(self.canvas, bg = "white",  bd = 0)
        self.vsb = tk.Scrollbar(self, orient = "vertical",
                                command = self.canvas.yview, width = 20)
        self.canvas.configure(yscrollcommand = self.vsb.set)
        self.frame.bind("<Configure>", lambda event,
                        canvas = self.canvas: self.onFrameConfigure(canvas))
        
        self.photo = tk.Button(self,text="Photos", bg = "white",
                               fg = "black", bd = 0,font=("Helvetica",16),
                               highlightbackground = "white",
                               activebackground = "white",
                               activeforeground = "black", image = icons[9],
                               compound="top", command = self.view_images)
        self.photo.place(x=140, y=100)

        self.video = tk.Button(self,text="Videos", bg = "white",fg = "black",
                               bd = 0,font=("Helvetica",16),
                               highlightbackground = "white",
                               activebackground = "white",
                               activeforeground = "black",image = icons[10],
                               compound="top", command = self.view_video)
        self.video.place(x=140, y=350)

        self.home = tk.Button(self, bg = "white", fg = "white", bd = 0,
                              highlightbackground = "white",image = icons[16],
                              activebackground = "white",
                              activeforeground = "white",
                              command = self.photo_home)
        self.home.place(x=210,y=720)

        self.prev = tk.Button(self, text = "<<", bg = "white", fg = "black",
                              font = ("Helvetica", 18), bd = 0,
                              highlightbackground = "white",
                              activebackground = "white",
                              activeforeground = "black", state = "disable",
                              command = self.prev_image)
        self.prev.place(x=20, y=720)

        
        self.next = tk.Button(self, text = ">>", bg = "white", fg = "black",
                              font = ("Helvetica", 18), bd = 0,
                              highlightbackground = "white",
                              activebackground = "white",
                              activeforeground = "black", state="disable",
                              command=self.next_image)
        self.next.place(x=410, y=720)

        self.label = tk.Label(self,text = "", font=("bold", 15),bg="white",
                              fg="black")
        self.label.place(x=380, y=750)

    def onFrameConfigure(self, canvas):
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
    def view_images(self):
        """ Open Images """
        self.homestate = "Photo"
        self.photo.config(state = "disable")
        for file in sorted(os.listdir('Gallery/Photos')):
            img = Image.open(path + "/Gallery/Photos/" + file)
            img = img.resize((480, 720), Image.ANTIALIAS)
            self.images.append(ImageTk.PhotoImage(img))

        if len(self.images):
            self.totalImages = len(self.images)
        
            self.showImage = tk.Label(self,image = self.images[0])
            self.showImage.grid(row=0, column=0)
            self.label.config(text= str(self.index + 1) + "/"+
                              str(self.totalImages))
            self.next.config(state= "normal")
            self.prev.config(state= "normal")
        else:
            self.label.config(text= "No Image")

    def next_image(self):
        """ Show next Image """
        if self.totalImages > 1 and self.index < (self.totalImages -1):
            self.index += 1
            self.showImage.config(image = self.images[self.index])
            self.label.config(text= str(self.index + 1) + "/"+
                              str(self.totalImages))

    def prev_image(self):
        """ Show previous Image """
        if self.homestate == "Photo":        
            if self.index > 0:
                self.index -= 1
                self.showImage.config(image = self.images[self.index])
                self.label.config(text= str(self.index + 1) + "/"+
                                  str(self.totalImages))

    def view_video(self):
        """ Go back to home frame """
        if os.listdir('Gallery/Videos'):
            self.vsb.pack(side = "right", fill = "y")
            self.canvas.pack(side = "left", fill = "both", expand = True)
            self.canvas.create_window((0,0), window = self.frame,
                                      width = 480, anchor = "nw")
            
            self.homestate = "Video"
            index = 0
            self.photo.place_forget()
            self.video.place_forget()
            self.next.place_forget()
            self.prev.place_forget()
            self.home.place_forget()
            self.label.place_forget()
            self.video_button = []
                    
            self.frame.grid_columnconfigure(0, weight = 1)
            self.videohome = tk.Button(self.frame, bg = "white",
                                       fg = "white", bd = 0,
                                       highlightbackground = "white",
                                       image = icons[16],
                                       activebackground = "white",
                                       activeforeground = "white",
                                       command = self.video_home)
            
            for file in sorted(os.listdir('Gallery/Videos')):
                self.video_button.append(tk.Button(self.frame,text = file,
                                                   font = ("Helvetica", 20),
                                                   command = lambda file=file:
                                                   self.play_video(file)))
                self.video_button[-1].grid(row = index, column = 0,
                                           sticky = "nsew")
                index = index+1
                self.videohome.grid(row = index, column = 0)
        else:
            self.video.config(state = "disable")
            self.label.config(text= "No Video")
            
        
    def play_video(self, args):
        """ Play video """
        subprocess.check_output(["sudo", "omxplayer",path+"/Gallery/Videos/"+
                                 str(args)])
        
    def photo_home(self):
        """ Go back to home from Photo """
        self.images = []
        self.index = 0
        self.next.config(state= "disable")
        self.prev.config(state= "disable")
        self.photo.config(state = "normal")
        self.label.config(text = "")
        
        if self.homestate == "Photo" and self.totalImages:
            self.showImage.grid_remove()

        self.video.config(state = "normal")
        self.controller.show_frame("HomeFrame")

    def video_home(self):
        """ Go back to home from Video """
        self.next.place(x=410, y=700)
        self.prev.place(x=20, y=700)
        self.videohome.grid_remove()
        self.canvas.pack_forget()
        self.vsb.pack_forget()
        
        for value in self.video_button:
            value.grid_forget()
            
        self.photo.place(x=140, y=100)
        self.video.place(x=140, y=350)
        self.home.place(x=210,y=700)
        self.label.place(x=720, y=420)
        self.controller.show_frame("HomeFrame")
        
###############################  CalculatorFrame  ##############################
class CalculatorFrame(tk.Frame):
    """ This class handle calculator """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.calculatorKeys = [
                               "7", "8", "9", "÷",
                               "4", "5", "6", "x",
                               "1", "2", "3", "-",
                               ".", "0", "%", "+",
                                ]
        self.calculatorKeyData = []
        self.newdiv='÷'

        for j in range(7):
            self.grid_rowconfigure(j, weight = 1)
            if j <= 3:
                self.grid_columnconfigure(j, weight = 1)

        self.calculatorentry = tk.Entry(self, width = 30,
                                        font = ("Helvetica", 20) )
        self.calculatorentry.grid(row = 0, column = 0, columnspan = 4,
                                  sticky = "nsew")

        self.square = tk.Button(self, text = "x²", width = 3, bg = "black",
                                fg = "white",font = ("Helvetica", 20),
                                command = self.square)
        self.square.grid(row = 1, column = 0, sticky = "nsew")

        self.sqroot = tk.Button(self, text = "√", width = 3, bg = "black",
                                fg = "white",font = ("Helvetica", 20),
                                command = self.squareroot)
        self.sqroot.grid(row = 1, column = 1, sticky = "nsew")

        self.AC = tk.Button(self, text = "AC", width = 3, bg = "black",
                            fg = "white",font = ("Helvetica", 20),
                            command = self.deleteall)
        self.AC.grid(row = 1, column = 2, sticky = "nsew")

        self.C = tk.Button(self, text = "C", width = 3, bg = "black",
                           fg = "white",font = ("Helvetica", 20),
                           command = self.delete1)
        self.C.grid(row = 1, column = 3, sticky = "nsew")

        c = 0
        r = 2
        for k in range(16):
            self.calculatorKeyData.append(0)
            self.calculatorKeyData[k] = tk.Button(self,
                                                  text = self.calculatorKeys[k],
                                                  width = 3, bg = "black",
                                                  fg = "white",
                                                  font = ("Helvetica", 20),
                                                  command = lambda k=k:
                                                  self.entryaction
                                                  (self.calculatorKeys[k]))
            self.calculatorKeyData[k].grid(row = r, column = c, sticky = "nsew")
            c = c + 1
            
            if(c == 4):
                r = r + 1
                c = 0

        tk.Button(self, text = "=",  bg = "black", font = ("Helvetica", 20),
                  fg = "white",
                  command = self.equals).grid(row = 6, column = 2,
                                              columnspan = 2, sticky = "nsew")

        tk.Button(self, bg = "black", fg = "red", text = "Back",
                  font = ("Helvetica", 20),
                  command = self.back).grid(row = 6, column = 0,
                                            sticky = "nsew")
        
        tk.Button(self, bg = "black", fg = "Deep sky blue",text = "Home",
                  font = ("Helvetica", 20),
                  command = self.home).grid(row = 6, column = 1,
                                            sticky = "nsew")

    def back(self):
        """ This class handle calculator """
        self.calculatorentry.delete("0", "end")
        self.controller.show_frame("Menu1Frame")

    def home(self):
        """ Go back to Home Frame """
        self.calculatorentry.delete("0", "end")
        self.controller.show_frame("HomeFrame")
    
    def getandreplace(self):
        """ replace x with * and ÷ with / """
        self.expression = self.calculatorentry.get()
        self.newtext=self.expression.replace(self.newdiv,'/')
        self.newtext=self.newtext.replace('x','*')

    def equals(self):
        """ Performs the arithematic operation and displays the result """
        self.getandreplace()
        try:
            self.value= eval(self.newtext)
        except SyntaxError or NameErrror:
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,'Invalid Input!')
        else:
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,self.value)

    def squareroot(self):
        """ Performs square root operation """
        self.getandreplace()
        try:
            self.value= eval(self.newtext) 
        except SyntaxError or NameErrror:
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,'Invalid Input!')
        else:
            self.sqrtval=math.sqrt(self.value)
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,self.sqrtval)

    def square(self):
        """ Performs squared operation """ 
        self.getandreplace()
        try:
            self.value= eval(self.newtext)
        except SyntaxError or NameErrror:
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,'Invalid Input!')
        else:
            self.sqval=math.pow(self.value,2)
            self.calculatorentry.delete(0,'end')
            self.calculatorentry.insert(0,self.sqval)

  
    def deleteall(self):
        """ Clears the calculator Entry """
        self.calculatorentry.delete(0, "end")

    def delete1(self):
        """ Deletes a single character in the calculator entry """
        self.txt=self.calculatorentry.get()[:-1]
        self.calculatorentry.delete(0,"end")
        self.calculatorentry.insert(0,self.txt)

    def entryaction(self, args):
        """ entry action """
        self.calculatorentry.insert("end", args)

###############################  StopwatchFrame  ###############################           
class StopwatchFrame(tk.Frame):
    """ This class handle Stop Watch """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self._running = 0
        self._start = 0.0        
        self._elapsedtime = 0.0
        tk.Frame.config(self, bg="black")

        for j in range(5):
            self.grid_rowconfigure(j, weight = 1)
            if j <= 2:
                self.grid_columnconfigure(j, weight = 1)

        self.canvas = tk.Canvas(self,bg="black",width = 240, height = 200,
                                highlightthickness=0,bd=0)
        self.canvas.create_rectangle(115,210,350,300,
                                     outline="royal blue",width=7)
        self.canvas.grid(row = 0, column = 0, rowspan = 3,columnspan = 3,
                         sticky = "nsew")

        tk.Label(self, text = "HH : MM : SS", font = ('bold', 18),
                 fg = "white", bg = "black").place(x = 155, y = 170)
        
        self.stopwatch = tk.Label(self,bg = "black", fg = "yellow",
                                  text = "00:00:00" , bd  = 0,
                                  highlightthickness = 0, font = ('bold', 30))
        self.stopwatch.grid(row = 1, column = 1)

        self.startwatch = tk.Button(self, text = "Start", image=icons[29],
                                    bg = "black", fg = "white", bd=0,
                                    highlightbackground = "black",
                                    activebackground = "black",
                                    activeforeground = "black",
                                    command = self.start_watch)
        self.startwatch.grid(row = 3, column = 0)

        self.stopWatch = tk.Button(self, text = "Stop",image=icons[37],
                                   bg = "black", fg = "white", bd=0,
                                   highlightbackground = "black",
                                   activebackground = "black",
                                   activeforeground = "black",
                                   command = self.stop_watch)
        self.stopWatch.grid(row = 3, column = 1)

        self.reset = tk.Button(self, text = "Reset",image=icons[31],
                               bg = "black", fg = "white", bd=0,
                               highlightbackground = "black",
                               activebackground = "black",
                               activeforeground = "black",
                               command = self.reset_watch)
        self.reset.grid(row = 3, column = 2)

        goback = tk.Button(self, bg = "black", fg = "black", bd = 0,
                           highlightbackground = "black",
                           activebackground = "black",
                           activeforeground = "black",
                           image = icons[30],text = "Home",
                           command = self.back)
        goback.grid(row = 4, column = 0)
        gohome = tk.Button(self, bg = "black", fg = "black", bd = 0,
                           highlightbackground = "black",
                           activebackground = "black",
                           activeforeground = "black",
                           image = icons[16],text = "Home",
                           command = self.home)
        gohome.grid(row = 4, column = 2)

    def start_watch(self):
        """ Starts the timer on the stopwatch """
        if not self._running:            
            self._start = time.time() - self._elapsedtime
            self._update()
            self._running = 1
 
    def _update(self):
        """ Update time """
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.master.after(50, self._update)
 
    def _setTime(self, elap):
        """ set time """
        minutes = int(elap/60)
        seconds = int(elap - minutes*60.0)
        hseconds = int((elap - minutes*60.0 - seconds)*100)                
        self.stopwatch.config(text = '%02d:%02d:%02d' % (minutes, seconds, hseconds))
 
    def stop_watch(self):
        """ stop timer """
        if self._running:
            self.master.after_cancel(self._timer)            
            self._elapsedtime = time.time() - self._start    
            self._setTime(self._elapsedtime)
            self._running = 0

    def reset_watch(self):
        """ Reset watch """
        self._start = time.time()         
        self._elapsedtime = 0.0
        self._setTime(self._elapsedtime)

    def back(self):
        """ Go back to Menu1 Frame """
        self.reset_watch()
        self.stop_watch()
        self.controller.show_frame("Menu1Frame")

    def home(self):
        """ Go to Home Frame """
        self.reset_watch()
        self.stop_watch()
        self.controller.show_frame("HomeFrame")

##############################  CalendarFrame  ###############
class CalendarFrame(tk.Frame):
    """ This class Calendar """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller
        self.wid = []

        self.DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday']

        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.cal = calendar.TextCalendar(calendar.SUNDAY)

        self.setup(self.year, self.month)
        for i in range(8):
            self.grid_columnconfigure(i, weight = 1)
            if i<= 6:
                self.grid_rowconfigure(i, weight = 1)

    def setup(self, y, m):
        """ Setup """
        left_month = tk.Button(self, text='<',font=("bold", 16),
                               bg = "black", fg = "tomato",
                               command=self.go_prev_month)
        self.wid.append(left_month)
        left_month.grid(row=0, column=0)
        right_month = tk.Button(self, text='>', font=("bold", 16),
                                bg = "black", fg = "tomato",
                                command=self.go_next_month)
        self.wid.append(right_month)
        right_month.grid(row=0, column=1)
                 
        header = tk.Label(self, bg = "black", fg = "SlateBlue1",
                          text='{}   {}'.format(calendar.month_abbr[m], str(y)),
                          font = ("bold", 18))
        self.wid.append(header)
        header.grid(row=0, column=2, columnspan=3)
        
        left_year = tk.Button(self, text='∨',font=("bold", 16), bd = 0,
                              bg = "black", fg = "tomato",
                              command=self.go_prev_year)
        self.wid.append(left_year)
        left_year.grid(row=0, column=5)         
        right_year = tk.Button(self, text='∧',font=("bold", 16), bd = 0,
                               bg = "black", fg = "tomato",
                               command=self.go_next_year)
        self.wid.append(right_year)
        right_year.grid(row=0, column=6)
                 
        
        for num, name in enumerate(self.DAYS):
            t = tk.Label(self, text=name[:3], bg = "black", fg = "gold",
                         font = ("bold", 15))
            self.wid.append(t)
            t.grid(row=1, column=num)
                 
        for w, week in enumerate(self.cal.monthdayscalendar(y, m), 2):
            for d, day in enumerate(week):
                if day:
                    b = tk.Button(self, width=1, text=day, bg = "black",
                                  fg = "white", font = ("bold", 15))
                    self.wid.append(b)
                    b.grid(row=w, column=d)

        ok = tk.Button(self, image = icons[30], bg = "black", fg = "black",
                       bd = 0, highlightbackground = "black",
                       activebackground = "black",activeforeground = "black",
                       command = lambda:
                       self.controller.show_frame("Menu2Frame"))
        self.wid.append(ok)
        ok.grid(row=8, column=0, columnspan=3, pady=10)
        
        home = tk.Button(self, image = icons[16], bg = "black", bd=0,
                         activeforeground = "black",
                         highlightbackground="black",activebackground = "black",
                         command = lambda:
                         self.controller.show_frame("HomeFrame"))
        self.wid.append(ok)
        home.grid(row=8, column=4, columnspan=3, pady=10)

    def clear(self):
        """ Clear """
        for w in self.wid[:]:
            w.grid_forget()
            self.wid.remove(w)
             
    def go_prev_month(self):
        """ go previous month """
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        self.clear()
        self.setup(self.year, self.month)
         
    def go_next_month(self):
        """ go to next month """
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
        self.clear()
        self.setup(self.year, self.month)

    def go_prev_year(self):
        """ go to previous year """
        self.year -= 1
        self.clear()
        self.setup(self.year, self.month)
        
    def go_next_year(self):
        """ go to next year """
        self.year += 1     
        self.clear()
        self.setup(self.year, self.month)

###############################  AudioFrame  ###################################
class AudioFrame(tk.Frame):
    """ This class hanlde Audio Mode """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")

        for j in range(5):
            self.grid_rowconfigure(j, weight = 1)

        for i in range (3):
            self.grid_columnconfigure(i, weight = 1)

        self.headphone = tk.Button(self, text = "Headphone \nMode",
                                   image  = icons[15], font = ("bold", 15),
                                   bg = "black", fg = "white",bd = 0,
                                   highlightbackground = "black",
                                   activebackground = "black",
                                   activeforeground = "white",compound = "top",
                                   anchor = "w", command = self.headphone_mode)
        self.headphone.grid(row = 0, column = 0, ipadx = 0, sticky = "s")

        self.speaker = tk.Button(self, text = "Speaker \nMode",
                                 image  = icons[34], font = ("bold", 15),
                                 bg = "black", fg = "white",bd = 0,
                                 highlightbackground = "black",
                                 activebackground = "black",
                                 activeforeground = "white",compound = "top",
                                 anchor = "w", command = self.speaker_mode)
        self.speaker.grid(row = 0, column = 2,sticky = "s")

        self.slider = tk.Scale(self, from_=0, to=7, orient = "horizontal",
                               bg = "black", fg = "white", bd = 0,
                               highlightbackground = "black",state = "disable",
                               font = ("Helvetica", 12))
        self.slider.grid(row = 2, column = 0, columnspan = 3, sticky = "nsew",
                         padx = 50)

        self.gainset = tk.Button(self,text = "Set", state = "disable",
                                 font = ("Helvetica", 15), fg = "white",
                                 bg = "black", command = self.set_Volume)
        self.gainset.grid(row = 3, column = 1)

        backbutton = tk.Button(self, text = "Back", image = icons[30],
                               bg = "black", fg = "black", bd = 0,
                               highlightbackground = "black",
                               activebackground = "black",
                               activeforeground = "black",
                               command = lambda:
                               controller.show_frame("Menu2Frame"))
        backbutton.grid(row = 4, column = 0,sticky = "nsew")

        homebutton = tk.Button(self, text = "Home", image = icons[16],
                               bg = "black", fg = "black", bd = 0,
                               highlightbackground = "black",
                               activebackground = "black",
                               activeforeground = "black",
                               command = lambda:
                               controller.show_frame("HomeFrame"))
        homebutton.grid(row = 4, column = 2, sticky = "nsew")
        

    def headphone_mode(self):
        """ Headphone Mode """
        self.slider.config(label = "Headphone gain", state = "disable",
                           fg = "yellow")
        self.gainset.config(state = "disable")
        self.headphone.grid_configure(sticky = "n")
        self.speaker.grid_configure(sticky = "s")
        phone.jackMode()
        
    def speaker_mode(self):
        """ Speaker Mode """
        self.slider.config(label = "Speaker gain", state = "normal",
                           fg = "deep sky blue")
        self.gainset.config(state = "normal")
        self.headphone.grid_configure(sticky = "s")
        self.speaker.grid_configure(sticky = "n")
        phone.speakerMode()

    def set_Volume(self):
        """ Set Volume """
        label = tk.Label(self, text = "Volume \nset", fg = "black",
                         bg = "yellow")
        label.grid(row = 4, column = 1)
        label.after(3000, label.grid_forget)

        
#############################  SensorFrame  ####################################
class SensorFrame(tk.Frame):
    """ This class handle Sensors data """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller

        tk.Label(self,text = "Read ADC Values" ,font=("bold", 22),
                 bg = "black", fg="red").place(x=130,y=30)
        tk.Label(self,text = "Measure Voltage Range 0v - 2.1v" ,
                 font=("bold", 12), bg = "yellow").place(x=140,y=80)

        tk.Button(self, bg = "black", fg = "black", bd = 0,
                  highlightbackground = "black",  activebackground = "black",
                  activeforeground = "black",
                  image = icons[30],text = "Home",
                  command = self.back).place(x=20, y=700)
        tk.Button(self, bg = "black", fg = "black", bd = 0,
                  highlightbackground = "black",  activebackground = "black",
                  activeforeground = "black",
                  image = icons[16],text = "Home",
                  command = self.home).place(x=410, y=700)

        tk.Label(self,text = "ADC 0" ,font=("bold", 15), bg = "black",
                 fg="gold2").place(x=250,y=200)
        tk.Label(self,text = "mV" ,font=("bold", 12), bg = "black",
                 fg="red").place(x=370,y=260)
        tk.Button(self, text="Read ADC 0", height=2 ,width=7,
                  command = self.read_ADC0).place(x=100, y=250)
        self.adc0 = tk.Entry(self,font=12,width = 15)
        self.adc0.place(x=200, y=260)
        
        tk.Label(self,text = "ADC 1" ,font=("bold", 15), bg = "black",
                 fg="gold2").place(x=250,y=350)
        tk.Label(self,text = "mV" ,font=("bold", 12), bg = "black",
                 fg="red").place(x=370,y=410)
        tk.Button(self, text="Read ADC 1", height=2 ,width=7,
                  command = self.read_ADC1).place(x=100, y=400)
        self.adc1 = tk.Entry(self,font=12,width = 15)
        self.adc1.place(x=200, y=410)
        
    def read_ADC0(self):
        """ Read ADC 0 value """
        self.adc0.delete(0, "end")
        self.adc0.insert("end", str(phone.readADC0()))   
        
    def read_ADC1(self):
        """ Read ADC 1 value """
        self.adc1.delete(0, "end")
        self.adc1.insert(0, str(phone.readADC1()))

    def home(self):
        """ Go to Home Frame """
        self.adc0.delete(0, "end")
        self.adc1.delete(0, "end")
        self.controller.show_frame("HomeFrame")

    def back(self):
        """ Go to Menu 2 Frame """
        self.adc0.delete(0, "end")
        self.adc1.delete(0, "end")
        self.controller.show_frame("Menu2Frame")
        
######################################  PiFrame  ###############################
class PiFrame(tk.Frame):
    """ This class Pi Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.buttons = []
        tk.Frame.config(self, bg="black")
        
        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=2:
                self.grid_columnconfigure(j, weight = 1)
           

        self.warningLabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text = "This feature allows you to\n "
                                     "access your Raspberry Pi \nby shutting "
                                     "down the phone UI",
                                     font = ("Helvetica", 22))
        self.warningLabel.grid(row = 0, column = 0, columnspan = 3,
                               sticky = "nsew")
        tk.Label(self, text = "Press OK to confirm", fg = "yellow",
                 bg = "black",
                 font = ("Helvetica", 20)).grid(row = 1, column = 1)
        
        ok = tk.Button(self, text = "OK" ,fg = "yellow",image = icons[18],
                       font = ("Helvetica", 15), anchor = "center",
                       highlightbackground = "white", bg = "black",
                       activebackground = "black",activeforeground = "white",
                       compound = "top", command = self.closeUI)
        ok.grid(row = 2, column = 1)

        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black",
                         anchor = "center", command = lambda :
                         self.controller.show_frame("Menu2Frame"))
        back.grid(row = 3, column = 0)

        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",
                  bd = 0,highlightbackground = "black", bg = "black",
                  activebackground = "black",
                  command = lambda:
                  controller.show_frame("HomeFrame")).grid(row = 3, column = 2)

    def closeUI(self):
        """ Close GUI """
        phone.close()
        app.destroy()

#############################  AboutFrame  #####################################
class AboutFrame(tk.Frame):
    """ This class handle About us Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller

        for i in range(12):
            self.grid_rowconfigure(i, weight = 1)
            if i <=4:
                self.grid_columnconfigure(i, weight = 1)

        header_label = tk.Label(self, text = "PiTalk", fg = "gold2",
                                bg = "black", font = ("Helvetica", 30))
        header_label.grid(row = 0, column = 2, sticky = "ew")



        tk.Label(self, text = 'PiTalk is a 3G GSM Shield for  RPi',
                 bg = "black", fg = "olive drab",
                 font = ("Bold", 18)).grid(row = 1, column = 0,
                                           columnspan = 5, sticky = "w")
        tk.Label(self, text = "  ->Quectel UC15 Chipset", bg = "black",
                 fg = "white",
                 font = ("Helvetica",18)).grid(row = 2, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = '  ->Compatible with 3.2", 4", 5" LCD',
                 bg = "black", fg = "white",
                 font = ("Helvetica",18)).grid(row = 3, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = "  ->Quad band UTMS/HSPDA Module", bg = "black",
                 fg = "white",
                 font = ("Helvetica",18)).grid(row = 4, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = "  ->Compatiable with Pi2/Pi3/PiZero",
                 bg = "black", fg = "white",
                 font = ("Helvetica",18)).grid(row = 5, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = "For More Info:", bg = "black",
                 fg = "turquoise",
                 font = ("Bold",20)).grid(row = 6, column = 0,
                                          sticky = "w", columnspan = 5)
        tk.Label(self, text = '    www.sb-components.co.uk', bg = "black",
                 fg = "white",
                 font = ("Helvetica",18)).grid(row = 7, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = "Developed by:", bg = "black",
                 fg = "tomato",
                 font = ("Bold",20)).grid(row = 8, column = 0,
                                          sticky = "w", columnspan = 5)
        tk.Label(self, text = "  Ankur Singh ", bg = "black",
                 fg = "white",
                 font = ("Helvetica",18)).grid(row = 9, column = 0,
                                               sticky = "w", columnspan = 5)
        tk.Label(self, text = "  Asher Ahmad Farooqui", bg = "black",
                 fg = "white",
                 font = ("Helvetica",18)).grid(row = 10, column = 0,
                                               sticky = "w", columnspan = 5)

        back_button = tk.Button(self, image = icons[30], bg = "black",
                                fg = "black", bd = 0,
                                highlightbackground = "black",
                                activebackground = "black",
                                activeforeground = "black",
                                command = lambda:
                                controller.show_frame("Menu2Frame"))
        back_button.grid(row = 12, column = 1)

        homebutton = tk.Button(self, image = icons[16], bg = "black",
                               fg = "black", bd = 0,
                               highlightbackground = "black",
                               activebackground = "black",
                               activeforeground = "black",
                               command = lambda:
                               controller.show_frame("HomeFrame"))
        homebutton.grid(row = 12, column = 3)

###################################  SIMFrame  #################################      
class SIMFrame(tk.Frame):
    """ This class handle SIM Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self, bg="black")
        self.controller = controller

        tk.Label(self, text = "IMEI Number:",font = ("bold", 28),
                 bg = "black", fg = "orange red").pack(pady = 50)

        self.imeiLabel = tk.Label(self, text = "",font = ("bold",22),
                                  bg = "black", fg = "yellow")
        self.imeiLabel.pack()

        tk.Label(self, text = "Module: ",font = ("bold", 28),
                 bg = "black", fg = "orange red").pack(pady = 50)

        tk.Label(self, text = "Quectel UC15",font = ("bold",22),
                 bg = "black", fg = "yellow").pack()

        tk.Label(self, text = "Carrier:",font = ("bold", 28),bg = "black",
                 fg = "orange red").pack(pady = 50)

        self.networkLabel = tk.Label(self, text = "",font = ("bold",22),
                                     bg = "black", fg = "yellow")
        self.networkLabel.pack()

        tk.Button(self, text="Read",font = ("Helvetica", 15),bg = "black",
                  fg = "tomato", command=self.read).pack(pady = (20,0))

        tk.Button(self, image = icons[30], bg = "black", fg = "black",
                  bd = 0, highlightbackground = "black",
                  activebackground = "black", activeforeground = "black",
                  command = lambda:
                  controller.show_frame("Menu2Frame")).pack(side = "left",
                                                            pady = (90,0))

        tk.Button(self, image = icons[16], bg = "black", fg = "black", bd = 0,
                  highlightbackground = "black",activebackground = "black",
                  activeforeground = "black", command = lambda:
                  controller.show_frame("HomeFrame")).pack(side = "right",
                                                           pady = (90,0))

    def read(self):
        """ Read SIM data """
        self.imeiLabel.config(text = self.controller.imei)
        self.networkLabel.config(text = self.controller.networkName)
        
    
#############################  SettingsFrame  ##################################
class SettingsFrame(tk.Frame):
    """ This class handle Settings Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        BUTTON = [# Text                     Image       Frame  
                  ("Screen Orientation",  icons[28], "GUIRotateFrame"),
                  ("Call Settings",       icons[7],  "CallSettingFrame"),
                  ("HDMI Mode",           icons[43],  "HDMIFrame" ),
                  ("Logs",      icons[46], "LogFrame" ),
                  ("Shutdown",            icons[44],  "ShutdownFrame" ),
                   ]

        self.grid_columnconfigure(0, weight = 2)
        for j in range(5):
            self.grid_rowconfigure(j, weight = 1)

        for b in range(len(BUTTON)):
            cmd = lambda x=BUTTON[b][2]: controller.show_frame(x)
            tk.Button(self, text = BUTTON[b][0], image = BUTTON[b][1],
                      font = ("Helvetica", 15), bg = "black", fg = "white",
                      anchor = "w", bd = 0,highlightbackground = "black",
                      activeforeground = "white", activebackground = "black",
                      compound = 'left', command = cmd).grid(row = b,
                                                             column = 0,
                                                             sticky = "nsew")

        tk.Button(self, text = "Go Home", image = icons[16], fg = "white",
                  bd = 0, anchor = "center",
                  command = lambda:
                  controller.show_frame("HomeFrame")).grid(row = 5, column = 0)
            
####################################  GUIRotateFrame  ##########################
class GUIRotateFrame(tk.Frame):
    """ This class Rotation of GUI """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")

        for j in range(5):
            self.grid_rowconfigure(j, weight = 1)
            if j < 2:
                self.grid_columnconfigure(j, weight = 1)

        tk.Label(self, text ="This will reboot your system and \ncalibrate "
                 "the screen", font = ("Helvetica", 18), bd = 2,fg = "tomato",
                 bg = "black").grid(row = 0, column = 0,columnspan = 2 ,
                                    sticky = "nsew")
        rotate0 = tk.Button(self, text = "Rotate 0°  ",
                            command = lambda:self.screenRotate(0), bg = "black",
                            fg = "white",font = ("helvetica", 15),bd = 2,
                            highlightbackground = "black",compound="left",
                            activebackground = "black",
                            activeforeground = "white",image  = icons[39])
        rotate0.grid(row = 1, column = 0)

        rotate90 = tk.Button(self, text = "Rotate 90° ",
                             command = lambda:self.screenRotate(90),
                             bg = "black", fg = "white",
                             font = ("helvetica", 15),bd = 2,
                             highlightbackground = "black",compound="left",
                             activebackground = "black",
                             activeforeground = "white", image  = icons[40])
        rotate90.grid(row = 1, column = 1)

        rotate180 = tk.Button(self, text = "Rotate 180°",
                              command = lambda:self.screenRotate(180),
                              bg = "black", fg = "white",
                              font = ("helvetica", 15), bd = 2,
                              highlightbackground = "black",compound="left",
                              activebackground = "black",
                              activeforeground = "white",image  = icons[41])
        rotate180.grid(row = 2, column = 0)

        rotate270 = tk.Button(self, text = "Rotate 270°",
                              command = lambda:self.screenRotate(270),
                              bg = "black", fg = "white",
                              font = ("helvetica", 15),bd = 2,
                              highlightbackground = "black",compound="left",
                              activebackground = "black",
                              activeforeground = "white",image  = icons[42])
        rotate270.grid(row = 2, column = 1)



        goback = tk.Button(self, text = "go Back",image = icons[30],
                           bg = "black", fg = "black", bd = 0,
                           highlightbackground = "black",
                           activebackground = "black",
                           activeforeground = "black",
                           command = lambda:
                           controller.show_frame("SettingsFrame"))
        goback.grid(row = 4, column = 0)

        home = tk.Button(self, text = "Go Home", image = icons[16],bg = "black",
                         fg = "white", bd = 0, highlightbackground = "black",
                         activebackground = "black", activeforeground = "black",
                         command = lambda: controller.show_frame("HomeFrame"))
        home.grid(row = 4, column = 1)

    def screenRotate(self, arg):
        """ Screen Rotate """
        if arg == 0:
            subprocess.call(['./LCD5-show','0'], cwd = path+'/LCD-show')
        elif arg == 90:
            subprocess.call(['./LCD5-show','90'], cwd = path+'/LCD-show')
        if arg == 180:
            subprocess.call(['./LCD5-show','180'], cwd = path+'/LCD-show')
        if arg == 270:
            subprocess.call(['./LCD5-show','270'], cwd = path+'/LCD-show')
            
############################  CallSettingFrame  ################################
class CallSettingFrame(tk.Frame):
    """ This class Call settings Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.buttons = []
        tk.Frame.config(self, bg="black")

        BUTTON = [#   text  anchor row col
                 ("1",   "e",   3,  1), ("2", "center", 3, 2), ("3", "w", 3, 3),
                 ("4",   "e",   4,  1), ("5", "center", 4, 2), ("6", "w", 4, 3),
                 ("7",   "e",   5,  1), ("8", "center", 5, 2), ("9", "w", 5, 3),
                 ("*",   "e",   6,  1), ("0", "center", 6, 2), ("#", "w", 6, 3)]

        for i in range(6):
            self.grid_rowconfigure(i, weight = 1)
            if i <= 5:
                self.grid_columnconfigure(i, weight = 1)

        canvas = tk.Canvas(self, bg = "snow", height = 10).grid(row = 0,
                                                                column = 0,
                                                                columnspan = 6,
                                                                sticky = "nsew")
        tk.Label(self,bg = "snow", fg = "black",
                 text = "Auto Answer after rings:",
                 font = ("Helvetica",12)).grid(row = 0, column = 0,
                                               columnspan = 2)

        self.ringspin = tk.Spinbox(self,from_=0, to = 255, width = 10,
                                   font = ("Helvetica", 15))
        self.ringspin.grid(row = 0, column = 2, columnspan = 3)
        tk.Button(self,text = "Set",bg = "deep sky blue", fg = "white",
                  command = self.ring_Set,
                  font = ("Helvetica", 16)).grid(row = 0, column = 5)

        tk.Label(self,bg = "black", fg = "white", text = "Forward Calls to :",
                 font = ("Helvetica",12)).grid(row = 1, column = 0,
                                               columnspan = 2)

        self.forwardnumber = tk.Entry(self, font = ('bold', 18),
                                      justify="right",fg='RoyalBlue1')
        self.forwardnumber.grid(row = 1, column = 2, columnspan = 4,
                                sticky = "ew")
        tk.Button(self,text = "Enable", font = ("Helvetica", 16),
                  command = self.set_callforwarding).grid(row = 2, column = 4,
                                                          columnspan = 2)
       
        for b in range(12):
            cmd = lambda x=BUTTON[b][0]: self.dial_Entry(x)
            self.buttons.append(tk.Button(self,text=BUTTON[b][0],
                                          font=('Helvetica',17),
                                          highlightbackground="black",
                                          activebackground = "black",
                                          activeforeground="white",bg="black",
                                          fg="white",bd=0,command = cmd))
            self.buttons[b].grid(row=BUTTON[b][2],column=BUTTON[b][3])

    
        tk.Button(self,text = "Check Call \nForwading", bg = "black",
                  fg = "white",  font = ("Helvetica", 16), \
                  command = self.check_status).grid(row = 2, column = 0,\
                                                    columnspan = 2)

        tk.Button(self,text = "Disable Call \nForwading", bg = "black",
                  fg = "white",font = ("Helvetica", 16),\
                  command = self.disable_callforwarding).\
                  grid(row = 2, column = 2, columnspan = 2)

        tk.Button(self,image = icons[16], bg = "black", fg = "white", bd = 0,
                  highlightbackground = "black", activebackground = "black",
                  activeforeground = "black",
                  command = self.home).grid(row = 6, column = 5)

        tk.Button(self,image = icons[30], bg = "black", fg = "black", bd = 0,
                  highlightbackground = "black", activebackground = "black",
                  activeforeground = "black", command = lambda: controller.\
                  show_frame("SettingsFrame")).grid(row = 6,column = 0)

        tk.Button(self, image = icons[11],bd=0,bg = "black", fg = "white",
                  highlightbackground = "black",activebackground = "black",
                  activeforeground = "white",
                  command = self.dial_Delete).grid(row = 6, column = 4)

    def ring_Set(self):
        """ Set rings for auto-answering """
        label = tk.Label(self, font = ("Helvetica", 15))
        if int(self.ringspin.get()):
            label.config(text = "Auto Ring Enable", bg = "yellow", fg = "black")
            label.place(x=10, y = 80)
            phone.autoRing(int(self.ringspin.get()))
            label.after(2000, label.place_forget)
            self.controller.Fl_Auto_Answer = True                                 
        else:
            phone.autoRing(int(self.ringspin.get()))
            label.config(text = "Auto Ring Not Enabled", bg = "yellow",
                         fg = "black")#, anchor = "w")
            label.place(x=10, y = 80)
            label.after(2000, label.place_forget)

    def check_status(self):
        """ Check status of call forwarding """
        number = phone.statusCallForwarding()
        if (number):
            self.forwardnumber.delete("0", "end")
            self.forwardnumber.insert("end",number)
        else:
            self.forwardnumber.delete("0", "end")
            self.forwardnumber.insert("end", "N/A")

    def disable_callforwarding(self):
        """ Disable call forwarding """
        label = tk.Label(self, text = "Disabled", bg = "yellow",
                         fg = "black", font = ("Helvetica", 15))
        label.place(x=20, y=350)
        phone.disableCallForwarding()
        self.forwardnumber.delete("0", "end")
        label.after(2000, label.place_forget)

    def set_callforwarding(self):
        """ Set call forwading """
        label = tk.Label(self, font = ("Helvetica", 15))
        if self.forwardnumber.get():
            if phone.enableCallForwarding(self.forwardnumber.get()):
                label.config(text = "Enabled", bg = "yellow", fg = "black",
                             font = ("Helvetica", 15))
                label.place(x=20, y=350)
                label.after(2000, label.place_forget)
            else:
                label.config(text = "Number Format \nNot Correct",
                             bg = "yellow", fg = "black",
                             font = ("Helvetica", 15))
                label.place(x=20, y=350)
                label.after(2000, label.place_forget)
                
    def dial_Entry(self, args):
        """ Enables the entry widget to get values from the dialpad """
        self.forwardnumber.insert("end", args)
      
    def dial_Delete(self):
        """ Deletes a single character in the dialler entry """ 
        self.txt=self.forwardnumber.get()[:-1]
        self.forwardnumber.delete(0,"end")
        self.forwardnumber.insert(0,self.txt)

    def home(self):
        """ Go to Home Frame """
        self.forwardnumber.delete("0", "end")
        self.controller.show_frame("HomeFrame")

    def back(self):
        """ Go to Settings Frame """
        self.forwardnumber.delete("0", "end")
        self.controller.show_frame("SettignsFrame")

##############################  HDMIFrame  #####################################
class HDMIFrame(tk.Frame):
    """ This class HDMI Mode """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.buttons = []
        tk.Frame.config(self, bg="black")
        
        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=2:
                self.grid_columnconfigure(j, weight = 1)
           

        self.warningLabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text = "Selecting this reboots and "
                                     "changes \noutput to HDMI",
                                     font = ("Helvetica", 20))
        self.warningLabel.grid(row = 0, column = 0, columnspan = 3,
                               sticky = "nsew")
        tk.Label(self, text = "Press OK to confirm", fg = "yellow",
                 bg = "black",
                 font = ("Helvetica", 20)).grid(row = 1, column = 1)
        
        ok = tk.Button(self, text = "OK" ,fg = "yellow",image = icons[43],
                       font = ("Helvetica", 15), anchor = "center",
                       highlightbackground = "white", bg = "black",
                       activebackground = "black",activeforeground = "white",
                       compound = "top", command = self.hdmi_mode)
        ok.grid(row = 2, column = 1)

        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black",
                         anchor = "center", command = lambda :
                         self.controller.show_frame("SettingsFrame"))
        back.grid(row = 3, column = 0)


        
        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",\
                  bd = 0,highlightbackground = "black", bg = "black", \
                  activebackground = "black", command = lambda: controller.\
                  show_frame("HomeFrame")).grid(row = 3, column = 2)

    def hdmi_mode(self):
        """ HDMI mode """
        subprocess.call(['./LCD-hdmi','0'], cwd = path+'/LCD-show')

#########################  LogFrame  ###########################################        
class LogFrame(tk.Frame):
    """ This class handle logging of call and SMS """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")
        self.Fl_logs = True
        
        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=2:
                self.grid_columnconfigure(j, weight = 1)
           

        self.warningLabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text="Enable/Disable or Delete ALL logs",
                                     font = ("Helvetica", 20))
        self.warningLabel.grid(row = 0, column = 0, columnspan = 3)
        
        self.enable = tk.Button(self, text = "Enable Log",
                                command = self.enable_log, bg = "black",
                                fg = "white",font = ("helvetica", 15),bd = 2,
                                highlightbackground = "black",compound="left",
                                activebackground = "black", state = "disable",
                                activeforeground = "white",image  = icons[47])
        self.enable.grid(row = 1, column = 0)

        self.disable = tk.Button(self, text = "Disable Log",
                                 command = self.disable_log,bg = "black",
                                 fg = "white",font = ("helvetica", 15),
                                 bd = 2, highlightbackground = "black",
                                 compound="left", activebackground = "black",
                                 activeforeground = "white",image  = icons[48])
        self.disable.grid(row = 1, column = 2)

        self.deletelog = tk.Button(self, text = "  Delete All Logs ",
                                   command = self.delete_log, bg = "black",
                                   fg = "white",font = ("helvetica", 15),bd = 2,
                                   highlightbackground = "black",compound="left",
                                   activebackground = "black", image  = icons[49],
                                   activeforeground = "white", )
        self.deletelog.grid(row = 2, column = 0, columnspan = 3)
        
        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black",anchor = "center",
                         command = lambda :
                         self.controller.show_frame("SettingsFrame"))
        back.grid(row = 3, column = 0)
        
        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",
                  bd = 0,highlightbackground = "black", bg = "black",
                  activebackground = "black",command = lambda:
                  controller.show_frame("HomeFrame")).grid(row = 3, column = 2)

        self.status = tk.Label(self,text="Logs Enabled", bg="spring green",
                               fg="black", font=("Helvetica", 12))
        self.status.place(x=180,y=540)

    def enable_log(self):
        """ Enable logging """
        self.Fl_logs = True
        self.status.config(text="Logs Enabled", bg="spring green")
        self.enable.config(state="disable")
        self.disable.config(state="normal")

    def disable_log(self):
        """ Disable Logging """
        self.Fl_logs = False
        self.enable.config(state="normal")
        self.disable.config(state="disable")
        self.status.config(text="Logs Disabled", bg="red")
        
    def delete_log(self):
        """ Delete all the logs """
        label = tk.Label(self,bg="black", fg="black", font=("Helvetica", 12))
        label.place(x=180, y=650)
        open(path + '/Logs/Call/Outgoing.txt', 'w').close()
        open(path + '/Logs/Call/Incoming.txt', 'w').close()
        open(path + '/Logs/Message/Inbox.txt', 'w').close()
        open(path + '/Logs/Message/Outbox.txt', 'w').close()
        label.config(text="Logs Deleted", bg="magenta")
        label.after(1000, label.place_forget)

###########################  ShutdownFrame  ####################################      
class ShutdownFrame(tk.Frame):
    """ This class handle SHUTDOWN """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")
        
        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=2:
                self.grid_columnconfigure(j, weight = 1)

        self.warningLabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text = "Selecting this shuts down your \n"
                                     "GSM Module and UI",
                                     font = ("Helvetica", 20))
        self.warningLabel.grid(row = 0, column = 0, columnspan = 3)
        tk.Label(self, text = "Press OK to confirm", fg = "yellow",
                 bg = "black", font = ("Helvetica", 20)).\
                 grid(row = 1, column = 1, sticky = "nsew")
        
        ok = tk.Button(self, text = "OK" ,fg = "yellow",image = icons[44],
                       font = ("Helvetica", 15), anchor = "center",
                       highlightbackground = "white", bg = "black",
                       activebackground = "black",activeforeground = "white",
                       compound = "top", command = self.shutdown)
        ok.grid(row = 2, column = 1)

        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black", anchor = "center",\
                         command = lambda : self.controller.\
                         show_frame("SettingsFrame"))
        back.grid(row = 3, column = 0)


        
        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",
                  bd = 0,highlightbackground = "black", bg = "black",
                  activebackground = "black",command = lambda:
                  controller.show_frame("HomeFrame")).grid(row = 3, column = 2)

    def shutdown(self):
        """ Shutdown """
        phone.shutdown()
        time.sleep(1)
        phone.close()
        app.destroy()

##############################  LocationFrame  #################################
class LocationFrame(tk.Frame):
    """ This class handle Location Frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")

        for j in range(4):
            self.grid_rowconfigure(j, weight = 1)
            if j<=1:
                self.grid_columnconfigure(j, weight = 1)
           

        self.headinglabel = tk.Label(self, bg = "black", fg = "Deep sky blue",
                                     text = "Get location coordinates",
                                     font = ("Helvetica", 20))
        self.headinglabel.grid(row = 0, column = 0, columnspan = 2)
        
        self.lattitude = tk.Label(self, text = "Lattitude: " ,bg = "black",
                                  fg = "tomato",font = ("helvetica", 15),
                                  bd = 2, highlightbackground = "black",
                                  activebackground = "black",
                                  activeforeground = "white")
        self.lattitude.grid(row = 1, column = 0, sticky = "nsew", columnspan = 2)

        self.longitude = tk.Label(self, text = "Longitude: ",bg = "black",
                                  fg = "tomato",font = ("helvetica", 15),
                                  bd = 2, highlightbackground = "black",
                                  activebackground = "black",
                                  activeforeground = "white")
        self.longitude.grid(row = 2, column = 0, sticky = "nsew", columnspan = 2)

        self.getposition = tk.Button(self, text = "  Get Position ",
                                     command = self.get_position, bg = "black",
                                     fg = "white",font = ("helvetica", 15),
                                     bd = 2, highlightbackground = "black",
                                     compound="left",activebackground ="black",
                                     activeforeground="white",image =icons[14])
        self.getposition.grid(row = 3, column = 0,columnspan = 2)
        
        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black", anchor = "center",\
                         command = self.goback)
        back.grid(row = 4, column = 0)
        
        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",
                  bd = 0,highlightbackground = "black", bg = "black",
                  activebackground = "black", command = self.gohome).\
                  grid(row = 4, column = 1)


    def get_position(self):
        """ Get coordinates """
        self.lattitude.config(text = "Lattitude: "+
                              str(phone.get_location()[0])+"°")
        self.longitude.config(text = "Longitude: "+
                              str(phone.get_location()[1])+"°")

    def goback(self):
        """ Go back to Menu1 Frame """
        self.lattitude.config(text = "Lattitude: ")
        self.longitude.config(text = "Longitude: ")
        self.controller.show_frame("Menu1Frame")

    def gohome(self):
        """ Go back to Home Frame """
        self.lattitude.config(text = "Lattitude: ")
        self.longitude.config(text = "Longitude: ")
        self.controller.show_frame("HomeFrame")

############################  TemplateFrame  ###################################
class TemplateFrame(tk.Frame):
    """ This class handle template frame """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame.config(self, bg="black")
        
        for i in range (2):
            self.grid_rowconfigure(i, weight =1)
            self.grid_columnconfigure(i, weight = 1)
        
        tk.Label(self, bg = "black", fg = "Deep sky blue",
                 text = "Develop\nyour apps here",
                 font = ("Helvetica", 30)).grid(row = 0, column = 0,
                                                columnspan = 2)
        
        back = tk.Button(self, text = "Back",image = icons[30],bd = 0,
                         highlightbackground = "black", bg = "black",
                         activebackground = "black", anchor = "center",
                         command=lambda:self.controller.show_frame("Menu2Frame"))
        back.grid(row = 1, column = 0)
        
        tk.Button(self, text = "Go Home", image = icons[16], anchor = "center",
                  bd = 0,highlightbackground = "black", bg = "black",
                  activebackground = "black",command = lambda:
                  self.controller.show_frame("Menu2Frame")).grid(row = 1,
                                                                 column = 1)
    

################################################################################
icons = []
Gframename = None
path = os.path.dirname(__file__)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        phone = pitalk.PiTalk('/dev/'+sys.argv[1], 115200)
        phone.connect()
    else:
        phone = pitalk.PiTalk('/dev/ttyS0', 115200)
        phone.connect()
    app = MainApp()
    app.mainloop()
