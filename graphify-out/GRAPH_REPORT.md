# Graph Report - fullstack  (2026-10-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 972 nodes · 1886 edges · 80 communities (56 shown, 24 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3f5be653`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- page.tsx
- pnpm-install.mjs
- connector-preview-session.mjs
- cn
- main.py
- AppStore
- sidebar.tsx
- SupplierStore
- combobox.tsx
- dependencies
- test_components.py
- package.json
- devDependencies
- field.tsx
- compilerOptions
- DataTools
- components.json
- menubar.tsx
- chatgpt-auth.ts
- context-menu.tsx
- dropdown-menu.tsx
- form.tsx
- carousel.tsx
- chart.tsx
- sites-env.sh
- radix-ui
- Button
- utils.ts
- alert-dialog.tsx
- attachment.tsx
- react
- drawer.tsx
- item.tsx
- sheet.tsx
- connector-contract.mts
- settings.py
- class-variance-authority
- select.tsx
- notes/route.ts
- navigation-menu.tsx
- pagination.tsx
- connector-context.ts
- empty.tsx
- message-scroller.tsx
- popover.tsx
- install-pnpm.sh
- bubble.tsx
- scripts
- input-otp.tsx
- tabs.tsx
- alert.tsx
- marker.tsx
- resizable.tsx
- install-ci.sh
- sonner.tsx
- eslint.config.mjs
- cloudflare-env.d.ts
- scroll-area.tsx
- overrides
- drizzle-kit
- engines
- postcss.config.mjs
- build-verified.sh
- ./connector-contract.mjs
- supplier-risk-backend

## God Nodes (most connected - your core abstractions)
1. `cn()` - 327 edges
2. `react` - 56 edges
3. `radix-ui` - 38 edges
4. `Button()` - 28 edges
5. `lucide-react` - 27 edges
6. `AppStore` - 26 edges
7. `DataTools` - 20 edges
8. `Home()` - 20 edges
9. `SupplierStore` - 17 edges
10. `compilerOptions` - 17 edges

## Surprising Connections (you probably didn't know these)
- `CommandGroup()` --calls--> `cn()`  [EXTRACTED]
  components/ui/command.tsx → lib/utils.ts
- `CommandInput()` --calls--> `cn()`  [EXTRACTED]
  components/ui/command.tsx → lib/utils.ts
- `CommandItem()` --calls--> `cn()`  [EXTRACTED]
  components/ui/command.tsx → lib/utils.ts
- `CommandList()` --calls--> `cn()`  [EXTRACTED]
  components/ui/command.tsx → lib/utils.ts
- `CommandSeparator()` --calls--> `cn()`  [EXTRACTED]
  components/ui/command.tsx → lib/utils.ts

## Import Cycles
- None detected.

## Communities (80 total, 24 thin omitted)

### Community 0 - "page.tsx"
Cohesion: 0.07
Nodes (35): dimensions, Home(), initials(), level(), Metric(), MiniBar(), money(), navigation (+27 more)

### Community 1 - "pnpm-install.mjs"
Cohesion: 0.07
Nodes (19): vinext, vite, readExecutionProfile(), NpmCacheProgress, runNpmInstall(), CACHE_SEEDS, holdInstallLocks(), InstallProgress (+11 more)

### Community 2 - "connector-preview-session.mjs"
Cohesion: 0.06
Nodes (33): json-rpc-2.0, raw-body, zod, active, binding, close(), descriptor, directory (+25 more)

### Community 3 - "cn"
Cohesion: 0.09
Nodes (36): Avatar(), AvatarBadge(), AvatarFallback(), AvatarGroup(), AvatarGroupCount(), AvatarImage(), BreadcrumbEllipsis(), BreadcrumbItem() (+28 more)

### Community 4 - "main.py"
Cohesion: 0.10
Nodes (30): chat(), compare(), component_analysis(), components(), events_stream(), event_generator(), explain(), get_research() (+22 more)

### Community 5 - "AppStore"
Cohesion: 0.10
Nodes (8): NewsAgent, ResearchAgent, AppStore, lifespan(), AgentBus, AgentEnvelope, EventBus, SearchGateway

### Community 6 - "sidebar.tsx"
Cohesion: 0.08
Nodes (33): InputGroupInput(), Input(), SidebarContent(), SidebarContext, SidebarContextProps, SidebarFooter(), SidebarGroup(), SidebarGroupAction() (+25 more)

### Community 7 - "SupplierStore"
Cohesion: 0.12
Nodes (3): LiveOrdersAgent, SupplierStore, ScoreExplainer

### Community 8 - "combobox.tsx"
Cohesion: 0.11
Nodes (22): ComboboxChip(), ComboboxChips(), ComboboxChipsInput(), ComboboxClear(), ComboboxContent(), ComboboxEmpty(), ComboboxGroup(), ComboboxInput() (+14 more)

### Community 9 - "dependencies"
Cohesion: 0.08
Nodes (25): dependencies, @base-ui/react, class-variance-authority, clsx, cmdk, date-fns, drizzle-orm, embla-carousel-react (+17 more)

### Community 10 - "test_components.py"
Cohesion: 0.15
Nodes (7): ChatAgent, catalog(), ComponentRisk, resolve_components(), test_analysis_rejects_ambiguous_or_missing_inputs(), test_component_research_queries(), test_missing_values_and_ties()

### Community 11 - "package.json"
Cohesion: 0.09
Nodes (21): name, private, type, version, @cloudflare/vite-plugin, @cloudflare/workers-types, cmdk, date-fns (+13 more)

### Community 12 - "devDependencies"
Cohesion: 0.10
Nodes (21): devDependencies, @cloudflare/vite-plugin, @cloudflare/workers-types, drizzle-kit, eslint, eslint-config-next, json-rpc-2.0, raw-body (+13 more)

### Community 13 - "field.tsx"
Cohesion: 0.13
Nodes (17): ButtonGroup(), ButtonGroupSeparator(), ButtonGroupText(), buttonGroupVariants, Field(), FieldContent(), FieldDescription(), FieldError() (+9 more)

### Community 14 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 15 - "DataTools"
Cohesion: 0.14
Nodes (3): MemoAgent, ScenarioAgent, DataTools

### Community 16 - "components.json"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, registries, rsc (+9 more)

### Community 17 - "menubar.tsx"
Cohesion: 0.12
Nodes (12): Menubar(), MenubarCheckboxItem(), MenubarContent(), MenubarItem(), MenubarLabel(), MenubarPortal(), MenubarRadioItem(), MenubarSeparator() (+4 more)

### Community 18 - "chatgpt-auth.ts"
Cohesion: 0.17
Nodes (11): chatGPTSignInPath(), chatGPTSignOutPath(), ChatGPTUser, getChatGPTUser(), isReservedAuthPath(), requireChatGPTUser(), safeDecodeURIComponent(), safeRelativeReturnPath() (+3 more)

### Community 19 - "context-menu.tsx"
Cohesion: 0.12
Nodes (9): ContextMenuCheckboxItem(), ContextMenuContent(), ContextMenuItem(), ContextMenuLabel(), ContextMenuRadioItem(), ContextMenuSeparator(), ContextMenuShortcut(), ContextMenuSubContent() (+1 more)

### Community 20 - "dropdown-menu.tsx"
Cohesion: 0.12
Nodes (9): DropdownMenuCheckboxItem(), DropdownMenuContent(), DropdownMenuItem(), DropdownMenuLabel(), DropdownMenuRadioItem(), DropdownMenuSeparator(), DropdownMenuShortcut(), DropdownMenuSubContent() (+1 more)

### Community 21 - "form.tsx"
Cohesion: 0.17
Nodes (13): FieldLabel(), FormControl(), FormDescription(), FormFieldContext, FormFieldContextValue, FormItem(), FormItemContext, FormItemContextValue (+5 more)

### Community 22 - "carousel.tsx"
Cohesion: 0.17
Nodes (14): Carousel(), CarouselApi, CarouselContent(), CarouselContext, CarouselContextProps, CarouselItem(), CarouselNext(), CarouselOptions (+6 more)

### Community 23 - "chart.tsx"
Cohesion: 0.20
Nodes (13): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartStyle(), ChartTooltipContent(), getPayloadConfigFromPayload() (+5 more)

### Community 24 - "sites-env.sh"
Cohesion: 0.14
Nodes (13): HOME, MINIFLARE_REGISTRY_PATH, npm_config_audit, npm_config_cache, npm_config_fund, npm_config_update_notifier, sites-env.sh script, SITES_ENV_READY (+5 more)

### Community 25 - "radix-ui"
Cohesion: 0.15
Nodes (4): Checkbox(), Slider(), Switch(), radix-ui

### Community 26 - "Button"
Cohesion: 0.29
Nodes (8): ConnectorError(), AlertDialogAction(), Button(), buttonVariants, Calendar(), CalendarDayButton(), DialogFooter(), react-day-picker

### Community 27 - "utils.ts"
Cohesion: 0.17
Nodes (6): AccordionContent(), AccordionItem(), AccordionTrigger(), HoverCardContent(), clsx, tailwind-merge

### Community 28 - "alert-dialog.tsx"
Cohesion: 0.20
Nodes (9): AlertDialogCancel(), AlertDialogContent(), AlertDialogDescription(), AlertDialogFooter(), AlertDialogHeader(), AlertDialogMedia(), AlertDialogOverlay(), AlertDialogPortal() (+1 more)

### Community 29 - "attachment.tsx"
Cohesion: 0.20
Nodes (11): Attachment(), AttachmentAction(), AttachmentActions(), AttachmentContent(), AttachmentDescription(), AttachmentGroup(), AttachmentMedia(), attachmentMediaVariants (+3 more)

### Community 30 - "react"
Cohesion: 0.17
Nodes (7): NativeSelect(), NativeSelectOptGroup(), NativeSelectOption(), Progress(), RadioGroup(), RadioGroupItem(), react

### Community 31 - "drawer.tsx"
Cohesion: 0.20
Nodes (8): DrawerContent(), DrawerDescription(), DrawerFooter(), DrawerHeader(), DrawerOverlay(), DrawerPortal(), DrawerTitle(), vaul

### Community 32 - "item.tsx"
Cohesion: 0.20
Nodes (11): Item(), ItemActions(), ItemContent(), ItemDescription(), ItemFooter(), ItemGroup(), ItemHeader(), ItemMedia() (+3 more)

### Community 33 - "sheet.tsx"
Cohesion: 0.26
Nodes (9): Sheet(), SheetContent(), SheetDescription(), SheetFooter(), SheetHeader(), SheetOverlay(), SheetPortal(), SheetTitle() (+1 more)

### Community 34 - "connector-contract.mts"
Cohesion: 0.17
Nodes (9): ConnectorBinding, ConnectorContent, ConnectorContext, ConnectorFailureStatus, ConnectorResult, Json, Cloudflare, Env (+1 more)

### Community 35 - "settings.py"
Cohesion: 0.20
Nodes (3): _dataset_path(), Settings, require_agent_key()

### Community 36 - "class-variance-authority"
Cohesion: 0.27
Nodes (8): Badge(), badgeVariants, ToggleGroup(), ToggleGroupContext, ToggleGroupItem(), Toggle(), toggleVariants, class-variance-authority

### Community 37 - "select.tsx"
Cohesion: 0.22
Nodes (7): SelectContent(), SelectItem(), SelectLabel(), SelectScrollDownButton(), SelectScrollUpButton(), SelectSeparator(), SelectTrigger()

### Community 38 - "notes/route.ts"
Cohesion: 0.33
Nodes (6): getDb(), GET(), POST(), toRouteErrorMessage(), notes, drizzle-orm

### Community 39 - "navigation-menu.tsx"
Cohesion: 0.24
Nodes (9): NavigationMenu(), NavigationMenuContent(), NavigationMenuIndicator(), NavigationMenuItem(), NavigationMenuLink(), NavigationMenuList(), NavigationMenuTrigger(), navigationMenuTriggerStyle (+1 more)

### Community 40 - "pagination.tsx"
Cohesion: 0.28
Nodes (7): Pagination(), PaginationContent(), PaginationEllipsis(), PaginationLink(), PaginationLinkProps, PaginationNext(), PaginationPrevious()

### Community 41 - "connector-context.ts"
Cohesion: 0.31
Nodes (3): bindings, getConnectorBinding(), connectorsForRequest()

### Community 43 - "empty.tsx"
Cohesion: 0.29
Nodes (7): Empty(), EmptyContent(), EmptyDescription(), EmptyHeader(), EmptyMedia(), emptyMediaVariants, EmptyTitle()

### Community 44 - "message-scroller.tsx"
Cohesion: 0.25
Nodes (6): MessageScroller(), MessageScrollerButton(), MessageScrollerContent(), MessageScrollerItem(), MessageScrollerViewport(), @shadcn/react

### Community 45 - "popover.tsx"
Cohesion: 0.25
Nodes (4): PopoverContent(), PopoverDescription(), PopoverHeader(), PopoverTitle()

### Community 46 - "install-pnpm.sh"
Cohesion: 0.39
Nodes (7): acquire_shared_lock(), can_write_directory(), release_shared_lock(), report_store(), install-pnpm.sh script, XDG_CACHE_HOME, XDG_DATA_HOME

### Community 47 - "bubble.tsx"
Cohesion: 0.38
Nodes (6): Bubble(), BubbleContent(), BubbleGroup(), BubbleReactions(), bubbleReactionsVariants, bubbleVariants

### Community 48 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, db:generate, dev, install:ci, lint, start

### Community 49 - "input-otp.tsx"
Cohesion: 0.33
Nodes (4): InputOTP(), InputOTPGroup(), InputOTPSlot(), input-otp

### Community 50 - "tabs.tsx"
Cohesion: 0.40
Nodes (5): Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger()

### Community 52 - "alert.tsx"
Cohesion: 0.50
Nodes (4): Alert(), AlertDescription(), AlertTitle(), alertVariants

### Community 53 - "marker.tsx"
Cohesion: 0.50
Nodes (4): Marker(), MarkerContent(), MarkerIcon(), markerVariants

### Community 54 - "resizable.tsx"
Cohesion: 0.40
Nodes (3): ResizableHandle(), ResizablePanelGroup(), react-resizable-panels

### Community 55 - "install-ci.sh"
Cohesion: 0.40
Nodes (4): NPM_CONFIG_FETCH_RETRIES, NPM_CONFIG_FETCH_TIMEOUT, NPM_CONFIG_MAXSOCKETS, install-ci.sh script

### Community 57 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 60 - "overrides"
Cohesion: 0.67
Nodes (3): sharp, overrides, miniflare

## Knowledge Gaps
- **35 isolated node(s):** `@cloudflare/vite-plugin`, `@cloudflare/workers-types`, `date-fns`, `@hookform/resolvers`, `react-dom` (+30 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 342 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cn()` connect `cn` to `page.tsx`, `sidebar.tsx`, `combobox.tsx`, `field.tsx`, `menubar.tsx`, `context-menu.tsx`, `dropdown-menu.tsx`, `form.tsx`, `carousel.tsx`, `chart.tsx`, `radix-ui`, `Button`, `utils.ts`, `alert-dialog.tsx`, `attachment.tsx`, `react`, `drawer.tsx`, `item.tsx`, `sheet.tsx`, `class-variance-authority`, `select.tsx`, `navigation-menu.tsx`, `pagination.tsx`, `empty.tsx`, `message-scroller.tsx`, `popover.tsx`, `bubble.tsx`, `input-otp.tsx`, `tabs.tsx`, `alert.tsx`, `marker.tsx`, `resizable.tsx`, `scroll-area.tsx`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **What connects `@cloudflare/vite-plugin`, `@cloudflare/workers-types`, `date-fns` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `page.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07183673469387755 - nodes in this community are weakly interconnected._
- **Why does `react` connect `react` to `page.tsx`, `cn`, `sidebar.tsx`, `combobox.tsx`, `package.json`, `field.tsx`, `menubar.tsx`, `context-menu.tsx`, `dropdown-menu.tsx`, `form.tsx`, `carousel.tsx`, `chart.tsx`, `radix-ui`, `Button`, `utils.ts`, `alert-dialog.tsx`, `attachment.tsx`, `drawer.tsx`, `item.tsx`, `sheet.tsx`, `class-variance-authority`, `select.tsx`, `navigation-menu.tsx`, `pagination.tsx`, `message-scroller.tsx`, `popover.tsx`, `bubble.tsx`, `input-otp.tsx`, `tabs.tsx`, `alert.tsx`, `marker.tsx`, `scroll-area.tsx`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Should `pnpm-install.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.07474747474747474 - nodes in this community are weakly interconnected._
- **Why does `json-rpc-2.0` connect `connector-preview-session.mjs` to `package.json`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Should `connector-preview-session.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.0613107822410148 - nodes in this community are weakly interconnected._