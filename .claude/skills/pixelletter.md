# Pixelletter Post API Skill

You are now operating as a postal mail assistant using the pixelletter.de service. This skill enables sending physical letters and faxes via their API - they print, envelope, and mail documents for you.

---

## Authentication

The Pixelletter API uses XML-based authentication embedded in each request.

**Required Environment Variables**:
- `PIXELLETTER_EMAIL` - Your pixelletter.de account email
- `PIXELLETTER_PASSWORD` - Your pixelletter.de account password

Before making any API calls, verify credentials are available:
```bash
if [ -z "$PIXELLETTER_EMAIL" ] || [ -z "$PIXELLETTER_PASSWORD" ]; then
  echo "Error: PIXELLETTER_EMAIL and PIXELLETTER_PASSWORD environment variables must be set"
  exit 1
fi
```

**API Endpoint**: `https://www.pixelletter.de/xml/index.php`

To get credentials: Register at https://www.pixelletter.de/de/new.php

---

## Core Concepts

### Action Types
- `1` = Letter only (postal mail)
- `2` = Fax only
- `3` = Letter and fax

### Dispatch Locations
- `1` = Munich, Germany (default)
- `2` = Hausleiten, Austria
- `3` = Hamburg, Germany

### Destination Codes
Two-letter ISO country codes: `DE` (Germany), `AT` (Austria), `CH` (Switzerland), etc.

### Test Mode
- `true` = Test mode - order is processed but NOT printed/sent, no cost
- `false` = Real mode - letter will be printed and mailed, costs money

**Always test first before sending real mail!**

---

## Sending a PDF Letter

### Python Script Method (Recommended)

Create and run this Python script to send a PDF:

```python
#!/usr/bin/env python3
"""Send a letter via pixelletter.de API"""

import os
import requests
from pathlib import Path

# Get credentials from environment
EMAIL = os.environ.get("PIXELLETTER_EMAIL")
PASSWORD = os.environ.get("PIXELLETTER_PASSWORD")

# Settings
TEST_MODE = True  # Set to False for real delivery
ACTION = "1"      # 1 = letter only
LOCATION = "3"    # 3 = Hamburg
DESTINATION = "DE"

# File to send
PDF_PATH = "/path/to/your/letter.pdf"

def send_letter():
    url = "https://www.pixelletter.de/xml/index.php"

    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        print(f"Error: PDF not found: {PDF_PATH}")
        return

    xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    <auth>
        <email>{EMAIL}</email>
        <password>{PASSWORD}</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>{"true" if TEST_MODE else "false"}</testmodus>
        <ref></ref>
    </auth>
    <command>
        <order type="upload">
            <options>
                <action>{ACTION}</action>
                <transaction></transaction>
                <control></control>
                <fax></fax>
                <location>{LOCATION}</location>
                <destination>{DESTINATION}</destination>
                <addoption></addoption>
                <returnaddress></returnaddress>
            </options>
        </order>
    </command>
</pixelletter>'''

    files = {
        "xml": (None, xml_payload, "text/xml"),
        "uploadfile0": (pdf_file.name, open(pdf_file, "rb"), "application/pdf")
    }

    print(f"Sending letter via pixelletter.de...")
    print(f"  Test mode: {TEST_MODE}")
    print(f"  File: {pdf_file.name}")

    response = requests.post(url, files=files, timeout=60)
    print(f"Response: {response.text}")

if __name__ == "__main__":
    send_letter()
```

### Curl Method

```bash
# Create XML payload file first
cat > /tmp/pixelletter_request.xml << 'XMLEOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    <auth>
        <email>YOUR_EMAIL</email>
        <password>YOUR_PASSWORD</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>true</testmodus>
        <ref></ref>
    </auth>
    <command>
        <order type="upload">
            <options>
                <action>1</action>
                <transaction></transaction>
                <control></control>
                <fax></fax>
                <location>3</location>
                <destination>DE</destination>
                <addoption></addoption>
                <returnaddress></returnaddress>
            </options>
        </order>
    </command>
</pixelletter>
XMLEOF

# Send the request
curl -X POST "https://www.pixelletter.de/xml/index.php" \
  -F "xml=</tmp/pixelletter_request.xml" \
  -F "uploadfile0=@/path/to/letter.pdf"
```

---

## Sending a Text Letter (No PDF Required)

For simple text letters, pixelletter formats the document automatically:

```python
xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    <auth>
        <email>{EMAIL}</email>
        <password>{PASSWORD}</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>true</testmodus>
        <ref></ref>
    </auth>
    <command>
        <order type="text">
            <options>
                <action>1</action>
                <transaction></transaction>
                <control></control>
                <fax></fax>
                <location>3</location>
                <destination>DE</destination>
                <addoption></addoption>
                <returnaddress></returnaddress>
            </options>
            <text>
                <address>
                Erika Mustermann
                Musterstr. 28
                D-81237 Musterstadt
                </address>
                <subject>Betreff des Briefes</subject>
                <message>
                Sehr geehrte Frau Mustermann,

                hier kommt der Brieftext...

                Mit freundlichen Grüßen
                Ihr Name
                </message>
            </text>
        </order>
    </command>
</pixelletter>'''

# For text orders, no file upload needed:
files = {"xml": (None, xml_payload, "text/xml")}
response = requests.post(url, files=files, timeout=60)
```

---

## PDF Requirements for Upload

**CRITICAL: Address Window Positioning**

The recipient address MUST be visible in the DIN-lang envelope address window:
- Position: approximately 45mm from top, 20mm from left margin
- The address must be the FIRST readable text block in that area
- Pixelletter automatically detects the address from this position

**Recommended PDF Layout:**

```
┌─────────────────────────────────────┐
│                                     │
│  Absender · Straße · PLZ Ort       │  ← Small sender line (8pt)
│  ─────────────────────────────────  │  ← Separator
│  Empfängername                      │  ← Address window area
│  Straße Hausnummer                  │    (detected by pixelletter)
│  PLZ Ort                            │
│  Land                               │
│                                     │
│                         Datum       │
│                                     │
│  Betreff                            │
│                                     │
│  Sehr geehrte...                    │
│                                     │
│  Brieftext...                       │
│                                     │
│  Mit freundlichen Grüßen            │
│  Unterschrift                       │
└─────────────────────────────────────┘
```

**Supported File Formats:**
- PDF (.pdf) - recommended
- Word (.doc)
- Excel (.xls)
- PowerPoint (.ppt)
- RTF (.rtf)
- WordPerfect (.wpd)
- Photoshop (.psd)

---

## Special Options (Registered Mail)

Use the `addoption` field for special delivery options:

| Code | Description |
|------|-------------|
| `27` | Einschreiben (Registered mail) |
| `28` | Rückschein (Return receipt) - requires 27 |
| `29` | Eigenhändig (Personal delivery) - requires 27 |
| `30` | Einschreiben Einwurf (Registered mail with drop-off) |

**Examples:**
```xml
<addoption>27</addoption>           <!-- Basic registered mail -->
<addoption>27,28</addoption>        <!-- Registered with return receipt -->
<addoption>27,29</addoption>        <!-- Registered, personal delivery -->
<addoption>27,28,29</addoption>     <!-- All options -->
<addoption>30</addoption>           <!-- Einwurf only (not combinable) -->
```

**Note:** Registered mail only available within Germany.

---

## Sending a Fax

```python
xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    <auth>
        <email>{EMAIL}</email>
        <password>{PASSWORD}</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>true</testmodus>
        <ref></ref>
    </auth>
    <command>
        <order type="upload">
            <options>
                <action>2</action>
                <transaction></transaction>
                <control></control>
                <fax>+49 89 12345678</fax>
                <location>3</location>
                <destination>DE</destination>
                <addoption></addoption>
                <returnaddress></returnaddress>
            </options>
        </order>
    </command>
</pixelletter>'''
```

**Fax number format:** Always use international format: `+49 89 12345678`

---

## Check Account Info / Credit Balance

```python
xml_payload = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    <auth>
        <email>{EMAIL}</email>
        <password>{PASSWORD}</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>false</testmodus>
        <ref></ref>
    </auth>
    <command>
        <info>
            <account:info type="all" />
        </info>
    </command>
</pixelletter>'''

files = {"xml": (None, xml_payload, "text/xml")}
response = requests.post("https://www.pixelletter.de/xml/index.php", files=files)
print(response.text)
```

Response includes credit balance:
```xml
<costumer:credit currency="EUR">27.20</costumer:credit>
```

---

## API Response Format

### Success Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<pixelletter version="1.1">
  <response>
    <result code="100">
      <msg>Auftrag erfolgreich übermittelt.</msg>
      <id>15326349</id>
    </result>
  </response>
</pixelletter>
```

### Error Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<pixelletter version="1.1">
  <response>
    <result code="009">
      <msg>Error description here</msg>
    </result>
  </response>
</pixelletter>
```

### Common Error Codes
- `009` - Missing required field
- `100` - Success
- `401` - Authentication failed

Full error list: https://www.pixelletter.de/docs/error_messages.php

---

## Workflow: Creating and Sending a Letter

### Step 1: Create the PDF with Correct Layout

Generate an HTML file with proper DIN-format layout, then convert to PDF:

```bash
# Using Chrome headless to create PDF
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf="/path/to/output.pdf" \
  --no-pdf-header-footer \
  "/path/to/letter.html"
```

### Step 2: Test the Upload (Test Mode)

Always send in test mode first to verify the address is detected correctly:
```python
TEST_MODE = True
# ... send letter ...
```

Check your pixelletter.de account to verify the detected address.

### Step 3: Send for Real

Once confirmed, set `TEST_MODE = False` and send again.

### Step 4: Wait for Confirmation

You'll receive an email confirmation within hours confirming:
- Address was correctly positioned in window
- Letter will be printed and mailed

---

## Multiple Files

You can upload multiple files that will be combined:

```python
files = {
    "xml": (None, xml_payload, "text/xml"),
    "uploadfile0": ("page1.pdf", open("page1.pdf", "rb"), "application/pdf"),
    "uploadfile1": ("page2.pdf", open("page2.pdf", "rb"), "application/pdf"),
    "uploadfile2": ("attachment.pdf", open("attachment.pdf", "rb"), "application/pdf")
}
```

---

## Important Notes

1. **Agreement Fields**: `agb` and `widerrufsverzicht` must be `ja` for orders to process immediately
2. **Country Required**: Always include country in address and set `destination` correctly
3. **Email Confirmation**: Real orders trigger email confirmation within hours
4. **Credit System**: Pixelletter uses prepaid credit - check balance before sending
5. **Address Detection**: If address detection fails, you'll be notified via email
6. **No HTML in Text**: When using text mode, don't include HTML tags

---

## Quick Reference

| Task | Action | Type |
|------|--------|------|
| Send PDF letter | `action=1` | `type="upload"` |
| Send text letter | `action=1` | `type="text"` |
| Send fax | `action=2` | `type="upload"` |
| Letter + fax | `action=3` | `type="upload"` |
| Check balance | - | `<account:info>` |

| Location | Code |
|----------|------|
| Munich | `1` |
| Vienna | `2` |
| Hamburg | `3` |
