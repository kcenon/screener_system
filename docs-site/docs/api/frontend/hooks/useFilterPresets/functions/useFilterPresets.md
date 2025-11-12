[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useFilterPresets](../README.md) / useFilterPresets

# Function: useFilterPresets()

> **useFilterPresets**(): `object`

Defined in: [src/hooks/useFilterPresets.ts:32](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/hooks/useFilterPresets.ts#L32)

Custom hook for managing filter presets with localStorage

Features:
- Save current filters as a preset
- Load saved presets
- Delete presets
- Update preset name/description
- Automatic localStorage synchronization

## Returns

Object with presets array and management functions

### presets

> **presets**: [`FilterPreset`](../interfaces/FilterPreset.md)[]

### savePreset()

> **savePreset**: (`name`, `filters`, `description?`) => [`FilterPreset`](../interfaces/FilterPreset.md)

Save current filters as a new preset

#### Parameters

##### name

`string`

##### filters

[`ScreeningFilters`](../../../types/screening/interfaces/ScreeningFilters.md)

##### description?

`string`

#### Returns

[`FilterPreset`](../interfaces/FilterPreset.md)

### updatePreset()

> **updatePreset**: (`id`, `updates`) => `void`

Update an existing preset

#### Parameters

##### id

`string`

##### updates

###### name?

`string`

###### description?

`string`

###### filters?

[`ScreeningFilters`](../../../types/screening/interfaces/ScreeningFilters.md)

#### Returns

`void`

### deletePreset()

> **deletePreset**: (`id`) => `void`

Delete a preset by ID

#### Parameters

##### id

`string`

#### Returns

`void`

### getPreset()

> **getPreset**: (`id`) => [`FilterPreset`](../interfaces/FilterPreset.md) \| `undefined`

Get a preset by ID

#### Parameters

##### id

`string`

#### Returns

[`FilterPreset`](../interfaces/FilterPreset.md) \| `undefined`

### clearPresets()

> **clearPresets**: () => `void`

Clear all presets

#### Returns

`void`
