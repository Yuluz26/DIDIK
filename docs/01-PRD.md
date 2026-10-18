# DIDIK — Product Requirements Document (PRD)

## Role
Act as a senior product manager, education technology consultant, and software architect.

## Project Overview
Plan a web-based educational platform called **DIDIK**, designed primarily for Malaysian parents and children who need accessible, engaging home-learning activities, including during haze-related school disruptions.

DIDIK should make learning feel like playing a delightful educational game rather than completing a conventional worksheet.

## Core Product Requirements

### 1. Public Learning Platform
- A welcoming homepage explaining DIDIK and how it works.
- Child-friendly navigation and age-appropriate visual language.
- A browsable collection of educational quizzes and learning activities.
- Organize content by subject, topic, school level, age range, and difficulty where appropriate.
- Allow children to participate without unnecessary registration barriers.
- Support responsive layouts for mobile phones, tablets, and desktops.
- Use Bahasa Melayu as the primary interface language.
- Design for accessibility, readability, and children using shared family devices.

### 2. Interactive Quiz System
- Support question banks and reusable quiz collections.
- Support multiple-choice questions and other question types only where justified by the product scope.
- Allow administrators to configure correct answers, explanations, question order, and scoring.
- Support configurable attempts, feedback, timers, and progress tracking where appropriate.
- Provide immediate, friendly feedback and a meaningful completion screen.
- Keep the quiz content model independent from its visual game presentation.

### 3. Configurable Game Concepts
Administrators must be able to select a supported game concept for a quiz or activity.

Potential concepts to evaluate include:
- Cute adventure and character journeys.
- Collecting stars, badges, and rewards.
- Memory matching.
- Interactive treasure hunts.
- Question-and-answer challenges.
- Gentle timed challenges.
- Progression through themed levels.

These are candidate concepts, not a requirement to build every game immediately. Recommend an achievable MVP set and a scalable architecture for adding more concepts later.

### 4. Admin Dashboard
Provide a protected administrative area for managing:
- Quiz collections and categories.
- Questions, answers, explanations, and scoring rules.
- Game concept assignments and supported configuration options.
- Draft, published, and archived content.
- Quiz visibility and availability.
- Quizizz collection links.
- Basic activity and completion statistics, where feasible.

Question creation and editing should be efficient. Administrators must not need to edit source code to add new questions or publish learning activities.

### 5. Quizizz Link Collection
DIDIK must support an administrative module for storing and managing existing Quizizz quiz links created by the administrator.

Required capabilities:
- Create, edit, delete, categorize, and publish link records.
- Store a title, external URL, description, subject, school level, relevant tags, and optional thumbnail.
- Provide an obvious action for opening the original Quizizz activity.
- Organize links into curated collections.
- Validate URL formats and handle unavailable or invalid links gracefully.

Treat these as external resources unless a supported and authorized integration is established. Do not assume that Quizizz links can be imported, scraped, embedded, or converted into native DIDIK quizzes automatically. Investigate the supported options and document any restrictions.

### 6. Design Direction
The intended visual identity is:
- Cute, charming, playful, and trustworthy.
- Soft neumorphism with clear visual hierarchy.
- Carefully controlled pastel colours.
- Friendly characters, delightful illustrations, rounded surfaces, and tactile controls.
- Subtle shadows, polished transitions, and meaningful feedback.
- A premium, professionally art-directed result rather than a generic AI-generated template.

Avoid excessive gradients, random floating decorations, emoji-only interfaces, repetitive card grids, excessive glassmorphism, and poor text contrast.

## Product Planning Requirements

Before implementation:
1. Inspect the existing project, repository structure, and available documentation.
2. Identify the target users, primary user journeys, and important usability constraints.
3. Define the product scope and distinguish MVP features from future enhancements.
4. Document functional requirements and acceptance criteria.
5. Propose a suitable technical architecture based on the existing project and actual deployment constraints.
6. Define the data model and relationships for users, quiz collections, questions, answers, game concepts, and external Quizizz links.
7. Identify security, privacy, accessibility, performance, and content-management requirements.
8. Define measurable success criteria.
9. Document assumptions, unresolved decisions, risks, and dependencies.

## Required Deliverables
Create a comprehensive PRD covering:
- Product vision and objectives.
- User personas and use cases.
- Functional and non-functional requirements.
- User journeys and information architecture.
- MVP scope and explicit exclusions.
- Proposed data model.
- Recommended technical architecture.
- Security and child-privacy considerations.
- Acceptance criteria and testing strategy.
- Risks, dependencies, and open questions.
- A phased implementation roadmap.

## Constraints
- Do not begin feature implementation during this phase.
- Do not install packages, modify production configuration, or run destructive commands.
- Do not assume an existing technology stack without inspecting the repository.
- Avoid overengineering.
- Do not invent external integration capabilities.
- Preserve existing project structure and unrelated functionality.

## Completion
Save the PRD in the project's documentation directory, using the existing documentation conventions where possible. Summarize the proposed scope, assumptions, and outstanding decisions. Stop and wait for approval before proceeding to UI/UX design.
