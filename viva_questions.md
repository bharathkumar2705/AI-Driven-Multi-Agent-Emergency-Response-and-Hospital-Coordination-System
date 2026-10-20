# FOAI Viva Questions and Answers

This document contains potential questions and answers for a final year project defense or case study presentation on the **AI-Driven Multi-Agent Emergency Response System**.

## 1. Multi-Agent Systems & PEAS Framework

**Q1: What is a Multi-Agent System (MAS)? Why use it here instead of a monolithic system?**
**A:** A Multi-Agent System consists of multiple interacting, autonomous entities (agents). In a monolithic CRUD app, a central controller makes all decisions. In MAS, agents (Ambulance, Hospital, Traffic) act based on local knowledge, mimicking real-world decentralization. It allows for better scalability, fault tolerance, and dynamic adaptation to changes (like a road block).

**Q2: Explain the PEAS framework using one of your agents.**
**A:** PEAS stands for Performance measure, Environment, Actuators, and Sensors. 
For the **Ambulance Agent**:
- **Performance:** Minimize time to patient, minimize patient transport time.
- **Environment:** City grid, roads, traffic state, hospitals.
- **Actuators:** Move North/South/East/West, pick up patient, drop off patient.
- **Sensors:** GPS (current location), traffic updates via Message Bus.

**Q3: How do the agents communicate?**
**A:** They use an asynchronous Message Bus implementing the Publish/Subscribe pattern. Agents don't call each other's functions directly; they emit messages (e.g., `EMERGENCY_REQUEST`) and subscribe to topics relevant to their goals.

## 2. Search & Pathfinding Algorithms

**Q4: You implemented BFS, DFS, UCS, Greedy, and A\*. Which one does the system use by default and why?**
**A:** The system defaults to **A\* (A-Star)**. A\* is both optimal (finds the shortest path) and complete (guaranteed to find a path if one exists) provided the heuristic is admissible. It expands far fewer nodes than BFS/UCS by combining the exact cost so far $g(n)$ with the estimated remaining cost $h(n)$.

**Q5: What heuristic did you use for A\*, and is it admissible?**
**A:** I used the Manhattan Distance heuristic because the city is a grid where agents can only move in 4 cardinal directions (no diagonals). It is admissible because it never overestimates the true cost—at best, the path is entirely clear and equal to the Manhattan distance.

**Q6: Why is Uniform Cost Search (UCS) implemented?**
**A:** In a simple unweighted grid, BFS is sufficient for shortest paths. However, our system models realistic city traffic where roads have different weights and congestion multipliers (MODERATE = 1.5x, CONGESTED = 2.5x, BLOCKED = ∞). UCS expands paths in order of cumulative cost $g(n)$, guaranteeing the cheapest overall route when edge costs vary and no heuristic is available.

**Q6a: Does every algorithm produce the same path length?**
**A:** **No.** Path length represents the number of steps/hops in the route. 
- **BFS** strictly guarantees the **minimum path length** (fewest hops), regardless of edge weights.
- **DFS** can take long, winding paths (e.g., 15+ nodes when a 13-node path exists) because it explores deep along single branches.
- **UCS and A\*** optimize for **minimum total path cost** (sum of edge weights), not hop count. If a direct 18-step path is heavily congested, UCS and A* will intentionally take a 22-step detour if that detour has a lower overall cost.

**Q6b: What is the exact difference between "Path Length" and "Path Cost"?**
**A:** 
- **Path Length**: The number of nodes/edges traversed from start to goal (pure hop count).
- **Path Cost**: The numerical sum of all edge weights (travel time, congestion delay, fuel cost) along that path.
BFS minimizes path length; UCS and A* minimize path cost.

**Q6c: In the default test from (0,0) to (9,9), why did all algorithms have a path length of 19 nodes?**
**A:** On an open 10×10 grid without obstacles, the Manhattan distance between (0,0) and (9,9) is $|9 - 0| + |9 - 0| = 18$ steps (19 nodes). Any path moving strictly Right and Down takes exactly 18 steps. Because the goal was at the opposite corner, the algorithms coincidentally found paths of 18 hops. However, their **total costs** and **nodes expanded** differed significantly (e.g., BFS had cost 34.0 and 100 expansions, whereas A* had cost 21.5 and only 85 expansions). Changing the start/goal (e.g. from (2,1) to (8,7)) immediately reveals different path lengths (BFS = 13 nodes, DFS = 15 nodes).

## 3. Knowledge Representation & Reasoning

**Q7: How is knowledge represented in your system?**
**A:** The system uses First-Order Predicate Logic stored in a Knowledge Base (KB). Facts are asserted as predicates with arguments, such as `hospital_icu_available(hospital=H1)`.

**Q8: Explain Forward Chaining. How is it used in your project?**
**A:** Forward chaining is data-driven reasoning. It starts with known base facts and applies inference rules until no new facts can be derived (a fixpoint). In the project, when a patient requires an ICU and a hospital has one, the rule fires to derive `hospital_satisfies_icu`.

**Q9: Explain Backward Chaining. How does it differ from Forward Chaining?**
**A:** Backward chaining is goal-driven. It starts with a specific query or goal (e.g., "Can Hospital H1 treat Patient P001?") and works backward through the rules to see if the required base facts exist. Forward chaining generates *all* possible conclusions from the data, while backward chaining only searches paths relevant to the specific goal.

## 4. Utility-Based Decision Making

**Q10: What is a Utility-Based Agent?**
**A:** An agent that maps states to a real number (utility score) representing the "degree of happiness" or desirability of that state, allowing the agent to choose the action that maximizes expected utility.

**Q11: How does your Decision Engine rank hospitals?**
**A:** It computes a utility score between 0 and 1 using a weighted sum of normalized factors:
$U = (W_{dist} \times (1 - norm(distance))) + (W_{icu} \times icu\_ratio) + (W_{bed} \times bed\_ratio)$
Crucially, the weights are dynamic based on patient severity. For a CRITICAL patient, $W_{icu}$ is given high weight, whereas for a LOW severity patient, $W_{dist}$ is prioritized.

## 5. Planning and Uncertainty

**Q12: How does the system handle a dynamic, changing environment?**
**A:** Through continuous state monitoring and **Replanning**. The environment is stochastic (traffic can happen at any time). If an ambulance is en route and a road becomes blocked, or if a target hospital's ICU fills up, the execution of the 11-step EmergencyPlan is invalidated. The Coordinator Agent detects this failure and generates a new plan version based on the new environment state.

**Q13: Why did you not use Machine Learning for this project?**
**A:** The goal of the FOAI (Fundamentals of AI) syllabus is to demonstrate classical AI concepts—search spaces, logic, reasoning, and heuristics. While ML is powerful for pattern recognition, classical AI provides transparent, rule-based, and deterministic systems that are highly interpretable for critical systems like emergency routing.
