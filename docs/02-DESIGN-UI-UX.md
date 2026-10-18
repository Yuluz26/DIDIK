# DIDIK — UI/UX Design Concept and Design System

## Role
Act as a senior product designer, UI/UX architect, creative director, and design systems specialist.

## Objective
Translate the approved DIDIK PRD into a distinctive, implementation-ready design concept before building production features.

## Mandatory Skill and Library Discovery

Before designing:
1. Inspect the repository's existing instructions, including AGENTS.md, CLAUDE.md, and other relevant project guidance.
2. Discover the skills and libraries already available in the environment.
3. Where available, study and use:
   - Taste Skill for strong visual direction and design quality.
   - UI/UX Pro Max for design systems, UX patterns, and accessibility guidance.
   - Impeccable for interface critique, visual refinement, and design quality.
4. Inspect each relevant skill's actual instructions and follow its documented workflow.
5. Reuse existing dependencies and approved tools whenever practical.
6. Do not pretend a skill or package was used if it is unavailable.
7. Do not install additional tools without authorization.

If the skills offer conflicting advice, prioritize the approved PRD, usability, accessibility, consistency, and the project's actual constraints.

## Creative Direction

DIDIK should feel like a delightful digital learning world for Malaysian children.

Visual attributes:
- Cute and expressive.
- Soft, tactile neumorphism.
- Pastel surfaces with carefully selected accent colours.
- Friendly characters and original educational motifs.
- Rounded but disciplined geometry.
- Generous whitespace and highly readable typography.
- Subtle, purposeful motion.
- Clear, reassuring feedback after every meaningful interaction.

Create a distinctive art direction instead of copying an existing educational platform.

Neumorphism should be used selectively. Important buttons, text, selected states, and focus indicators must remain accessible and easy to recognize. Avoid low-contrast controls and interfaces that look attractive but are difficult to operate.

## Design the Following Experiences

### Public Website
- Homepage and primary navigation.
- Learning activity discovery.
- Subject and topic browsing.
- Quiz detail and instructions.
- Quiz-playing interface.
- Correct and incorrect answer feedback.
- Progress indicators.
- Quiz completion and reward experience.
- Quizizz external-link collections.
- Empty, loading, error, and unavailable-content states.

### Admin Experience
- Dashboard overview.
- Quiz collection management.
- Question editor and answer configuration.
- Game concept selector and configuration.
- Quizizz link management.
- Publishing workflow.
- Search, filtering, validation, and confirmation states.
- Basic analytics and activity overview where supported by the PRD.

The admin interface must prioritize productivity and clarity. It may share the DIDIK brand but must not sacrifice usability for decorative styling.

## Game Concept System

Develop a reusable design approach for multiple game experiences.

For each proposed game concept, define:
- Its visual identity.
- Core interaction loop.
- Question presentation.
- Answer selection behavior.
- Feedback and reward mechanics.
- Progress and completion states.
- Mobile interaction requirements.
- Accessibility considerations.
- Reusable components and concept-specific components.

Recommend a small, coherent set of game concepts for the MVP. Do not build every proposed game before the core experience is validated.

## Design System Deliverables

Specify:
- Brand principles and visual direction.
- Colour tokens with semantic meanings.
- Typography scale and font recommendations.
- Spacing, sizing, and layout rules.
- Border radii and shadow tokens.
- Neumorphic surface treatments.
- Button, input, modal, navigation, and card patterns.
- Quiz and game interaction components.
- Icon and illustration direction.
- Animation and transition principles.
- Focus, hover, pressed, selected, disabled, success, and error states.
- Responsive breakpoints and mobile-first behavior.
- Accessibility and reduced-motion rules.

## Implementation Guidance

- Inspect the project's actual framework and dependencies before proposing components.
- Prefer the existing stack unless a change is justified and approved.
- Reuse suitable installed libraries instead of reinventing standard functionality.
- Keep design tokens centralized.
- Use reusable components and consistent interaction patterns.
- Avoid unnecessary dependencies and unrelated refactoring.
- Use real interface copy in Bahasa Melayu rather than lorem ipsum.
- Use consistent visual quality across public and admin areas.

## Required Deliverables

Produce:
1. A written UI/UX concept.
2. A documented design system.
3. A sitemap and key user flows.
4. Screen-by-screen layout specifications.
5. A reusable component inventory.
6. A game concept comparison and MVP recommendation.
7. Responsive and accessibility specifications.
8. A design review checklist.
9. An implementation plan for the approved design.

If an existing preview or design environment is available, create a representative prototype of the most important screens. Clearly distinguish a prototype from a working backend.

## Constraints
- Do not begin full application implementation.
- Do not modify unrelated functionality.
- Do not use generic dashboard templates as the final visual direction.
- Do not create purely decorative controls that imply nonexistent functionality.
- Do not claim that a design has been browser-tested unless it has actually been tested.

## Completion
Save the design documentation and any approved design artifacts using the project's existing conventions. Summarize the visual direction, component strategy, and decisions requiring approval. Stop before MVP implementation.
