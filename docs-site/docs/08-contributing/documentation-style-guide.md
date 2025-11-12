---
id: documentation-style-guide
title: Documentation Style Guide
description: Writing standards and conventions for all project documentation
sidebar_label: Style Guide
sidebar_position: 1
tags:
  - contributing
  - documentation
  - standards
---

# Documentation Style Guide

This guide defines writing standards and conventions for all documentation in the Stock Screening Platform project.

## Writing Principles

### 1. Clarity First

- **Use simple language**: Prefer "use" over "utilize", "help" over "facilitate"
- **Be concise**: Remove unnecessary words without losing meaning
- **Be specific**: Provide concrete examples rather than abstract descriptions
- **One idea per sentence**: Break complex sentences into simpler ones

**Good Example:**
```markdown
The screening API returns results in under 500ms for 99% of queries.
```

**Bad Example:**
```markdown
The screening API, which is one of our most important components, typically tends to return results in a relatively fast manner for the vast majority of queries that are submitted by users.
```

### 2. Active Voice

Use active voice to make documentation more direct and engaging.

**Good:** "The system validates user input"
**Bad:** "User input is validated by the system"

**Exception:** Use passive voice when the actor is unknown or unimportant.

### 3. Present Tense

Write in present tense for describing how the system works.

**Good:** "The API returns JSON responses"
**Bad:** "The API will return JSON responses"

### 4. Consistent Terminology

Use the same terms throughout documentation. Refer to the [Terminology Glossary](#terminology-glossary) below.

## Document Structure

### Headers

- Use sentence case for headers: "Getting started" not "Getting Started"
- Use descriptive headers that reflect content
- Maintain a logical hierarchy (H1 → H2 → H3)
- Don't skip header levels

### Paragraphs

- Keep paragraphs short (3-5 sentences)
- Start with the main point
- Use blank lines between paragraphs

### Lists

**Bulleted Lists:**
- Use for unordered items
- Start each item with a capital letter
- End with a period if items are complete sentences
- Keep items parallel in structure

**Numbered Lists:**
1. Use for sequential steps or ordered items
2. Start each item with a capital letter
3. Use imperative mood for instructions ("Click the button")

### Tables

- Use tables for structured data comparison
- Keep column headers concise
- Align numbers to the right
- Align text to the left
- Add a caption or description above complex tables

## Code Examples

### Inline Code

Use backticks for:
- Variable names: `user_id`
- Function names: `get_stock_data()`
- File names: `config.yaml`
- Short code snippets: `SELECT * FROM stocks`
- Commands: `npm install`

### Code Blocks

Use fenced code blocks with language identifiers:

````markdown
```python
def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index."""
    return rsi_value
```
````

**Guidelines:**
- Always specify the language for syntax highlighting
- Include comments to explain complex logic
- Show complete, runnable examples when possible
- Test all code examples before documenting
- Use realistic variable names

### Code Block Languages

Common language identifiers:
- `python` - Python code
- `typescript` - TypeScript/JavaScript code
- `bash` - Shell commands
- `sql` - SQL queries
- `yaml` - YAML configuration
- `json` - JSON data
- `dockerfile` - Dockerfile content
- `nginx` - NGINX configuration

## Links

### Internal Links

Use relative paths for links within documentation:

```markdown
See [API Reference](../03-api-reference/rest-api.md) for details.
```

### External Links

- Open external links in new tabs (handled automatically by Docusaurus)
- Provide link text that describes the destination
- Avoid "click here" or "this link"

**Good:**
```markdown
Read the [PostgreSQL documentation](https://postgresql.org/docs) for more details.
```

**Bad:**
```markdown
Click [here](https://postgresql.org/docs) for more information.
```

## Admonitions

Use Docusaurus admonitions to highlight important information:

```markdown
:::tip
Use WebSocket API for real-time updates to reduce latency.
:::

:::warning
Never expose API credentials in client-side code.
:::

:::danger
This operation cannot be undone. Back up your data first.
:::

:::info
The free tier has a limit of 50 requests per hour.
:::

:::note
This feature is currently in beta.
:::
```

**When to use:**
- **tip**: Helpful suggestions, best practices
- **warning**: Important cautions, potential issues
- **danger**: Critical warnings, destructive actions
- **info**: Additional context, related information
- **note**: Side notes, less critical information

## Tone and Voice

### Professional but Friendly

- Write as if explaining to a colleague
- Use "we" when referring to the project team
- Use "you" when addressing the reader
- Avoid jargon unless necessary (and define it)
- Don't use exclamation marks excessively

### Inclusive Language

- Use gender-neutral language ("they" instead of "he/she")
- Avoid idioms that may not translate well
- Use "people" instead of "guys" or "folks"
- Be mindful of cultural differences

## Formatting Conventions

### Text Formatting

- **Bold**: For emphasis and UI element names ("Click the **Submit** button")
- *Italic*: For introducing new terms ("A *webhook* is an HTTP callback")
- `Code`: For technical terms, commands, code elements

### Numbers

- Spell out numbers one through nine
- Use numerals for 10 and above
- Use numerals for measurements and percentages: "3GB", "25%"
- Use commas for thousands: "1,000 stocks"

### Dates and Times

- Use ISO 8601 format for dates: `2025-11-13`
- Use 24-hour time format: `14:30 UTC`
- Always specify timezone for times

## Screenshots and Images

### When to Include

- Complex UI workflows
- Configuration examples
- Architecture diagrams
- Before/after comparisons

### Guidelines

- Use PNG format for screenshots
- Use SVG for diagrams when possible
- Keep file sizes under 500KB
- Use descriptive file names: `dashboard-filtering-stocks.png`
- Add alt text for accessibility
- Highlight important areas with arrows or boxes
- Use consistent colors for highlights (red for errors, green for success)

### Image Markdown

```markdown
![Dashboard showing stock filtering interface](./images/dashboard-filtering.png)
```

## Terminology Glossary

Use these standard terms consistently throughout documentation:

| Term | Use | Don't Use |
|------|-----|-----------|
| **Stock Screening** | Filtering stocks by criteria | Stock filtering, stock search |
| **Indicator** | Technical or financial metric | Metric, measure, parameter |
| **Portfolio** | User's collection of stocks | Watchlist (unless specifically referring to watch functionality) |
| **KOSPI** | Korea main stock market | Korean stock market |
| **KOSDAQ** | Korea tech stock market | Korean tech market |
| **Real-time** | Live data updates | Realtime, real time |
| **Back-end** | Server-side system | Backend, back end |
| **Front-end** | Client-side application | Frontend, front end |
| **API** | Application Programming Interface | Api, interface |
| **JWT** | JSON Web Token | Json Web Token |
| **WebSocket** | Protocol for real-time communication | Websocket, Web Socket |
| **DataFrame** | Pandas data structure | Data frame, dataframe |
| **Time series** | Sequential data points | Timeseries, time-series |

## API Documentation Standards

### Endpoint Documentation

Each API endpoint should include:

1. **HTTP Method and Path**: `GET /api/v1/stocks/{stock_id}`
2. **Description**: Brief summary of what the endpoint does
3. **Authentication**: Required authentication method
4. **Path Parameters**: Parameters in the URL
5. **Query Parameters**: Optional URL query parameters
6. **Request Body**: JSON schema for POST/PUT requests
7. **Response**: Example successful response
8. **Error Responses**: Common error codes and meanings
9. **Rate Limiting**: Applicable rate limits
10. **Example**: Complete curl or code example

### Parameter Documentation

```markdown
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stock_id` | string | Yes | Stock ticker symbol (e.g., "005930") |
| `period` | integer | No | Number of days (default: 30, max: 365) |
| `include_indicators` | boolean | No | Include technical indicators (default: false) |
```

## Code Comment Guidelines

### Python Docstrings (Google Style)

```python
def calculate_moving_average(prices: List[float], period: int = 20) -> List[float]:
    """Calculate simple moving average for a price series.

    Args:
        prices: List of historical prices in chronological order
        period: Number of periods for the moving average (default: 20)

    Returns:
        List of moving average values with same length as input.
        First (period-1) values will be None.

    Raises:
        ValueError: If period is less than 1 or greater than len(prices)

    Example:
        >>> prices = [100, 102, 101, 103, 105]
        >>> calculate_moving_average(prices, period=3)
        [None, None, 101.0, 102.0, 103.0]
    """
    # Implementation here
```

### TypeScript TSDoc

```typescript
/**
 * Fetches real-time stock price data from the API.
 *
 * @param stockId - The stock ticker symbol (e.g., "005930")
 * @param subscribe - Whether to subscribe to real-time updates
 * @returns Promise resolving to StockPrice object
 * @throws {APIError} When the stock is not found or API is unavailable
 *
 * @example
 * ```ts
 * const price = await fetchStockPrice("005930", true);
 * console.log(price.current); // 70000
 * ```
 */
async function fetchStockPrice(
  stockId: string,
  subscribe: boolean = false
): Promise<StockPrice> {
  // Implementation here
}
```

### SQL Comments

```sql
-- Calculate average trading volume for each stock over the last 30 days
-- Used by: screening API, portfolio analytics
-- Performance: ~50ms for 2,400 stocks
SELECT
    stock_id,
    AVG(volume) as avg_volume,
    STDDEV(volume) as volume_volatility
FROM daily_prices
WHERE
    date >= CURRENT_DATE - INTERVAL '30 days'
    AND volume > 0  -- Exclude days with no trading
GROUP BY stock_id
HAVING COUNT(*) >= 20;  -- Require minimum 20 trading days
```

### YAML Comments

```yaml
# Database connection configuration
# Environment-specific: Override in .env file
database:
  # PostgreSQL connection string
  # Format: postgresql+asyncpg://user:pass@host:port/dbname
  url: ${DATABASE_URL}

  # Connection pool size (per worker process)
  # Production: 20-50, Development: 5-10
  pool_size: 20

  # Maximum overflow connections beyond pool_size
  max_overflow: 10
```

## Version Control

### Commit Messages

Follow conventional commits format for documentation changes:

```
docs: add WebSocket API connection examples

- Add client connection examples in Python and TypeScript
- Update authentication section with JWT token usage
- Fix broken links to rate limiting documentation

Fixes #123
```

**Commit types:**
- `docs:` - Documentation changes
- `fix:` - Documentation fixes (broken links, typos)
- `feat:` - New documentation features
- `style:` - Formatting changes

## Review Checklist

Before submitting documentation:

- [ ] Spell check completed
- [ ] Grammar check completed
- [ ] Links tested (internal and external)
- [ ] Code examples tested
- [ ] Screenshots up to date
- [ ] Terminology consistent with glossary
- [ ] Headers follow hierarchy
- [ ] Admonitions used appropriately
- [ ] Alt text added for images
- [ ] Build passes without warnings

## References

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/)
- [Write the Docs Best Practices](https://www.writethedocs.org/guide/writing/style-guides/)
- [Docusaurus Documentation](https://docusaurus.io/docs)

---

**Last Updated:** 2025-11-13
**Maintainer:** Documentation Team
