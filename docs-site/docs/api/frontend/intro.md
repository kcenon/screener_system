# Frontend Components Reference

The frontend is built with React and TypeScript, providing reusable components for stock market analysis.

## Component Library

### Data Display Components

#### StockTable
Displays a filterable, sortable table of stocks.

```tsx
import { StockTable } from '@/components/StockTable';

function MyComponent() {
  return (
    <StockTable
      stocks={stocks}
      columns={['code', 'name', 'price', 'change']}
      onRowClick={(stock) => navigate(`/stocks/${stock.code}`)}
    />
  );
}
```

#### StockChart
Renders interactive price charts with technical indicators.

```tsx
import { StockChart } from '@/components/StockChart';

function MyComponent() {
  return (
    <StockChart
      stockCode="005930"
      period="1y"
      indicators={['MA20', 'MA60', 'RSI', 'MACD']}
      height={400}
    />
  );
}
```

### Screening Components

#### ScreenBuilder
Interactive stock screening filter builder.

```tsx
import { ScreenBuilder } from '@/components/ScreenBuilder';

function MyComponent() {
  const handleScreen = (filters) => {
    // Send to API
    screenStocks(filters);
  };

  return (
    <ScreenBuilder
      onApply={handleScreen}
      presets={savedPresets}
    />
  );
}
```

### Portfolio Components

#### PortfolioSummary
Displays portfolio performance and holdings.

```tsx
import { PortfolioSummary } from '@/components/PortfolioSummary';

function MyComponent() {
  return (
    <PortfolioSummary
      holdings={userHoldings}
      benchmark="KOSPI"
      period="1M"
    />
  );
}
```

## State Management

The app uses Zustand for state management:

```tsx
import { useStockStore } from '@/stores/stockStore';

function MyComponent() {
  const { stocks, fetchStocks, isLoading } = useStockStore();

  useEffect(() => {
    fetchStocks();
  }, []);

  if (isLoading) return <Loading />;

  return <StockTable stocks={stocks} />;
}
```

## Data Fetching

TanStack Query (React Query) is used for server state:

```tsx
import { useQuery } from '@tanstack/react-query';
import { stockApi } from '@/api/stocks';

function MyComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['stock', code],
    queryFn: () => stockApi.getStock(code),
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return <StockDetails stock={data} />;
}
```

## Styling

Components use Tailwind CSS and Radix UI:

```tsx
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardContent } from '@/components/ui/card';

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <h2 className="text-2xl font-bold">Stock Analysis</h2>
      </CardHeader>
      <CardContent>
        <Button variant="primary" onClick={handleClick}>
          Add to Watchlist
        </Button>
      </CardContent>
    </Card>
  );
}
```

## Type Definitions

TypeScript interfaces for stock data:

```tsx
interface Stock {
  code: string;
  name: string;
  market: 'KOSPI' | 'KOSDAQ';
  price: number;
  change: number;
  changePercent: number;
  volume: number;
}

interface FinancialRatios {
  per: number;
  pbr: number;
  roe: number;
  roa: number;
  debtRatio: number;
}
```

## Next Steps

- [Component API Reference](/docs/api/frontend/components)
- [State Management Guide](/docs/api/frontend/state)
- [Custom Hooks](/docs/api/frontend/hooks)
- [Styling Guidelines](/docs/guides/styling)
