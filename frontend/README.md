# SVA Visualizer Frontend

React-based frontend for the Subject-Verb Agreement Visualizer with D3.js parse tree visualization.

## Features

- Interactive sentence input with real-time analysis
- Parse tree visualization using D3.js
- Step-by-step derivation display
- Problem span highlighting
- Example sentences for quick testing

## Setup

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:5000`

### Installation

```powershell
cd frontend
npm install
```

### Development

```powershell
npm start
```

Opens the app at `http://localhost:3000`. The proxy is configured to forward API requests to the Flask backend at `http://localhost:5000`.

### Build for Production

```powershell
npm run build
```

Creates an optimized production build in the `build/` directory.

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── ParseTreeVisualizer.js   # D3 tree visualization
│   │   ├── ParseTreeVisualizer.css
│   │   ├── DerivationSteps.js       # Derivation step display
│   │   └── DerivationSteps.css
│   ├── App.js              # Main application component
│   ├── App.css             # Application styles
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
└── package.json            # Dependencies and scripts
```

## Usage

1. Start the Flask backend:
   ```powershell
   cd backend
   python app.py
   ```

2. Start the React frontend:
   ```powershell
   cd frontend
   npm start
   ```

3. Open `http://localhost:3000` in your browser.

4. Enter a sentence or click an example, then click "Analyze".

5. View the parse tree, problem spans, and derivation steps.

## Example Sentences

- "The cats runs." → Detects plural/singular mismatch
- "The cat and the dog runs." → Detects coordination mismatch
- "They don't run." → Handles contractions and pronouns
- "He runs fast." → Accepts correct singular agreement
- "The children plays." → Detects irregular plural mismatch

## Technologies

- **React 18** — UI framework
- **D3.js 7** — Tree visualization
- **Axios** — HTTP client for API requests
- **CSS3** — Styling with modern flexbox/grid
