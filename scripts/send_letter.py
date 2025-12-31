#!/usr/bin/env python3
"""
Pixelletter API Client - Send physical letters via pixelletter.de

Usage:
    python send_letter.py --pdf /path/to/letter.pdf --destination DE
    python send_letter.py --pdf /path/to/letter.pdf --destination DE --test
    python send_letter.py --balance

Environment variables required:
    PIXELLETTER_EMAIL - Your pixelletter.de account email
    PIXELLETTER_PASSWORD - Your pixelletter.de account password
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


API_URL = "https://www.pixelletter.de/xml/index.php"

LOCATIONS = {
    "munich": "1",
    "vienna": "2",
    "hamburg": "3",
    "1": "1",
    "2": "2",
    "3": "3",
}


def get_credentials():
    """Get credentials from environment variables."""
    email = os.environ.get("PIXELLETTER_EMAIL")
    password = os.environ.get("PIXELLETTER_PASSWORD")

    if not email or not password:
        print("Error: PIXELLETTER_EMAIL and PIXELLETTER_PASSWORD environment variables must be set")
        sys.exit(1)

    return email, password


def build_auth_xml(email, password, test_mode=True):
    """Build the authentication XML block."""
    return f'''<auth>
        <email>{email}</email>
        <password>{password}</password>
        <agb>ja</agb>
        <widerrufsverzicht>ja</widerrufsverzicht>
        <testmodus>{"true" if test_mode else "false"}</testmodus>
        <ref></ref>
    </auth>'''


def send_pdf_letter(pdf_path, destination="DE", location="3", test_mode=True,
                    action="1", fax="", addoption=""):
    """
    Send a PDF as a physical letter.

    Args:
        pdf_path: Path to the PDF file
        destination: ISO country code (e.g., DE, AT, CH)
        location: Dispatch center (1=Munich, 2=Vienna, 3=Hamburg)
        test_mode: If True, order is simulated (no cost, not sent)
        action: 1=letter, 2=fax, 3=both
        fax: Fax number (required if action is 2 or 3)
        addoption: Special options (e.g., "27" for registered mail)

    Returns:
        Response text from API
    """
    email, password = get_credentials()

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    location = LOCATIONS.get(location.lower(), location)

    xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    {build_auth_xml(email, password, test_mode)}
    <command>
        <order type="upload">
            <options>
                <action>{action}</action>
                <transaction></transaction>
                <control></control>
                <fax>{fax}</fax>
                <location>{location}</location>
                <destination>{destination.upper()}</destination>
                <addoption>{addoption}</addoption>
                <returnaddress></returnaddress>
            </options>
        </order>
    </command>
</pixelletter>'''

    files = {
        "xml": (None, xml_payload, "text/xml"),
        "uploadfile0": (pdf_file.name, open(pdf_file, "rb"), "application/pdf")
    }

    response = requests.post(API_URL, files=files, timeout=60)
    return response.text


def send_text_letter(address, subject, message, destination="DE", location="3",
                     test_mode=True, addoption=""):
    """
    Send a text letter (auto-formatted by pixelletter).

    Args:
        address: Recipient address (multiline string)
        subject: Letter subject
        message: Letter body text
        destination: ISO country code
        location: Dispatch center
        test_mode: If True, simulated
        addoption: Special options

    Returns:
        Response text from API
    """
    email, password = get_credentials()
    location = LOCATIONS.get(location.lower(), location)

    # Escape XML special characters
    def escape_xml(text):
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

    xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    {build_auth_xml(email, password, test_mode)}
    <command>
        <order type="text">
            <options>
                <action>1</action>
                <transaction></transaction>
                <control></control>
                <fax></fax>
                <location>{location}</location>
                <destination>{destination.upper()}</destination>
                <addoption>{addoption}</addoption>
                <returnaddress></returnaddress>
            </options>
            <text>
                <address>{escape_xml(address)}</address>
                <subject>{escape_xml(subject)}</subject>
                <message>{escape_xml(message)}</message>
            </text>
        </order>
    </command>
</pixelletter>'''

    files = {"xml": (None, xml_payload, "text/xml")}
    response = requests.post(API_URL, files=files, timeout=60)
    return response.text


def check_balance():
    """Check account balance."""
    email, password = get_credentials()

    xml_payload = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pixelletter version="1.3">
    {build_auth_xml(email, password, test_mode=False)}
    <command>
        <info>
            <account:info type="all" />
        </info>
    </command>
</pixelletter>'''

    files = {"xml": (None, xml_payload, "text/xml")}
    response = requests.post(API_URL, files=files, timeout=60)
    return response.text


def main():
    parser = argparse.ArgumentParser(
        description="Send physical letters via pixelletter.de",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Send PDF letter (test mode):
    %(prog)s --pdf letter.pdf --destination DE --test

  Send PDF letter (real):
    %(prog)s --pdf letter.pdf --destination DE

  Send as registered mail:
    %(prog)s --pdf letter.pdf --destination DE --addoption 27

  Check account balance:
    %(prog)s --balance

  Send fax:
    %(prog)s --pdf document.pdf --action 2 --fax "+49 89 12345678"
"""
    )

    parser.add_argument("--pdf", help="Path to PDF file to send")
    parser.add_argument("--destination", default="DE",
                        help="Destination country ISO code (default: DE)")
    parser.add_argument("--location", default="3",
                        help="Dispatch center: 1=Munich, 2=Vienna, 3=Hamburg (default: 3)")
    parser.add_argument("--test", action="store_true",
                        help="Test mode - no cost, letter not actually sent")
    parser.add_argument("--action", default="1",
                        help="Action: 1=letter, 2=fax, 3=both (default: 1)")
    parser.add_argument("--fax", default="",
                        help="Fax number (required for action 2 or 3)")
    parser.add_argument("--addoption", default="",
                        help="Special options (e.g., 27 for registered mail)")
    parser.add_argument("--balance", action="store_true",
                        help="Check account balance")

    args = parser.parse_args()

    if args.balance:
        print("Checking account balance...")
        result = check_balance()
        print(result)
        return

    if not args.pdf:
        parser.print_help()
        sys.exit(1)

    print(f"Sending letter via pixelletter.de...")
    print(f"  PDF: {args.pdf}")
    print(f"  Destination: {args.destination}")
    print(f"  Location: {args.location}")
    print(f"  Test mode: {args.test}")
    if args.addoption:
        print(f"  Options: {args.addoption}")
    print()

    result = send_pdf_letter(
        pdf_path=args.pdf,
        destination=args.destination,
        location=args.location,
        test_mode=args.test,
        action=args.action,
        fax=args.fax,
        addoption=args.addoption
    )

    print("Response:")
    print(result)

    if "code=\"100\"" in result:
        print("\n✓ Order submitted successfully!")
        if args.test:
            print("  (Test mode - letter will NOT be sent)")
        else:
            print("  Letter will be printed and mailed. Check email for confirmation.")
    else:
        print("\n✗ Order failed - check response for details")


if __name__ == "__main__":
    main()
