# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- `npm run dev` - Start development server with Turbopack (opens at http://localhost:3000)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint for code quality checks

## Architecture Overview

This is a Next.js 15.3.4 application using the App Router architecture with TypeScript and React 19. The project follows a modern React/Next.js structure:

### Key Technologies
- **Framework**: Next.js 15.3.4 with App Router
- **Language**: TypeScript with strict mode enabled
- **Styling**: Tailwind CSS v4 with shadcn/ui components (New York style)
- **Animation**: Motion library for animations
- **Icons**: Lucide React
- **Development**: Turbopack for fast development builds

### Directory Structure
- `app/` - Next.js App Router pages and layouts
  - `layout.tsx` - Root layout with Geist fonts
  - `page.tsx` - Home page component
  - `globals.css` - Global Tailwind styles
- `lib/` - Utility functions
  - `utils.ts` - Contains `cn()` utility for class merging (clsx + tailwind-merge)
- `components/` - Reusable UI components (shadcn/ui structure)
  - `ui/` - Base UI components
- `public/` - Static assets

### Import Aliases
- `@/*` maps to root directory
- `@/components` for components
- `@/lib` for utilities
- `@/ui` for UI components
- `@/hooks` for custom hooks

### Component System
The project uses shadcn/ui with:
- New York style variant
- CSS variables for theming
- Neutral base color
- RSC (React Server Components) enabled
- Lucide icons as the icon library

### TypeScript Configuration
- Strict mode enabled
- Path aliases configured for clean imports
- ES2017 target with modern module resolution