# BUGFIX-017: Add Missing Accessibility Attributes to Dialog Components

## Metadata
- **Status**: TODO
- **Priority**: Low
- **Assignee**: TBD
- **Estimated Time**: 1-2 hours
- **Sprint**: Phase 5 (Accessibility)
- **Tags**: frontend, accessibility, a11y, radix-ui

## Description

Dialog components using Radix UI are missing required accessibility attributes, specifically `aria-describedby`. This causes console warnings and may impact screen reader users.

**Warning Message:**
```
Warning: Missing `Description` or `aria-describedby={undefined}` for {DialogContent}.
```

**Affected Components:**
- `FilterPresetManager` - Save dialog
- Potentially other dialogs throughout the application

## Subtasks

- [ ] Audit all Dialog usages in the codebase
- [ ] Add `DialogDescription` component to each dialog
- [ ] For dialogs without visible description, use `VisuallyHidden`
- [ ] Alternatively, explicitly set `aria-describedby={undefined}`
- [ ] Update related unit tests
- [ ] Verify fix with accessibility testing tools
- [ ] Document dialog accessibility patterns

## Acceptance Criteria

1. No accessibility warnings in console for any dialog
2. All dialogs have proper aria attributes
3. Screen readers can properly announce dialog content
4. Unit tests pass without accessibility warnings
5. Accessibility audit passes (axe-core or similar)

## Technical Details

### Solution Options

**Option 1: Add DialogDescription (Recommended)**
```tsx
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@radix-ui/react-dialog';

<Dialog>
  <DialogContent>
    <DialogTitle>Save Filter Preset</DialogTitle>
    <DialogDescription>
      Enter a name for your filter preset to save it for future use.
    </DialogDescription>
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

**Option 2: Use VisuallyHidden for Implicit Description**
```tsx
import { VisuallyHidden } from '@radix-ui/react-visually-hidden';

<Dialog>
  <DialogContent>
    <DialogTitle>Save Filter Preset</DialogTitle>
    <VisuallyHidden asChild>
      <DialogDescription>
        Dialog to save current filter configuration
      </DialogDescription>
    </VisuallyHidden>
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

**Option 3: Explicit aria-describedby={undefined}**
```tsx
// Use only when dialog truly has no description
<DialogContent aria-describedby={undefined}>
  <DialogTitle>Confirmation</DialogTitle>
  {/* Minimal dialog with no description needed */}
</DialogContent>
```

### Files to Update

1. `frontend/src/components/screener/FilterPresetManager.tsx`
2. `frontend/src/components/common/ConfirmDialog.tsx` (if exists)
3. `frontend/src/components/subscription/CheckoutDialog.tsx` (if exists)
4. Any other files using `DialogContent`

### Audit Command

```bash
# Find all Dialog usages
grep -r "DialogContent" frontend/src --include="*.tsx"
```

## Dependencies
- None

## Blocks
- None

## Progress
- [ ] 0% - Not started

## Notes
- Radix UI requires either Description or explicit aria-describedby
- This improves accessibility for screen reader users
- Consider creating a reusable Dialog wrapper component
- Follow WCAG 2.1 AA guidelines

## Accessibility Testing

```typescript
// Add accessibility test
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

describe('FilterPresetManager Dialog', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<FilterPresetManager open={true} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

## References
- [Radix UI Dialog Accessibility](https://www.radix-ui.com/primitives/docs/components/dialog#accessibility)
- [WCAG 2.1 Dialog Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
