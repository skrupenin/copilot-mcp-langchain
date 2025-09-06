# Super Empath LLM Integration - Task List

## Project Overview
This project enhances the Super Empath Telegram bot to use LLM-based responses instead of hardcoded logic. The system will maintain conversation history for each user and provide contextual, empathetic responses using a structured prompt template.

## Task Breakdown

### Task 1: Create Project Documentation ✅
**Description:** Create tasklist.md and update readme.md in projects/super-empath/ with task decomposition and project overview

**Implementation Details:**
- Document the complete project scope and requirements
- Create this task list with clear acceptance criteria
- Update readme.md with technical specifications

**Testing:** Review documentation completeness and clarity

**Acceptance Criteria:**
- [x] tasklist.md created with all tasks
- [x] readme.md updated with project overview
- [x] Technical requirements documented

---

### Task 2: Create Prompt Template File ✅
**Description:** Create prompt template file in projects/super-empath/prompt/default_super_empath.txt with the specified prompt structure

**Implementation Details:**
- Create directory structure: `projects/super-empath/prompt/`
- Create `default_super_empath.txt` with the empathy prompt from requirements
- Exact prompt text: "Ты супер эмпат, твоя задача помочь собеседникам договориться..."
- Template should include placeholders for: `{conversation_history}`, `{user_message}`, `{user_id}`
- Prompt should request structured JSON output with `explanation` and `suggestion` fields
- Avoid "ё" characters (use "е") and long dashes (use "-") as specified
- Response should not sound "plastic" or artificial

**Testing:** Validate template syntax and placeholder structure

**Acceptance Criteria:**
- [x] Prompt directory created
- [x] Template file contains complete empathy prompt
- [x] JSON structure specified correctly
- [x] Character restrictions applied (no "ё", no long dashes)

---

### Task 3: Update Telegram Pipeline Config ✅
**Description:** Transform telegram_pipeline.json into a batch pipeline that loads prompt and saves it as template, then calls telegram tool

**Implementation Details:**
- Convert current telegram_pipeline.json to batch pipeline format
- Add step to load prompt from file using `lng_file_read`
- Add step to save prompt template using `lng_llm_prompt_template save`
- Keep existing telegram tool call with current parameters
- Configure template name as "default_super_empath"
- Use pipeline_file approach instead of inline pipeline for better expression handling

**Testing:** Validate pipeline syntax and execution order

**Acceptance Criteria:**
- [x] Pipeline loads prompt from file
- [x] Pipeline saves template with correct name
- [x] Pipeline calls telegram tool with pipeline_file reference
- [x] All steps have proper output variables
- [x] Expression evaluation works correctly with telegram context

---

### Task 4: Implement Session History Management ✅
**Description:** Add session/user history management to super-empath tool with file storage in config/telegram/sessions/<sessionId>/<userId>.txt

**Implementation Details:**
- Create session directory structure automatically
- Implement history file format: `[USER_ID|USER_NAME]: message content`
- Support multi-line messages (preserve line breaks)
- Include EMPATH responses in history as `[EMPATH]: response content`
- Handle special commands like `тамам`, `отбой` (not `/tamam`, `/cancel`)
- Each user sees: own messages + messages from others + empath responses
- Load existing history when processing new messages
- Append new messages to history files
- Create separate history file per user per session

**Testing:** Test history creation, loading, and appending with mock data

**Acceptance Criteria:**
- [x] Session directories created automatically
- [x] History files follow specified format
- [x] Multi-line messages handled correctly
- [x] History loading works for existing users
- [x] New messages appended correctly

---

### Task 5: Modify Super-Empath Tool for LLM Integration ✅
**Description:** Replace hardcoded logic with LLM calls using lng_llm_prompt_template through tool_registry.py, implement structured JSON output parsing

**Implementation Details:**
- Import and use tool_registry.py for LLM calls
- Replace hardcoded response logic with `lng_llm_prompt_template use`
- Pass conversation history, user message, and user ID as parameters
- Parse structured JSON response with `explanation` and `suggestion`
- Handle LLM response errors gracefully
- Maintain backward compatibility for error cases

**Testing:** Test LLM integration with various message types and history scenarios

**Acceptance Criteria:**
- [x] Hardcoded logic removed
- [x] LLM calls implemented via tool_registry
- [x] JSON response parsing works correctly
- [x] Error handling implemented
- [x] All parameters passed correctly to LLM

---

### Task 6: Implement Named Bot Management ✅
**Description:** Add named bot instances to avoid conflicts when multiple bots are running

**Implementation Details:**
- Replace global `_server_instance` with `_server_instances` dictionary
- Add `bot_name` parameter to telegram polling server operations
- Implement automatic cleanup of old instances when starting new bot with same name
- Update pipeline configuration to use named bots
- Add proper status reporting for named instances

**Testing:** Test multiple named bot instances and proper cleanup

**Acceptance Criteria:**
- [x] Named bot instances implemented
- [x] Automatic cleanup of conflicting instances
- [x] Pipeline configuration updated with bot_name
- [x] Status reporting works for named bots
- [x] No "Conflict: terminated by other getUpdates request" errors

---

### Task 7: Test and Validate Implementation ✅
**Description:** Test the complete pipeline with mock telegram data and validate JSON response parsing

**Implementation Details:**
- Create test scenarios with mock telegram messages
- Test session creation and history management
- Validate LLM responses and JSON parsing
- Test error handling scenarios
- Verify pipeline execution from start to finish
- Test with multiple users and sessions

**Testing:** Comprehensive testing of all components

**Acceptance Criteria:**
- [x] Pipeline executes successfully end-to-end
- [x] History management works correctly
- [x] LLM responses are properly structured
- [x] Error scenarios handled gracefully
- [x] Multiple user scenarios tested

## Important Requirements from Discussion
- **Commands in Russian:** Use `тамам` (not `/tamam`) and `отбой` (not `/cancel`)
- **Character restrictions:** Replace "ё" with "е", use "-" instead of long dashes
- **Response tone:** Avoid "plastic" or artificial sounding responses
- **Context is critical:** LLM must see full conversation history for each user
- **User perspective:** Each user sees their own messages + what others sent + empath responses
- **File-based config:** Single pipeline file with embedded configurations, no external references
- **Tool integration:** Use existing `lng_llm_prompt_template` through `tool_registry.py`

## Notes
- Each task should be completed and tested before proceeding to the next
- All file paths use forward slashes for consistency
- JSON responses must be properly escaped
- Character restrictions (no "ё", no long dashes) apply throughout
