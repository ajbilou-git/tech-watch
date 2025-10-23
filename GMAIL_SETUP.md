# 📧 Gmail Setup Guide for Tech Watch

Follow these steps to configure email sending via Gmail.

## Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left menu
3. Under "Signing in to Google", enable **2-Step Verification**
4. Follow the setup process

## Step 2: Generate an App Password

1. Go to: https://myaccount.google.com/apppasswords
2. If you don't see this option, make sure 2-Step Verification is enabled
3. In the "Select app" dropdown, choose **Mail**
4. In the "Select device" dropdown, choose **Windows Computer** (or Other)
5. Click **Generate**
6. Google will display a 16-character password like: `xxxx xxxx xxxx xxxx`
7. **Copy this password** (you won't see it again!)

## Step 3: Configure config.yaml

Open `tech-watch/config.yaml` and fill in your credentials:

```yaml
email:
  to: "abdelhadi.jbilou@gmail.com"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  smtp_username: "abdelhadi.jbilou@gmail.com"  # Your full Gmail address
  smtp_password: "xxxx xxxx xxxx xxxx"          # The 16-char App Password
  from_email: ""                                 # Optional
```

**Important Notes:**
- ✅ Use the **App Password**, NOT your regular Gmail password
- ✅ The App Password is 16 characters (with or without spaces)
- ✅ Keep your App Password secure (don't share it)
- ❌ Don't use your regular Gmail password (it won't work!)

## Step 4: Test Email Sending

Run the tech watch script:

```powershell
.\run_tech_watch.ps1 -OpenReport
```

You should see:
```
Sending email to abdelhadi.jbilou@gmail.com...
Email sent successfully to abdelhadi.jbilou@gmail.com!
```

Check your inbox at `abdelhadi.jbilou@gmail.com` for the HTML report!

## Troubleshooting

### Error: "Email authentication failed"
- ✅ Make sure you're using an **App Password**, not your regular password
- ✅ Check that 2-Step Verification is enabled
- ✅ Regenerate a new App Password if needed

### Error: "SMTPAuthenticationError: Username and Password not accepted"
- ✅ Double-check the email address in `smtp_username`
- ✅ Make sure there are no extra spaces in the password
- ✅ Try removing spaces from the App Password: `xxxxxxxxxxxxxxxx`

### Error: "Connection refused" or "timed out"
- ✅ Check your internet connection
- ✅ Make sure port 587 is not blocked by your firewall
- ✅ Verify `smtp_server: "smtp.gmail.com"` is correct

### No email received
- ✅ Check your Spam/Junk folder
- ✅ Wait a few minutes (Gmail can be slow sometimes)
- ✅ Verify the email address in the `to:` field

## Security Best Practices

1. **Don't commit passwords to Git**
   - The `.gitignore` already excludes `config.local.yaml`
   - Consider using `config.local.yaml` for sensitive data

2. **Revoke App Passwords you don't use**
   - Go to: https://myaccount.google.com/apppasswords
   - Remove any unused App Passwords

3. **Use a dedicated email for automation**
   - Consider creating a separate Gmail account for automated reports

## Disable Email Sending

To stop receiving emails, simply clear the SMTP credentials in `config.yaml`:

```yaml
email:
  to: "abdelhadi.jbilou@gmail.com"
  smtp_server: ""
  smtp_port: 587
  smtp_username: ""
  smtp_password: ""
```

The script will skip email sending and only save the report locally.

---

**Ready to configure?** Edit `config.yaml` and run the script! 🚀
