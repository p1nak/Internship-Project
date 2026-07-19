# Rhino QR - Setup & User Guide

Welcome to the **Rhino QR Machine Documentation System**! This guide is written for complete beginners. Follow these step-by-step instructions to get the software running on your computer.

---

## 🛠️ Part 1: Initial Setup (Do this only once)

Before you can run the software, you need to prepare your computer.

### Step 1: Install Python
The system is built using Python. If you don't have it installed:
1. Go to the official website: [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest version for Windows.
3. **CRITICAL:** When running the installer, make sure to check the box that says **"Add Python to PATH"** at the very bottom of the window before clicking Install.

### Step 2: Open the Terminal
1. Open the folder where the QR Generator code is located (e.g., `Desktop\QR Generator`).
2. Click on the address bar at the top of the folder window.
3. Delete the text, type `cmd`, and press **Enter**. A black command prompt window will open.

### Step 3: Install Required Libraries
In the black command prompt window, type the following command exactly as shown and press Enter:
```cmd
pip install -r requirements.txt
```
*Wait a minute or two while it downloads all the necessary background files.*

---

## 🚀 Part 2: Running the System (Do this every day)

Whenever you want to use the system, follow these steps to turn it on:

### Step 1: Start the Server
1. Open the command prompt in your `QR Generator` folder (using the `cmd` trick from Step 2 above).
2. Type the following command and press Enter:
```cmd
python run.py
```
3. You will see some text appear saying `* Running on http://127.0.0.1:5000`. **Do not close this black window!** If you close it, the system will turn off.

### Step 2: Open in Your Browser
1. Open Google Chrome, Edge, or Firefox.
2. In the web address bar at the very top, type:
   **`http://127.0.0.1:5000`**
3. Press Enter. You should now see the Rhino QR login screen!

---

## 👤 Part 3: How to Log In

Once the website is open, you can log in using these default accounts:

- **Admin Account (Full Access):**
  - **Username:** `admin`
  - **Password:** `admin123`

- **Engineer Account:**
  - **Username:** `engineer`
  - **Password:** `eng123`

---

## 🛑 Part 4: How to Shut Down

When you are completely done for the day and want to turn the system off:
1. Go back to the black command prompt window.
2. Press **`Ctrl + C`** on your keyboard to stop the server.
3. You can now safely close the window.
