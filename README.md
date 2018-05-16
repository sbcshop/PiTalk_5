# PiTalk_5

Modular Smartphone on Raspberry Pi.

<img src="http://sb-components.co.uk/assets/images/portfolio/pitalk.png" width="300"><img src="http://pitalk.co.uk/images/apple-watch.png" width="300">

**Steps for PiTalk software installation -** 

1. Open Terminal and download the code by writing: 
   ```
   git clone https://github.com/sbcshop/PiTalk_5.git
   ```

2. Your code will be downloaded to '/home/pi' directory. Use 'ls' command to check the list of directories.

3. Go to directory 'PiTalk_5' and run the command to change the permissions:
   ```
   sudo chmod +x setup
   ```
   and then run 'setup', but make sure Raspberry Pi is connected to Internet.
   ```
   sudo ./setup
   ```
   It will reboot your Raspberry Pi

4. Go to directoy 'PiTalk_5' and you will see there are two GUI files i.e. GUI5_Landscape.py and GUI5_Portrait.py. As its name indicates    it will create PiTalk GUI in Landscape and Portrait mode.

5. Lets run the PiTalk code (Landscape or Portrait Mode). Open the terminal and write:

   For Raspberry Pi 3 or 3B+ use 'ttyS0' if PiTalk is connected through GPIO or 'ttyUSB3' if connected through USB
   ```
   sudo python3 ./GUI5_Landscape.py ttyS0
   ```
   For other version use 'ttyAMA0' if connected through GPIO or 'ttyUSB3' if connected throught USB
   or 
   ```
   sudo python3 ./GUI5_Portrait.py ttyAMA0
   ```
   **Note**: Default it will take 'ttyS0' port. It means if you simply write :
   ```
   sudo python3 ./GUI5_Portrait.py
   ```
   or 
   ```
   sudo python3 ./GUI5_Landscape.py
   ```
   It will also work but for Raspberry Pi 3 or 3B+ only.
   
6. This will run PiTalk code on HDMI screen. If you want to run this code on 5" LCD, go to 'setting' app and go to 'Screen Orientation'.
   You will see diffrent orientation at different angles. Click to any angle will reboot your Raspberry Pi and start GUI on 5" LCD.
   
7. Now to run the PiTalk code on 5" LCD, repeat **Step 5** 


For more details, go to http://pitalk.co.uk/

For blogs and projects, go to http://sb-components.co.uk/pitalk-blog.html

Go to https://shop.sb-components.co.uk/ to order your PiTalk now

