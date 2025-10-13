# Platform-Inspired Features

This document describes how the Personal Learning Portal adapts best-in-class features from existing learning platforms (Canvas, EducateMe, Valamis) to the domain of corporate forecasting and structural breaks.

---

## Canvas LMS Adaptations

### 1. **Modules with Prerequisites**
- **Original Feature:** Canvas organizes content into sequential modules with prerequisite requirements (e.g., "Complete Module 1 before accessing Module 2").
- **Our Adaptation:** Six modules (Mechanisms, Detection, Overlays, Nowcasting, Evaluation, Reflection) with gated progress. Learners must mark modules as "completed" before unlocking dependent modules. Sidebar displays progress bar and module checkboxes.
- **Value:** Ensures foundational understanding before advancing to complex topics like regime-switching or nowcasting.

### 2. **Mastery Paths**
- **Original Feature:** Canvas allows instructors to create differentiated learning paths based on quiz performance or learner goals.
- **Our Adaptation:** Three predefined paths (QuickStart, QuantDeepDive, OpsPlaybooks) map to different module subsets. Learners select a path in the sidebar, and the app highlights required modules and tracks path-specific progress.
- **Value:** Personalized learning journeys for practitioners with different roles (e.g., analysts vs. risk managers vs. quants).

### 3. **Embedded Assessments**
- **Original Feature:** Inline quizzes and assignments within modules.
- **Our Adaptation:** Micro-survey after each RAG Q&A interaction (Helpful: Y/N, Novelty: 0–2, Confidence: 0–2). Results logged to JSONL for analytics.
- **Value:** Real-time feedback on content quality and learner self-assessment.

---

## EducateMe Adaptations

### 1. **Micro-Surveys & Pulse Checks**
- **Original Feature:** EducateMe uses brief surveys to gauge learner sentiment and comprehension after each lesson.
- **Our Adaptation:** Post-answer micro-survey with three dimensions: Helpful (binary), Novelty (3-point scale), Confidence (3-point scale). Logged with timestamps and query metadata.
- **Value:** Tracks engagement and perceived learning gains; informs content iteration.

### 2. **Kanban-Style Progress Boards**
- **Original Feature:** Visual Kanban boards showing task completion status (To Do, In Progress, Done).
- **Our Adaptation:** Sidebar progress bar and module checkboxes visualize completion status. Weekly Analytics card displays aggregated metrics (helpful rate, recall@5, groundedness) as a "dashboard tile."
- **Value:** Transparent progress tracking and data-driven insights into learning effectiveness.

---

## Valamis Adaptations

### 1. **Learning Paths with Analytics**
- **Original Feature:** Valamis offers curated learning paths with detailed analytics (time-on-task, completion rates, skill gaps).
- **Our Adaptation:** Three paths (QuickStart, QuantDeepDive, OpsPlaybooks) with per-path module requirements. Weekly Analytics card computes:
  - **Helpful Rate:** % of queries marked "Helpful."
  - **Avg Recall@5:** Proxy metric from eval_basic.py.
  - **Groundedness Proxy:** Cosine similarity between answer and top-5 chunks.
  - **Time-on-Module:** Session duration per module (logged in JSONL).
  - **Next Best Action:** Suggested focus area based on low metrics.
- **Value:** Evidence-based recommendations for improvement.

### 2. **Competency-Based Progression**
- **Original Feature:** Valamis tracks skill mastery (beginner → intermediate → advanced) and recommends next steps.
- **Our Adaptation:** Implicit competency tracking via module gating and path completion. "Next Best Action" in Analytics card suggests modules or queries based on gaps (e.g., low recall on "Nowcasting" queries → recommend Nowcasting module).
- **Value:** Adaptive scaffolding aligned with learner performance.

---

## Summary Table

| Platform   | Feature                     | Our Adaptation                                      | Benefit                              |
|------------|-----------------------------|-----------------------------------------------------|--------------------------------------|
| Canvas     | Modules + Prerequisites     | Gated 6-module progression with checkboxes          | Structured learning path             |
| Canvas     | Mastery Paths               | 3 predefined paths (QuickStart, QuantDeepDive, Ops) | Personalized role-based learning     |
| Canvas     | Embedded Assessments        | Micro-survey (Helpful/Novelty/Confidence)           | Real-time feedback & self-assessment |
| EducateMe  | Micro-Surveys               | Post-answer 3-question pulse check                  | Engagement tracking                  |
| EducateMe  | Kanban Boards               | Progress bar + Analytics card                       | Visual progress & metrics            |
| Valamis    | Learning Paths + Analytics  | Paths + Weekly Analytics (4 metrics + action)       | Data-driven improvement              |
| Valamis    | Competency Progression      | Module gating + "Next Best Action" suggestions      | Adaptive scaffolding                 |

---

**Assignment Alignment:**  
This document satisfies Step 2 (Platform-Inspired Features) by explicitly mapping established LMS/LEP capabilities to our domain-specific implementation.
