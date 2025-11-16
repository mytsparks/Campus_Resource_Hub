# High-Impact Prompts

Prompts that resulted in significant architectural or implementation improvements will be stored here.

---

## Golden Prompt 1: Initial Project Structure Creation

**Prompt:**
Create a complete file and folder structure for a Python/Flask project named "CampusResourceHub." This project must follow an MVC pattern, include a Data Access Layer (DAL) separation, and adhere to an AI-First Development folder structure. All Python files should contain only basic imports and function/class definitions (no logic), and all HTML files should have a basic HTML5/Bootstrap 5 template structure extending a base layout.

**Why This Prompt is Golden:**
This prompt established the entire architectural foundation of the project. By requesting MVC + DAL separation and AI-First Development structure upfront, it ensured:
- **Separation of Concerns:** Clear boundaries between controllers, views, and data access
- **Maintainability:** The DAL pattern made database operations testable and reusable
- **Context Preservation:** The `.prompt/` and `docs/context/` folders maintained project knowledge across sessions
- **Scalability:** The skeleton structure allowed incremental implementation without breaking changes
- **Best Practices:** Following established patterns from the start prevented technical debt

The prompt's specificity about "no logic" in skeleton files forced a thoughtful, incremental approach that made the codebase easier to understand and modify. This foundation enabled all subsequent development to proceed smoothly.

---

## Golden Prompt 2: Comprehensive Feature Implementation

**Prompt:**
Below is a list of the remaining requirements that need to be fulfilled... Carry out the necessary changes that can be done to implement these, and be sure to adhere to: 1. the current styling and structure of the website (ensuring mobile display scaling) 2. Ensure the app can still be tested locally while also deployed to the cloud platform 3. Adhere to the MVC structure and functionality of the program.

**Why This Prompt is Golden:**
This prompt demonstrated exceptional constraint management and comprehensive thinking:
- **Multi-Constraint Adherence:** Successfully balanced styling preservation, local/cloud compatibility, and architectural integrity
- **Feature Completeness:** Implemented role-based access control, approval workflows, conflict detection, reviews, dashboards, and security features in one cohesive pass
- **Architectural Consistency:** Maintained MVC + DAL patterns throughout, ensuring code quality
- **Production Readiness:** Addressed security, testing, and documentation requirements simultaneously

The prompt's emphasis on maintaining existing structure while adding features prevented regression and ensured backward compatibility. The comprehensive scope required systematic analysis and implementation, resulting in a production-ready application rather than a collection of features.

---

## Golden Prompt 3: Security and Route Review

**Prompt:**
Check all other routes too, I'm nearing the final deployment for the project due date so i want everything to work.

**Why This Prompt is Golden:**
This prompt exemplifies proactive quality assurance and risk mitigation:
- **Comprehensive Audit:** Triggered a systematic review of all routes, catching multiple security vulnerabilities
- **Critical Issue Discovery:** Found GET requests for state-changing operations, missing CSRF protection, and error handling gaps
- **Production Readiness:** Addressed issues before deployment, preventing potential exploits and user experience problems
- **Pattern Recognition:** Established consistent security patterns (POST for state changes, CSRF on all forms) across the entire application

The prompt's timing (before final deployment) and scope (all routes) demonstrated the importance of thorough review phases. The systematic approach caught issues that could have compromised security or functionality in production. This type of comprehensive review prompt is essential for any production deployment.
