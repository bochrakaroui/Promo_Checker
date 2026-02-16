# PromoChecker Frontend

Modern, responsive web application for comparing laptop prices across Tunisian e-commerce stores.

## Features

- 🏠 **Products Page**: Browse all laptops with search, filter, and sort capabilities
- 💎 **Best Deals**: Discover products with the biggest price differences between stores
- 🏪 **Stores**: View all partner stores and their statistics
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- ⚡ **Fast & Modern**: Built with Next.js 14, React 19, and Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file (already created):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page (products listing)
│   ├── deals/             # Best deals page
│   ├── stores/            # Stores listing page
│   ├── products/          # Product detail pages
│   │   └── [productKey]/  # Dynamic product detail route
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # Reusable React components
│   └── ProductCard.tsx    # Product card component
├── lib/                   # Utilities and helpers
│   ├── api.ts            # API service layer
│   └── types.ts          # TypeScript type definitions
├── public/               # Static assets
└── next.config.ts        # Next.js configuration
```

## Pages

### 1. Products (`/`)
- Grid view of all laptops
- Search by name, brand, or specs
- Sort by price, name, brand, or availability
- Pagination
- Shows best price for each product

### 2. Best Deals (`/deals`)
- Products with biggest price differences
- Filter by minimum savings amount
- Detailed savings breakdown
- Side-by-side store comparison

### 3. Product Detail (`/products/[productKey]`)
- Full product specifications
- Price comparison across all stores
- Price history (if available)
- Savings calculator

### 4. Stores (`/stores`)
- List of all partner stores
- Statistics for each store
- Product count and average prices
- Direct links to store websites

## Technologies

- **Framework**: Next.js 14 with App Router
- **UI**: React 19
- **Styling**: Tailwind CSS 4
- **Language**: TypeScript 5
- **Image Optimization**: Next.js Image component
- **State Management**: React Hooks
- **API Communication**: Native Fetch API

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL (default: `http://localhost:8000`)

## API Integration

The frontend communicates with the FastAPI backend through the service layer in `lib/api.ts`. All API calls are typed with TypeScript interfaces defined in `lib/types.ts`.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
