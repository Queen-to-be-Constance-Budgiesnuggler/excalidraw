# Excalidraw Local Setup Guide

This guide shows how to run a local instance of Excalidraw and share it securely using ngrok.

## Prerequisites

- **Node.js** 14+
- **npm** or **yarn**
- **ngrok** (for public access)

## 1. Clone the Repository

```bash
git clone https://github.com/Queen-to-be-Constance-Budgiesnuggler/excalidraw.git
cd excalidraw
```

## 2. Install Dependencies

```bash
npm install
# or
# yarn install
```

## 3. Start the Server

```bash
npm run start
```

Press Ctrl+C to stop the server when finished.

Visit <http://localhost:3000> in your browser.

## 4. Expose via ngrok

In a new terminal, authenticate if needed:

```bash
ngrok authtoken YOUR_NGROK_TOKEN
```

Start a tunnel to port `3000`:

```bash
ngrok http 3000
```

Share the generated HTTPS forwarding URL to give others access.
