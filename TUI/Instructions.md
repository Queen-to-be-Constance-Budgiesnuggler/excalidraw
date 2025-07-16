# Excaliman Session Manager

A GPU-friendly terminal interface for Kitty that controls an Excalidraw collaboration room and shares it through ngrok.

## Prerequisites

- **Python** 3.8+
- **pip**
- **textual** (or **tui-kit**)
- **pyngrok**

## 1. Clone the Repository

```bash
git clone https://github.com/Queen-to-be-Constance-Budgiesnuggler/excalidraw-room.git
cd excalidraw-room
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Create a `.env` file:

```
EXCALIDRAW_URL=http://localhost:3000
PORT=4000
NGROK_AUTH_TOKEN=your_token_here
```

## 4. Launch the TUI Manager

```bash
python excalimanTUI.py
```

### TUI Controls

- **s** — Start server and ngrok tunnel
- **t** — Toggle tunnel
- **x** — Stop
- **q** — Quit

The public URL appears under **🌐 Public URL:** in the interface.
