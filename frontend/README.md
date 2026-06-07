# frontend — RAG Hex UI

[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss)](https://tailwindcss.com)

Interface utilisateur Next.js 15 pour le système RAG.

## Structure

```
frontend/
├── app/
│   ├── api/auth/       ← next-auth route handler
│   ├── chat/           ← Chat interface (page + layout)
│   ├── documents/      ← Document browser (list + detail [id])
│   ├── login/          ← Login page
│   ├── settings/       ← Settings page
│   ├── globals.css     ← Tailwind CSS v4
│   ├── layout.tsx      ← Root layout with SessionProvider
│   ├── middleware.ts   ← Auth middleware
│   └── page.tsx        ← Redirects to /chat
├── components/
│   ├── chat/           ← Chat components
│   ├── documents/      ← Document components
│   ├── layout/         ← SessionProvider, navigation
│   └── ui/             ← Radix UI primitives
└── lib/
    ├── api/            ← API client for backend
    ├── auth/           ← Auth helpers
    ├── hooks/          ← Custom React hooks
    ├── types/          ← TypeScript types
    └── utils.ts        ← Utility functions
```

## Pages

| Route             | Description                            |
| ----------------- | -------------------------------------- |
| `/chat`           | Interface de chat RAG (page d'accueil) |
| `/documents`      | Liste des documents ingérés            |
| `/documents/[id]` | Détail d'un document + ses chunks      |
| `/settings`       | Configuration utilisateur              |
| `/login`          | Authentification                       |

## Configuration

Voir `.env.example` :

```
NEXT_PUBLIC_API_URL=http://localhost:8000
AUTH_USERNAME=admin
AUTH_PASSWORD=changeme
AUTH_SECRET=change-me-to-a-random-secret
NEXTAUTH_URL=http://localhost:3000
```

## Commandes

```bash
npm run dev       # Dev server (localhost:3000)
npm run build     # Production build
npm run lint      # ESLint
npm run typecheck # tsc --noEmit
```

## Stack

- **Next.js 15** App Router with standalone output
- **TypeScript 5.7** strict with `noUncheckedIndexedAccess`
- **Tailwind CSS v4** via `@tailwindcss/postcss`
- **Radix UI** primitives (dialog, dropdown-menu, slot)
- **next-auth** for authentication
- **lucide-react** icons
- **Prettier** formatting (via pre-commit)

## Docker

```dockerfile
FROM node:22-slim
# Multi-stage build → standalone output
CMD ["node", "server.js"]
```

Le frontend est servi sur le port 3000, l'API backend sur le port 8000.
