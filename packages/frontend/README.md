# Frontend - Internship Chatbot

This is the frontend application for the Internship Chatbot, built with React, TypeScript, and Vite.

## Features

- Modern React with TypeScript
- Tailwind CSS for styling
- Real-time chat interface
- User authentication and session management
- Responsive design

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library

## Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```
   
   Required environment variables:
   - `VITE_FLASK_BACKEND_URL` - Backend API URL (default: http://localhost:5000)

3. **Run Development Server**:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Reusable UI components
│   ├── Chatbot.tsx     # Main chatbot component
│   └── ChatMessageBubble.tsx  # Chat message display
├── App.tsx             # Main app component
├── main.tsx            # App entry point
└── App.css             # Global styles
```

## Key Components

### Chatbot Component
The main chat interface that handles:
- User registration/verification
- Message sending and receiving
- Session management with localStorage
- API communication with the backend

### ChatMessageBubble Component
Displays individual chat messages with:
- User/bot message styling
- Suggestion buttons for quick actions
- Loading indicators

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist` directory.

## Deployment

The built files in `dist` can be served by any static file hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

## Development Notes

- The app uses Vite's environment variable system (prefixed with `VITE_`)
- User sessions are stored in localStorage with a 3-day expiry
- All API calls go through the configured backend URL
- The chat interface is responsive and works on mobile devices
