[**Stock Screening Platform - Frontend API v0.1.0**](../../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../../modules.md) / [components/stock/MetricCard](../README.md) / default

# Function: default()

> **default**(`__namedParameters`): `Element`

Defined in: [src/components/stock/MetricCard.tsx:42](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/components/stock/MetricCard.tsx#L42)

Metric Card Component

Displays a single financial/technical metric with label, value, and optional tooltip

Features:
- Formatted value display
- Color coding (positive/negative)
- Tooltip with explanation
- Responsive design

## Parameters

### \_\_namedParameters

`MetricCardProps`

## Returns

`Element`

## Example

```tsx
<MetricCard
  label="PER"
  value={12.5}
  unit="배"
  tooltip="주가수익비율: 주가 / 주당순이익"
  variant="positive"
/>
```
