# TSDoc Templates for Frontend Documentation

This guide provides standardized TSDoc templates for documenting frontend code in the Stock Screening Platform.

## Table of Contents

1. [React Component Template](#react-component-template)
2. [Custom Hook Template](#custom-hook-template)
3. [Utility Function Template](#utility-function-template)
4. [Type Definition Template](#type-definition-template)
5. [Service Class Template](#service-class-template)

## React Component Template

### Functional Component with Props

```typescript
/**
 * Brief one-line description of what this component does.
 *
 * More detailed description explaining the component's purpose,
 * behavior, and any important implementation details. Include
 * information about state management, side effects, or interactions
 * with other components.
 *
 * @component
 * @example
 * ```tsx
 * <ComponentName
 *   requiredProp="value"
 *   optionalProp={42}
 *   onEvent={(data) => console.log(data)}
 * />
 * ```
 *
 * @param props - Component props
 * @param props.requiredProp - Description of required prop
 * @param props.optionalProp - Description of optional prop with default value
 * @param props.onEvent - Callback fired when event occurs
 *
 * @returns React component rendering the component description
 *
 * @see {@link RelatedComponent} for related functionality
 * @see {@link useRelatedHook} for data fetching logic
 *
 * @category Components
 * @subcategory SubcategoryName (e.g., Screening, Stock Detail)
 */
export const ComponentName: React.FC<ComponentNameProps> = ({
  requiredProp,
  optionalProp = 42,
  onEvent
}) => {
  // Implementation
  return <div>Component content</div>;
};

/**
 * Props for ComponentName component.
 *
 * @interface
 * @category Types
 */
export interface ComponentNameProps {
  /**
   * Description of what this prop does and when it should be used.
   * Include any constraints or valid value ranges.
   */
  requiredProp: string;

  /**
   * Description of optional prop with its default behavior.
   *
   * @defaultValue 42
   */
  optionalProp?: number;

  /**
   * Callback invoked when a specific event occurs.
   * Describe when and why this callback is fired.
   *
   * @param data - Description of callback parameter
   */
  onEvent: (data: EventData) => void;
}
```

## Custom Hook Template

### Data Fetching Hook

```typescript
/**
 * React Query hook for fetching specific data type.
 *
 * Detailed description of what data this hook fetches, how it handles
 * caching, background refetching, error states, and any special behaviors.
 * Include information about query invalidation and dependencies.
 *
 * @hook
 * @example
 * ```tsx
 * const { data, isLoading, error, refetch } = useHookName({
 *   param1: 'value',
 *   param2: 42,
 *   options: { enabled: true }
 * });
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <ErrorAlert error={error} />;
 *
 * return <DataDisplay data={data} />;
 * ```
 *
 * @param params - Hook parameters
 * @param params.param1 - Description of first parameter
 * @param params.param2 - Description of second parameter
 * @param params.options - React Query options
 *
 * @returns React Query result object
 * @returns data - The fetched data when successful
 * @returns isLoading - Loading state indicator
 * @returns error - Error object if request failed
 * @returns refetch - Function to manually refetch data
 *
 * @throws {ValidationError} When parameters are invalid
 * @throws {NetworkError} When API request fails
 *
 * @see {@link RelatedService} for API implementation
 * @see {@link DataType} for return data structure
 *
 * @category Hooks
 * @subcategory Data Fetching
 */
export function useHookName({
  param1,
  param2,
  options
}: HookParams): UseQueryResult<DataType> {
  // Implementation
}

/**
 * Parameters for useHookName hook.
 *
 * @interface
 * @category Types
 */
export interface HookParams {
  /**
   * Description of parameter with constraints.
   *
   * @example "KOSPI"
   */
  param1: string;

  /**
   * Description of numeric parameter.
   *
   * @minimum 1
   * @maximum 100
   * @defaultValue 50
   */
  param2?: number;

  /**
   * React Query options for controlling hook behavior.
   *
   * @see {@link https://tanstack.com/query/latest/docs/react/guides/query-options}
   */
  options?: UseQueryOptions<DataType>;
}
```

### State Management Hook

```typescript
/**
 * Custom hook for managing specific state or behavior.
 *
 * Detailed description of what state this hook manages, side effects
 * it triggers, and how it integrates with other parts of the application.
 *
 * @hook
 * @example
 * ```tsx
 * const { state, actions } = useStateName();
 *
 * // Access state
 * console.log(state.value);
 *
 * // Trigger actions
 * actions.updateValue('new value');
 * ```
 *
 * @returns Hook state and actions
 * @returns state - Current state object
 * @returns actions - Functions to update state
 *
 * @category Hooks
 * @subcategory State Management
 */
export function useStateName() {
  // Implementation
}
```

## Utility Function Template

### Pure Function

```typescript
/**
 * Brief description of what this function does.
 *
 * More detailed explanation of the function's purpose, algorithm,
 * edge cases, and any performance considerations.
 *
 * @param input - Description of input parameter with constraints
 * @param options - Optional configuration object
 *
 * @returns Description of return value
 *
 * @throws {TypeError} When input is not the expected type
 * @throws {RangeError} When input is outside valid range
 *
 * @example
 * ```typescript
 * // Basic usage
 * const result = functionName('input', { option: true });
 * // => expected output
 *
 * // Edge case
 * const edge = functionName('', { option: false });
 * // => expected output for edge case
 * ```
 *
 * @see {@link relatedFunction} for related functionality
 *
 * @category Utilities
 * @subcategory SubcategoryName
 */
export function functionName(
  input: string,
  options?: FunctionOptions
): ReturnType {
  // Implementation
}
```

### Formatting Function

```typescript
/**
 * Formats data into human-readable string representation.
 *
 * Converts raw data into formatted string following locale conventions.
 * Handles edge cases like undefined, null, zero, and extreme values.
 *
 * @param value - Raw value to format
 * @param precision - Number of decimal places (default: 2)
 * @param locale - Locale for formatting (default: 'en-US')
 *
 * @returns Formatted string representation
 *
 * @example
 * ```typescript
 * formatValue(1234.56);
 * // => "1,234.56"
 *
 * formatValue(1234.56, 0);
 * // => "1,235"
 *
 * formatValue(1234.56, 2, 'ko-KR');
 * // => "1,234.56"
 * ```
 *
 * @category Utilities
 * @subcategory Formatting
 */
export function formatValue(
  value: number,
  precision: number = 2,
  locale: string = 'en-US'
): string {
  // Implementation
}
```

## Type Definition Template

### Interface

```typescript
/**
 * Represents a specific entity or data structure.
 *
 * Detailed description of what this interface represents, when it's used,
 * and any validation rules or constraints that apply to its fields.
 *
 * @interface
 * @category Types
 * @subcategory SubcategoryName
 */
export interface TypeName {
  /**
   * Unique identifier for the entity.
   *
   * @example "abc123"
   */
  id: string;

  /**
   * Human-readable name.
   * Must be non-empty and contain only valid characters.
   *
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9\s]+$
   */
  name: string;

  /**
   * Optional description field.
   * Provides additional context about the entity.
   *
   * @defaultValue undefined
   */
  description?: string;

  /**
   * Numeric value with specific constraints.
   *
   * @minimum 0
   * @maximum 100
   * @defaultValue 0
   */
  value: number;

  /**
   * Timestamp indicating when entity was created.
   * Stored as ISO 8601 string.
   *
   * @format date-time
   * @example "2024-01-01T00:00:00Z"
   */
  createdAt: string;
}
```

### Type Alias

```typescript
/**
 * Union type representing possible state values.
 *
 * Describes all valid values this type can take and when each is used.
 *
 * @example "active"
 * @example "pending"
 * @example "completed"
 *
 * @category Types
 */
export type StatusType = 'active' | 'pending' | 'completed' | 'failed';
```

### Enum

```typescript
/**
 * Enumeration of possible categories.
 *
 * Defines all valid categories used throughout the application.
 *
 * @enum
 * @category Types
 */
export enum Category {
  /**
   * First category type.
   * Used when condition A is met.
   */
  TYPE_A = 'TYPE_A',

  /**
   * Second category type.
   * Used when condition B is met.
   */
  TYPE_B = 'TYPE_B',

  /**
   * Default category.
   * Fallback when no specific category applies.
   */
  DEFAULT = 'DEFAULT'
}
```

## Service Class Template

```typescript
/**
 * Service class for handling specific domain operations.
 *
 * Detailed description of what this service does, how it interacts
 * with APIs or external systems, error handling strategy, and any
 * important configuration or initialization requirements.
 *
 * @class
 * @example
 * ```typescript
 * const service = new ServiceName({
 *   baseURL: 'https://api.example.com',
 *   timeout: 5000
 * });
 *
 * const data = await service.getData({ id: '123' });
 * ```
 *
 * @category Services
 */
export class ServiceName {
  /**
   * Service configuration options.
   *
   * @private
   */
  private config: ServiceConfig;

  /**
   * Creates a new instance of ServiceName.
   *
   * @param config - Service configuration
   * @param config.baseURL - Base URL for API requests
   * @param config.timeout - Request timeout in milliseconds
   *
   * @throws {ConfigError} When configuration is invalid
   */
  constructor(config: ServiceConfig) {
    // Implementation
  }

  /**
   * Fetches data from the service.
   *
   * Detailed description of what data is fetched, how errors are handled,
   * caching behavior, and any side effects.
   *
   * @param params - Request parameters
   * @param params.id - Entity identifier
   * @param params.options - Additional request options
   *
   * @returns Promise resolving to fetched data
   *
   * @throws {NotFoundError} When entity doesn't exist
   * @throws {NetworkError} When request fails
   * @throws {TimeoutError} When request exceeds timeout
   *
   * @example
   * ```typescript
   * const data = await service.getData({ id: '123' });
   * console.log(data);
   * ```
   */
  async getData(params: GetDataParams): Promise<DataType> {
    // Implementation
  }

  /**
   * Updates data in the service.
   *
   * @param id - Entity identifier
   * @param updates - Partial updates to apply
   *
   * @returns Promise resolving to updated entity
   *
   * @throws {ValidationError} When updates are invalid
   * @throws {NotFoundError} When entity doesn't exist
   */
  async updateData(id: string, updates: Partial<DataType>): Promise<DataType> {
    // Implementation
  }
}
```

## Best Practices

### General Guidelines

1. **Be Concise but Complete**: One-line descriptions should be clear and informative. Expand in the detailed description when necessary.

2. **Use Active Voice**: "Fetches user data" instead of "User data is fetched"

3. **Include Examples**: Real-world usage examples help developers understand how to use the API

4. **Document Constraints**: Specify min/max values, required formats, valid patterns

5. **Link Related Items**: Use `@see` to cross-reference related components, hooks, or types

6. **Categorize Properly**: Use `@category` and `@subcategory` tags for better organization

7. **Explain Why, Not Just What**: Include rationale for design decisions when relevant

### Example Quality Standards

- ✅ **Good**: `formatCurrency(1234.56) // => "$1,234.56"`
- ❌ **Bad**: `formatCurrency(value) // formats value`

### Documentation Coverage Goals

- **Components**: 100% of exported components
- **Hooks**: 100% of custom hooks
- **Utilities**: 100% of exported functions
- **Types**: 90%+ of exported interfaces and types
- **Services**: 100% of public methods

### When to Update Documentation

- When adding new features
- When modifying public APIs
- When fixing bugs that affect behavior
- When deprecating functionality

### TSDoc Tags Reference

| Tag | Purpose | Example |
|-----|---------|---------|
| `@param` | Document function parameters | `@param value - The input value` |
| `@returns` | Document return value | `@returns Formatted string` |
| `@throws` | Document exceptions | `@throws {Error} When invalid` |
| `@example` | Provide usage example | See templates above |
| `@see` | Reference related items | `@see {@link RelatedType}` |
| `@category` | Group by category | `@category Components` |
| `@defaultValue` | Specify default value | `@defaultValue 0` |
| `@deprecated` | Mark as deprecated | `@deprecated Use newFunction instead` |

## Validation

### Linting TSDoc Comments

```bash
# Install ESLint TSDoc plugin
npm install --save-dev eslint-plugin-tsdoc

# Add to .eslintrc.json
{
  "plugins": ["eslint-plugin-tsdoc"],
  "rules": {
    "tsdoc/syntax": "error"
  }
}
```

### Checking Coverage

```bash
# Generate documentation
npm run docs:generate

# Check for undocumented exports
npx ts-node scripts/check-documentation.ts
```

## Resources

- [TSDoc Official Specification](https://tsdoc.org/)
- [TypeDoc Documentation](https://typedoc.org/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)

---

**Last Updated**: 2024-11-12
**Version**: 1.0.0
**Maintainer**: Development Team
