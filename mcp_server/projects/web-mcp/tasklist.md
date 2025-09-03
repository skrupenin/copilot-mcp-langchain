# Web MCP Interface - Task List

This document decomposes the Web MCP Interface project into testable implementation phases.

Please check `architecture.md` for detailed architecture information.

## Phase 1: Project Structure Setup ✅ **COMPLETED**
**Goal**: Create basic project structure and configuration files
**Testable outcome**: Project files exist and webhook server can start (even with minimal functionality)

### Tasks:
1. ✅ Create project directory structure (`config/`, `static/`)
2. ✅ Create `config/webhook_config.json` with basic webhook server configuration including html_routes
3. ✅ Create `static/index.html` with minimal HTML structure and template placeholders (TITLE, VERSION, BASE_URL)
4. ✅ Create `readme.md` with setup instructions
5. ✅ Create `run.ps1` PowerShell script for starting the server with virtual environment activation
6. ✅ Test: Run `run.ps1` and verify webhook server starts without errors

## Phase 2: Tool Discovery Integration ✅ **COMPLETED**
**Goal**: Implement backend API for tool discovery
**Testable outcome**: `/api/tools` endpoint returns list of available MCP tools with schemas

### Tasks:
1. ✅ Update `webhook_config.json` with conditional pipeline for `/api/tools` endpoint
2. ✅ Configure pipeline to call `lng_get_tools_info` for 5 selected tools using proper expressions
3. ✅ Implement proper JSON response formatting for tool schemas with JSON template
4. ✅ Add error handling for tool discovery failures in JavaScript frontend
5. ✅ Return only selected tools (5 tools to avoid token overload)
6. ✅ Test: Call `/api/tools` endpoint and verify JSON response with tool schemas
7. ✅ **BONUS**: Frontend displays tools with interactive parameter details
8. ✅ **BONUS**: English-only interface with clean categorization

## Phase 3: Universal Tool Execution ⏳ **NEXT PHASE**
**Goal**: Implement backend API for tool execution
**Testable outcome**: `/api/execute` endpoint can execute any MCP tool

### Tasks:
1. ✅ Update `webhook_config.json` with conditional pipeline for `/api/execute` endpoint (POST method)
2. ✅ Configure pipeline with dynamic tool routing using `{! webhook.body.tool !}` expression
3. ✅ Implement parameter passing using `{! webhook.body.params || {} !}` with fallback
4. ✅ Add error handling and response formatting for execution failures
5. ✅ Test: Execute various tools via POST requests to `/api/execute` with different parameter combinations

## Phase 4: Static HTML Structure ✅ **COMPLETED**
**Goal**: Create complete HTML structure with embedded CSS
**Testable outcome**: Web interface loads and displays static UI elements

### Tasks:
1. ✅ Design responsive HTML layout with header, main content, and footer using CSS Grid and Flexbox
2. ✅ Create CSS styles for tool list, forms, and results display with component-based approach
3. ✅ Implement mobile-first responsive design for desktop and mobile
4. ✅ Add CSS custom properties for theming support
5. ✅ Create basic UI components (buttons, inputs, containers) with reusable CSS classes
6. ✅ Test: Open web interface in browser and verify responsive layout across different screen sizes

## Phase 5: Dynamic Tool Loading ✅ **COMPLETED**
**Goal**: Implement JavaScript to fetch and display tools
**Testable outcome**: Tool list displays all available MCP tools with descriptions

### Tasks:
1. ✅ Implement JavaScript function to fetch tools from `/api/tools` using Fetch API
2. ✅ Create tool card components dynamically with proper DOM manipulation
3. ✅ Display tool descriptions, schemas, and group them by directory structure
4. ✅ Implement tool grouping by directory structure (lng_file, lng_http_client, etc.)
5. ✅ Add hashtag-style group filters with auto-generated categories
6. ✅ Test: Verify tool list loads and displays correctly with filtering and grouping

## Phase 6: Search and Filtering ✅ **COMPLETED**
**Goal**: Implement search and filtering functionality
**Testable outcome**: Users can search and filter tools by various criteria

### Tasks:
1. ✅ Implement real-time search across tool names, descriptions, schemas
2. ✅ Create hashtag filter buttons for tool groups
3. ✅ Add clear filters functionality
4. ✅ Implement case-insensitive search with highlighting
5. ✅ Test: Search for specific tools and verify filtering works correctly

## Phase 7: Dynamic Form Generation ⏳ **NEXT PHASE**
**Goal**: Generate forms based on tool schemas
**Testable outcome**: Each tool displays appropriate input form

### Tasks:
1. Implement JSON Schema to HTML form converter for all parameter types
2. Handle all parameter types (string, number, array, object, enum, oneOf, conditional fields)
3. Create form validation with **force-disable option** to bypass validation when needed
4. Add support for conditional fields and complex schemas based on MCP specifications
5. Implement real-time validation feedback as user types
6. Test: Verify forms generate correctly for various tool schemas including complex parameter types

## Phase 8: Tool Execution Integration
**Goal**: Connect frontend forms to backend execution
**Testable outcome**: Tools can be executed from web interface

### Tasks:
1. Implement form submission to `/api/execute` endpoint
2. Add loading states and progress indicators
3. Handle execution errors gracefully
4. Implement request/response logging for debugging
5. Test: Execute tools through web forms and verify results

## Phase 9: Results Display and Formatting
**Goal**: Display tool results with smart formatting
**Testable outcome**: Results display properly formatted based on content type

### Tasks:
1. Implement JSON syntax highlighting for formatted output
2. Add smart detection for JSON vs plain text with auto-formatting
3. Create **smart formatting**:
   - Tables for arrays of objects
   - Lists for arrays of strings  
   - Expandable JSON trees for complex objects
4. Implement expandable/collapsible JSON trees for better readability
5. Add **single-click copy to clipboard** functionality (primary action)
6. Add download results as file functionality (secondary action)
7. Test: Execute tools with different result types and verify proper formatting and actions work

## Phase 10: Polish and Testing
**Goal**: Final polish and comprehensive testing
**Testable outcome**: Complete web interface works reliably across browsers

### Tasks:
1. Add comprehensive error handling for network failures and API unavailability
2. Implement loading states and user feedback with progress indicators
3. Add keyboard shortcuts and accessibility features for better UX
4. Cross-browser testing (Chrome, Firefox, Edge) with ES6+ compatibility
5. Performance optimization, efficient DOM manipulation, and code cleanup
6. Update documentation with usage examples and deployment options
7. Test: Full end-to-end testing of all functionality across browsers and devices

## Testing Strategy

Each phase includes specific testing requirements:
- **Unit Testing**: Test individual JavaScript functions
- **Integration Testing**: Test API endpoints with various inputs
- **Manual Testing**: Verify UI functionality in browser
- **Error Testing**: Test error handling and edge cases

## Dependencies

- `lng_webhook_server` tool for web server functionality
- `lng_get_tools_info` tool for tool discovery
- `lng_batch_run` tool for pipeline execution
- Modern web browser with ES6+ support
- Python MCP server with virtual environment activated

## Success Criteria

The project is considered complete when:
1. Web interface loads without errors
2. All MCP tools are discoverable and executable
3. Forms generate correctly for all tool schemas
4. Results display with appropriate formatting
5. Search and filtering work reliably
6. Interface is responsive on desktop and mobile
7. Error handling provides clear user feedback
