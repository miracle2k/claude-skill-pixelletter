# Pixelletter Post Skill for Claude Code

A Claude Code skill that provides knowledge about sending physical letters and faxes via the [pixelletter.de](https://www.pixelletter.de) API. They print, envelope, and mail your documents as real postal mail.

## Features

- **PDF Letters**: Upload PDF documents to be printed and mailed
- **Text Letters**: Send plain text letters (auto-formatted by pixelletter)
- **Fax**: Send documents via fax
- **Registered Mail**: Support for Einschreiben and other special delivery options
- **Multiple Files**: Combine multiple documents into one letter
- **Test Mode**: Verify everything works before spending money

## Installation

Run the install script:
```bash
./install.sh
```

Or manually copy the `.claude/skills` directory to your home directory:
```bash
mkdir -p ~/.claude/skills
cp .claude/skills/pixelletter.md ~/.claude/skills/
```

Then set your Pixelletter credentials as environment variables in your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export PIXELLETTER_EMAIL="your-email@example.com"
export PIXELLETTER_PASSWORD="your-password"
```

To get credentials:
- Register at [pixelletter.de](https://www.pixelletter.de/de/new.php)
- Add credit to your account

## Usage

Once installed, Claude Code will automatically have knowledge about the pixelletter.de API. Just ask Claude to:

- "Send this PDF as a letter to Germany"
- "Create a payment reminder letter and mail it via pixelletter"
- "Check my pixelletter account balance"
- "Send this document as registered mail"
- "Fax this PDF to +49 89 12345678"

## PDF Requirements

For PDF uploads, the recipient address must be positioned in the DIN-lang envelope address window area (approximately 45mm from top). Pixelletter automatically detects the address from this position.

## API Operations

| Operation | Description |
|-----------|-------------|
| Send PDF | Upload and mail a PDF document |
| Send Text | Mail auto-formatted text letter |
| Send Fax | Fax a document |
| Check Balance | View account credit |
| Registered Mail | Send with tracking/signature |

## Delivery Options

| Option | Code | Description |
|--------|------|-------------|
| Standard | - | Regular mail |
| Einschreiben | 27 | Registered mail |
| Rückschein | 27,28 | With return receipt |
| Eigenhändig | 27,29 | Personal delivery only |
| Einwurf | 30 | Registered with drop-off |

## Dispatch Locations

| Location | Code |
|----------|------|
| Munich, Germany | 1 |
| Vienna, Austria | 2 |
| Hamburg, Germany | 3 |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PIXELLETTER_EMAIL` | Yes | Your pixelletter.de account email |
| `PIXELLETTER_PASSWORD` | Yes | Your pixelletter.de account password |

## Helper Script

A Python helper script is included at `scripts/send_letter.py` for standalone use:

```bash
python scripts/send_letter.py --pdf /path/to/letter.pdf --destination DE --test
```

## License

MIT
