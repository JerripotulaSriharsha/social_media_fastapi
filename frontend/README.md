# Social Media App - Frontend

A modern social media application built with React, TypeScript, and TailwindCSS.

## Features

- 🔐 User authentication (Login/Register)
- 📸 Upload images and videos
- ✏️ Edit and delete posts
- 📱 Responsive design
- 🎨 Modern UI with TailwindCSS

## Tech Stack

- **React** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Router** - Routing

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

### Building for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   │   ├── CreatePost.tsx
│   │   └── PostCard.tsx
│   ├── pages/          # Page components
│   │   ├── Auth.tsx
│   │   └── Home.tsx
│   ├── services/       # API services
│   │   └── api.ts
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before starting the frontend.

### Available Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /upload` - Upload post
- `GET /feed` - Get all posts
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post

## Environment Variables

Create a `.env` file if you need to customize the API URL:

```
VITE_API_URL=http://localhost:8000
```
