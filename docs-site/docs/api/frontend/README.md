**Stock Screening Platform - Frontend API v0.1.0**

***

# Stock Screening Platform - Frontend

React-based frontend application for Korean stock market (KOSPI/KOSDAQ) screening platform.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Routing**: React Router v6
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **UI Components**: Radix UI
- **Styling**: Tailwind CSS
- **Charts**: Lightweight Charts, Recharts
- **Forms**: React Hook Form
- **Date Handling**: date-fns

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components (routes)
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API clients and services
│   ├── store/          # Zustand stores
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript type definitions
│   ├── assets/         # Static assets
│   ├── App.tsx         # Root component
│   ├── main.tsx        # Application entry point
│   ├── router.tsx      # Route definitions
│   └── index.css       # Global styles
├── public/             # Public static files
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
├── tailwind.config.js  # Tailwind CSS configuration
├── .eslintrc.json      # ESLint configuration
├── .prettierrc         # Prettier configuration
└── package.json        # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js >= 18
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
```

### Development

```bash
# Start development server
npm run dev

# Development server will be available at:
# http://localhost:5173
```

### Building

```bash
# Type check
npm run type-check

# Lint code
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

## Available Routes

- `/` - Home page
- `/screener` - Stock screener (to be implemented in FE-003)
- `/stocks/:code` - Stock detail page (to be implemented in FE-004)
- `/login` - Login page (to be implemented in FE-002)
- `/register` - Register page (to be implemented in FE-002)

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

## Code Quality

### TypeScript

- Strict mode enabled
- Path aliases: `@/*` maps to `src/*`

### ESLint

- TypeScript ESLint
- React recommended rules
- React Hooks rules
- Prettier integration

### Prettier

- Single quotes
- No semicolons
- 2 space indentation
- Trailing commas

## State Management

### Zustand Stores

- `authStore` - Authentication state (user, tokens)
- More stores will be added as needed

### React Query

- Configured with 5-minute stale time
- Automatic retry on failure
- No refetch on window focus

## API Integration

### Axios Instance

Configured in `src/services/api.ts`:

- Base URL from environment variable
- 10-second timeout
- Automatic auth token injection
- 401 redirect to login

## Development Guidelines

1. **TypeScript**: Use strict typing, avoid `any`
2. **Components**: Functional components with hooks
3. **Styling**: Tailwind CSS utility classes
4. **State**: Zustand for global state, useState for local
5. **Data Fetching**: React Query for server state
6. **Forms**: React Hook Form with validation
7. **Code Style**: Follow ESLint and Prettier rules

## Next Steps

- **FE-002**: Implement authentication pages (Login, Register)
- **FE-003**: Build stock screener page with filters
- **FE-004**: Create stock detail page with charts
- **FE-005**: Add order book visualization

## License

Private - All rights reserved
