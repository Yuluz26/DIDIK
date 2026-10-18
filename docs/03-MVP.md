# DIDIK — MVP Implementation

## Role
Act as a senior full-stack engineer, software architect, and quality-focused product developer.

## Objective
Implement the approved DIDIK PRD and UI/UX design as a functional, testable minimum viable product.

## Mandatory Pre-Implementation Checks

Before changing code:
1. Read the approved PRD and UI/UX design documents.
2. Inspect the current repository, project instructions, dependencies, database schema, and existing functionality.
3. Discover and follow the available Taste Skill, UI/UX Pro Max, Impeccable, and other relevant installed skills.
4. Identify the actual framework, runtime, database, and local development workflow.
5. Create a concise implementation plan with dependencies and acceptance criteria.
6. Identify missing decisions that could materially affect architecture or data integrity.

Do not silently replace the approved stack or redesign the approved concept.

## MVP Functional Scope

### 1. Public Learning Experience
- Build the approved DIDIK homepage and navigation.
- Display published learning activities.
- Support browsing and filtering by the available subject, topic, level, and difficulty fields.
- Provide a quiz introduction screen.
- Allow children to answer supported question types.
- Show answer feedback and calculate scores correctly.
- Display completion results and a clear way to return to learning activities.
- Handle unavailable content, empty collections, loading, and errors gracefully.

### 2. Quiz and Question Management
Implement administrative CRUD for:
- Quiz collections.
- Questions and answer options.
- Correct answers and optional explanations.
- Question order and scoring.
- Relevant categorization and difficulty metadata.
- Draft and published states.

Use server-side validation and enforce data integrity. Only authorized administrators may manage content.

### 3. Game Concept Selection
- Implement a reusable game presentation architecture.
- Build the MVP game concepts approved in the design phase.
- Allow administrators to assign a supported concept to a quiz.
- Persist and validate concept-specific settings.
- Ensure that switching presentation concepts does not corrupt the underlying questions or scoring.
- Keep shared quiz logic separate from game-specific presentation.

Do not create nonfunctional concept selectors or claim that a game is implemented when it is only a visual mockup.

### 4. Quizizz Link Collection
Implement an admin-managed external resource library.

Include:
- Create, edit, delete, search, and categorize link records.
- Store titles, URLs, descriptions, tags, and supported metadata.
- Publish or unpublish records.
- Display published links in the appropriate public collection.
- Open external activities using safe link handling.
- Validate URLs and provide understandable errors.

Do not scrape private content, bypass access controls, or assume that an external link can be embedded or imported. Store links as external resources unless a verified integration is approved.

### 5. Administration and Authentication
- Implement protected admin routes and server-side authorization.
- Provide a usable dashboard and navigation.
- Add secure validation and error handling.
- Keep administrative actions inaccessible to ordinary visitors.
- Use the existing authentication system if one exists and is suitable.

Do not introduce child accounts, public profiles, leaderboards, or unnecessary personal-data collection unless explicitly approved.

### 6. Persistence and Data Integrity
- Use the project's existing database and migration conventions.
- Create appropriate relationships, constraints, and indexes.
- Preserve existing records and unrelated tables.
- Use transactions for operations that require atomic changes.
- Include repeatable development seed data where appropriate.
- Never seed demonstration records into production automatically.

### 7. Responsive Design
Implement the approved design for:
- Mobile phones.
- Tablets.
- Desktop screens.

Prioritize touch-friendly interactions, readable questions, large answer targets, and consistent feedback.

## Engineering Standards

- Reuse suitable existing dependencies and project patterns.
- Keep changes scoped to DIDIK requirements.
- Avoid unnecessary abstractions and overengineering.
- Keep secrets and credentials out of source control.
- Enforce authorization on the server, not just in the interface.
- Escape and validate user-controlled content appropriately.
- Handle failures without exposing sensitive implementation details.
- Follow the approved design tokens and component system.

## Testing and Acceptance

Test:
- Creating, editing, publishing, and archiving quizzes.
- Creating questions and validating answers.
- Scoring and completion calculations.
- Game concept assignment and rendering.
- Quizizz link CRUD and external navigation.
- Unauthorized admin access.
- Invalid input and database errors.
- Responsive behavior and important user journeys.

Run the existing test suite and relevant available static checks. Add focused tests for new behavior. Report any checks that could not run.

## Deliverables
- Working MVP implementation.
- Required database migrations.
- Reusable interface components.
- Functional admin management.
- Implemented MVP game concepts.
- Quizizz link collection.
- Tests and setup instructions.
- Updated documentation.
- A concise list of completed features, limitations, and remaining issues.

## Constraints
- Do not silently remove existing features.
- Do not make unrelated structural or visual changes.
- Do not bypass failing tests or disable validation to obtain a passing result.
- Do not claim functionality is complete without verifying it.
- Do not deploy to production without explicit approval.

## Completion
Verify the important user journeys, summarize test results, and document any known limitations. Stop before production hardening and deployment.
