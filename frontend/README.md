# PayPilot Frontend

Next.js + TypeScript + Tailwind CSS client for PayPilot, an AI-powered commerce agent.

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Design Aesthetic**: Minimalist Fintech / AI Dark Theme

## Directory Layout
```text
frontend/
├── app/              # Next.js App Router (pages and layouts)
│   ├── globals.css   # Global styles and Tailwind directives
│   ├── layout.tsx    # Root layout with metadata and fonts
│   └── page.tsx      # Main landing page
├── components/       # Reusable React components
│   └── Navbar.tsx    # Header navigation bar
├── lib/              # Utility functions
│   └── utils.ts      # Classnames helper
├── public/           # Static assets
├── package.json      # Dependencies and scripts
├── tsconfig.json     # TypeScript configuration
├── tailwind.config.ts# Tailwind CSS configuration
└── next.config.js    # Next.js configuration
```

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### 3. Build for Production
```bash
npm run build
npm run start
```
