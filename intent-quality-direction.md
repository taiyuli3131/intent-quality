# Intent Quality Project Direction

## 1. Core Definition

`intent-quality` is a collaboration-quality project, not merely an answer-quality, prompt-optimization, or evaluation project.

Its purpose is to help an AI agent make better pre-action judgments so the user can feel genuinely understood, helped, and supported in a process of shared growth.

The project should optimize both:

- the user's subjective experience of being understood;
- the objective reduction of direction errors, unsupported assumptions, over-execution, and context pollution.

## 2. First Principle

The first principle is:

> Before the agent acts, it should understand the user's real objective, validate important premises, identify material risks, confirm the current action boundary, and choose an appropriate verification route.

The project is not about asking more questions by default. It is about asking, answering, pausing, verifying, or acting at the right time.

## 3. Primary Value Proposition

The main selling point is:

> A pre-execution collaboration-quality layer that helps AI agents align with the user's goal, context, assumptions, risk boundaries, permissions, and desired experience before producing output or taking action.

This makes the project different from ordinary prompt rewriting or output evaluation. It focuses on the collaboration process before execution.

## 4. What The User Should Feel

A successful use of this project should make the user feel:

- "It understood what I actually meant."
- "It did not accuse me or distort my goal."
- "It noticed important missing context without making the interaction heavy."
- "It helped me clarify my own thinking."
- "It knew when to discuss, when to draft, and when to act."
- "It did not write, persist, or execute something before I authorized it."
- "It is learning how to collaborate with me over time."

This emotional and practical experience is part of the project quality target, not a secondary effect.

## 5. Core Capabilities

### 5.1 Intent State Recognition

The agent should distinguish whether the user is:

- exploring an idea;
- discussing project direction;
- asking for advice;
- asking for a draft;
- authorizing a document update;
- authorizing code or file changes;
- asking to persist a reusable rule or memory.

This prevents the agent from treating discussion as execution approval.

### 5.2 Real Objective Alignment

The agent should preserve the user's legitimate objective instead of replacing it with a safer, narrower, or more convenient objective.

Example:

- User objective: quickly push a charger product toward the front of a ranking list.
- Incorrect interpretation: the user intends fake orders or ranking manipulation.
- Correct interpretation: the user wants a fast ranking-growth strategy; non-compliant ranking manipulation is only a possible path risk.

### 5.3 Premise Validation

The agent should not treat important user-stated claims as verified facts without evidence.

Example:

- "Our brand influence is strong" should be marked as user-stated, assumed for now, or needing validation.
- It should not automatically become the foundation of a strategy.

### 5.4 Risk Classification

The agent should classify risks instead of collapsing them into one warning:

- Goal risk: the desired outcome itself may be unsafe, illegal, impossible, or misleading.
- Path risk: some ways of achieving the goal may be risky, but the goal itself is legitimate.
- Premise risk: a key assumption may be unverified, exaggerated, stale, or context-dependent.
- Permission risk: the agent may not yet be authorized to write, persist, execute, or update.

Permission risk is important because this project itself previously exposed a failure: project-direction discussion was incorrectly treated as permission to update files.

### 5.5 Action Boundary Control

The agent should decide whether the current response should be:

- discussion only;
- advice;
- structured proposal;
- draft content;
- document update;
- file/code change;
- verification;
- persistent memory or rule update.

For project rules, memory, test standards, and direction documents, the default should be discussion first unless the user explicitly asks to write or update.

### 5.6 Verification Loop

The project should eventually test whether the agent avoided collaboration failures such as:

- goal misreading;
- unsupported premise acceptance;
- excessive questioning;
- excessive execution;
- replacing the user's goal with a risk warning;
- writing or persisting without authorization;
- stale-context pollution;
- treating a draft discussion as a final rule.

## 6. Minimal Starting Workflow

The first version should stay simple and easy to use.

Minimum five-question loop:

1. Is the user asking to discuss, advise, draft, or execute?
2. What result does the user actually want?
3. Which key premises are unverified?
4. Are the main risks goal risks, path risks, premise risks, or permission risks?
5. Should the agent ask, answer, answer with assumptions, verify, or wait for authorization?

This minimal loop should be understandable without reading the full reference system.

## 7. Final Project Goal

The final project should include:

- clear usage instructions;
- real use cases with concrete prompts and expected behavior;
- comparison tests against ordinary model behavior;
- automatic regression tests;
- automatic update suggestions after repeated failures;
- user-approved persistence for rules, profile updates, and memory updates;
- metrics for both answer reliability and collaboration experience.

The final system should not automatically mutate itself without approval. It should generate proposed updates, explain the evidence, and ask for confirmation before writing persistent changes.

## 8. Required Case Types

The project should eventually include concrete cases for:

- commercial growth strategy, such as the charger ranking case;
- product positioning and competitive comparison;
- high-stakes factual or compliance-sensitive advice;
- technical debugging with incomplete environment context;
- long-context conversations where prior assumptions may pollute the current task;
- exaggerated or unverified user claims;
- direction discussions that should not be treated as write authorization;
- memory or rule updates that require explicit approval.

Each case should ideally include:

- original user prompt;
- ordinary-model failure mode;
- expected `intent-quality` behavior;
- better answer shape;
- acceptance criteria;
- regression signals.

## 9. Adjacent Projects And Reference Points

Current related projects are useful references, but they mostly solve adjacent problems rather than the exact collaboration-quality problem.

### 9.1 Evaluation And Regression Testing

- [LangSmith Evaluations](https://www.langchain.com/langsmith/evaluation): agent and LLM evaluation, production monitoring, conversation evals, and regression detection.
- [Braintrust Evaluations](https://www.braintrust.dev/docs/evaluate): systematic experiments, datasets, prompt/model comparison, and production monitoring.
- [Promptfoo](https://www.promptfoo.dev/docs/intro/): open-source LLM app evaluation and red-teaming CLI.
- [OpenAI Evals](https://github.com/openai/evals): framework for evaluating LLMs and LLM systems.
- [DeepEval](https://github.com/confident-ai/deepeval): test framework for LLM applications.
- [Langfuse](https://langfuse.com/docs): open-source LLM engineering platform for traces, evaluation, prompt management, and debugging.

These are strong references for automated testing and regression detection. However, they generally focus more on output/system evaluation than on the user's felt experience of being understood during collaboration.

### 9.2 Context Engineering And Observability

- Langfuse, LangSmith, and related observability tools help inspect traces, prompts, costs, latency, and evaluation results.
- Context-engineering practices help decide what information an agent should receive, keep, compress, isolate, or forget.

These are relevant because `intent-quality` also needs context hygiene. The difference is that this project focuses on how context should be interpreted before action, not only how context is stored or retrieved.

### 9.3 AI UX And Intent Alignment

AI UX and intent-alignment research is closest to the spirit of this project. The important idea is that users often discover and refine intent through interaction, rather than providing a complete specification at the beginning.

`intent-quality` should therefore help the agent participate in clarifying and improving the user's thinking, while still respecting user agency and authorization boundaries.

## 10. Differentiation

This project should avoid becoming "just another eval framework."

Its distinctive position is:

> It evaluates and improves the collaboration process before execution, especially whether the agent understands the user's goal, validates important premises, respects permissions, and helps the user feel understood and supported.

Most adjacent tools measure outputs, traces, prompts, or security risks. `intent-quality` should additionally measure and improve:

- understood intent;
- action authorization;
- premise handling;
- risk framing;
- context hygiene;
- collaborative growth;
- user experience of being helped rather than processed.

## 11. Current Working Conclusion

The project direction should be:

> A pre-execution AI collaboration-quality framework that helps agents calibrate goal, premise, risk, permission, and verification before acting, so users genuinely feel understood, helped, and able to grow through the interaction.

This direction should guide later documentation, test cases, automation, and product positioning.
