# DIDIK — Production Readiness and Hardening

## Role
Act as a senior production engineer, application security specialist, database engineer, and DevOps reviewer.

## Objective
Audit and harden the approved DIDIK MVP for real-world use while preserving its existing functionality and approved design.

## Mandatory First Step: Read-Only Audit

Before making changes:
1. Read the PRD, design specification, implementation notes, and project instructions.
2. Inspect the actual codebase and deployment architecture.
3. Review dependencies, authentication, authorization, data handling, database schema, error handling, and configuration.
4. Identify existing tests and establish a baseline.
5. Produce a prioritized report of findings, severity, impact, and proposed remediation.

Do not change production systems during the initial audit. Request approval for material architectural changes or potentially disruptive remediation.

## Production Requirements

### 1. Application Security
Review and address, as applicable:
- Authentication and session security.
- Server-side authorization and privilege escalation.
- CSRF protection where relevant.
- XSS, SQL injection, unsafe redirects, and insecure URL handling.
- Input validation and output escaping.
- Rate limiting for sensitive endpoints.
- Secure cookie and transport configuration.
- Secret management and environment configuration.
- Error messages and logging that could disclose sensitive information.
- Dependency vulnerabilities and outdated packages.

Apply controls appropriate to the actual framework and hosting environment. Do not add redundant security middleware without understanding the existing stack.

### 2. Child Privacy and Safety
- Minimize the collection of children's personal information.
- Avoid unnecessary public profiles, personal photographs, and precise location data.
- Do not expose children's names, individual performance, or activity history publicly by default.
- Define suitable retention and deletion practices for any stored activity data.
- Ensure analytics do not unnecessarily identify individual children.
- Review relevant Malaysian privacy requirements and any other applicable obligations.
- Obtain qualified legal guidance where compliance interpretation is required.

### 3. Database and Data Integrity
- Review indexes, relationships, constraints, query efficiency, and migration safety.
- Verify that quiz scores and correct answers are determined server-side where appropriate.
- Protect existing data during schema changes.
- Document backup frequency, retention, restoration, and recovery objectives.
- Test restoration in a safe environment where feasible.
- Ensure production migrations have a clear rollback or recovery strategy.

### 4. Performance and Reliability
- Identify slow database queries and expensive application operations.
- Apply caching only where correct invalidation and data freshness can be maintained.
- Optimize assets, images, and loading behavior.
- Reduce unnecessary JavaScript and network requests.
- Handle failed requests and unavailable external resources gracefully.
- Verify performance on mobile devices and slower connections.
- Add suitable health checks and operational logging.

### 5. Content and Admin Operations
- Verify permissions for every administrative operation.
- Validate quiz publication and archival workflows.
- Protect question banks and correct answers from unauthorized disclosure.
- Ensure external Quizizz links are validated and handled safely.
- Confirm that changes to game settings do not break existing quizzes.
- Provide a safe operational workflow for maintaining educational content.

### 6. Deployment and Operations
Document and verify:
- Supported runtime and required extensions.
- Environment variables and secrets.
- Database provisioning and migrations.
- Web server and application process configuration.
- HTTPS and domain configuration.
- File and directory permissions.
- Logging, monitoring, and error reporting.
- Scheduled jobs and queues, if actually used.
- Backup and restoration procedures.
- Deployment, rollback, and recovery procedures.

Do not assume a particular hosting provider or deployment platform. Base recommendations on the actual environment.

## Verification

Run applicable:
- Automated tests.
- Dependency audits.
- Static analysis and linting.
- Authorization and security tests.
- Database migration checks.
- Representative end-to-end user journeys.
- Responsive and accessibility checks.
- Performance checks appropriate to the deployment environment.

Distinguish verified results from recommendations or untested assumptions.

## Deliverables
- Production readiness report.
- Prioritized remediation plan.
- Security and privacy findings.
- Applied code changes with explanations.
- Updated tests and documentation.
- Deployment and rollback checklist.
- Backup and restoration procedure.
- Outstanding risks and operational recommendations.

## Safety Constraints
- Never expose secrets or copy production credentials into reports.
- Never delete production data or run destructive commands without explicit approval.
- Do not disable security controls to make the application work.
- Do not upgrade major dependencies blindly.
- Do not perform production deployment, DNS changes, or infrastructure modifications without explicit approval.
- Preserve existing functionality and avoid unrelated refactoring.

## Completion
Report what was actually tested, what was changed, what remains unresolved, and whether the system is ready for deployment. Do not label the application production-ready while critical issues remain unverified.
