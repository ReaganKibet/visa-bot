# 🚀 Visa Booking Instructions

## The Issue
Docker containers cannot display GUI applications (like browsers) because they don't have access to your computer's display server. This is why the browser wasn't opening when you clicked "Start Booking".

## The Solution
I've created a standalone booking script that runs on your local machine and opens a visible browser window.

## How to Use

### Step 1: Install Playwright (if not already installed)
```bash
pip install playwright
playwright install
```

### Step 2: Run the Booking Script
When you click "Start Booking" in the dashboard, you'll see instructions in the Docker logs. Then:

1. **Open a new terminal/command prompt**
2. **Navigate to your project directory**:
   ```bash
   cd C:\Users\Elitebook\OneDrive\Documents\PROJECTS\visa-bot
   ```
3. **Run the booking script**:
   ```bash
   python launch_booking.py
   ```

### Step 3: Complete the Booking
The script will:
- ✅ Launch a visible browser window
- ✅ Navigate to the VFS booking form
- ✅ Help you solve CAPTCHA
- ✅ Auto-fill your form data
- ✅ Wait for you to submit

## What You'll See

### In the Dashboard:
```
🚀 Booking session started for user_12345
```

### In Docker Logs:
```
🚀 BOOKING SESSION READY!
==========================================
Since you're running in Docker, please run the booking script on your host machine:

1. Open a new terminal/command prompt
2. Navigate to your project directory  
3. Run: python launch_booking.py

Your form data:
   first_name: John
   last_name: Doe
   dob: 1990-01-01
   passport: A12345678

The script will:
✅ Launch a visible browser window
✅ Navigate to the VFS booking form
✅ Help you solve CAPTCHA
✅ Auto-fill your form data
✅ Wait for you to submit
==========================================
```

### In the Booking Script:
```
🚀 Starting Visa Booking Session
==================================================
📝 Enter your details (or press Enter to use defaults):
First Name [John]: 
Last Name [Doe]: 
Date of Birth (YYYY-MM-DD) [1990-01-01]: 
Passport Number [A12345678]: 

✅ Using data: {'first_name': 'John', 'last_name': 'Doe', 'dob': '1990-01-01', 'passport': 'A12345678'}
🌐 Launching browser...

🚨 CAPTCHA DETECTED!
👉 Please solve the CAPTCHA in the browser window
👉 Complete any facial verification if required
👉 Press Enter when you're ready to continue

🛑 Press Enter after solving CAPTCHA...

✅ BOOKING SESSION READY!
👉 Review the form data in the browser
👉 Click 'Submit' or 'Book Appointment' when ready
👉 Press Enter when you've submitted the form

🛑 Press Enter after submitting the form...
✅ Booking session completed!
🔚 Browser closed
```

## Benefits of This Approach

1. **Visible Browser**: You can see and interact with the browser
2. **CAPTCHA Solving**: You can solve CAPTCHAs manually
3. **Form Review**: You can review and modify auto-filled data
4. **Full Control**: You control when to submit the form
5. **No Docker Issues**: Runs directly on your machine

## Troubleshooting

### If the script doesn't run:
```bash
# Make sure you have Python and Playwright installed
python --version
pip install playwright
playwright install
```

### If the browser doesn't open:
- Make sure you're running the script from your local machine (not in Docker)
- Check that Playwright is properly installed
- Try running with `python3` instead of `python`

### If you get permission errors:
- Run the terminal as administrator (Windows) or with sudo (Linux/Mac)

## Summary

This approach gives you the best of both worlds:
- **Monitoring runs in Docker** (24/7, reliable)
- **Booking runs locally** (visible browser, full control)

The system will continue monitoring for slots in the background while you handle the booking process manually when slots become available.
