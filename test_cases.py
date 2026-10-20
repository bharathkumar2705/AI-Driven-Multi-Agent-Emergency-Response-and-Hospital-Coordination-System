import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_search_algorithms():
    print("\n--- 1. Testing Search Algorithms ---")
    from simulation.city_grid import get_city_graph
    from search.graph import SearchGraph
    from search.bfs import bfs
    from search.astar import astar
    
    cg = get_city_graph()
    sg = SearchGraph(cg)
    start, goal = (0, 0), (9, 9)
    
    res_bfs = bfs(sg, start, goal)
    res_astar = astar(sg, start, goal)
    
    print(f"BFS Path Length: {len(res_bfs.path)}")
    print(f"BFS Nodes Expanded: {res_bfs.nodes_expanded}")
    print(f"A* Path Length: {len(res_astar.path)}")
    print(f"A* Nodes Expanded: {res_astar.nodes_expanded}")
    assert len(res_bfs.path) == len(res_astar.path)
    assert res_astar.nodes_expanded <= res_bfs.nodes_expanded
    print("Search algorithms passed.")

def test_knowledge_and_forward_chaining():
    print("\n--- 2. Testing Knowledge Base & Forward Chaining ---")
    from knowledge.knowledge_base import KnowledgeBase
    from reasoning.forward_chaining import forward_chain
    
    kb = KnowledgeBase()
    kb.assert_fact('patient_requires_icu', patient='P001')
    kb.assert_fact('hospital_icu_available', hospital='H1')
    
    derivations = forward_chain(kb)
    derived = [d.to_dict()['derived_fact']['predicate'] for d in derivations]
    
    print("Derived facts:", derived)
    assert 'hospital_satisfies_icu' in derived
    print("Forward chaining passed.")

def test_backward_chaining():
    print("\n--- 3. Testing Backward Chaining ---")
    from knowledge.knowledge_base import KnowledgeBase
    from reasoning.backward_chaining import can_hospital_treat_patient
    
    kb = KnowledgeBase()
    kb.assert_fact('patient_requires_icu', patient='P001')
    kb.assert_fact('hospital_icu_available', hospital='H1')
    kb.assert_fact('hospital_satisfies_icu', hospital='H1', patient='P001')
    kb.assert_fact('hospital_satisfies_specialist', hospital='H1', patient='P001')
    kb.assert_fact('hospital_eligible_for_patient', hospital='H1', patient='P001')
    
    res = can_hospital_treat_patient('H1', 'P001', kb)
    print(f"Goal proved? {res.proved}")
    assert res.proved == True
    print("Backward chaining passed.")

def test_utility_decision_making():
    print("\n--- 4. Testing Utility-Based Decision Engine ---")
    from decision.utility_engine import select_best_hospital
    from simulation.city_grid import get_city_graph
    
    patient = {"patient_id": "P001", "location": {"row": 0, "col": 0}, "severity": "CRITICAL"}
    hospitals = [
        {"hospital_id": "H1", "location": {"row": 0, "col": 1}, "icu_available": 0, "available_beds": 10},
        {"hospital_id": "H2", "location": {"row": 9, "col": 9}, "icu_available": 5, "available_beds": 10}
    ]
    doctors = []
    
    best, all_scores = select_best_hospital(hospitals, patient, doctors, get_city_graph(), [0, 0])
    
    print(f"Selected hospital: {best['hospital_id']} (Score: {best['utility_score']:.2f})")
    assert best['hospital_id'] == "H2" # H1 is closer but has no ICU, and patient is CRITICAL
    print("Utility engine passed.")

if __name__ == "__main__":
    print("Running FOAI Core AI Engine Tests...")
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        test_search_algorithms()
        test_knowledge_and_forward_chaining()
        test_backward_chaining()
        test_utility_decision_making()
        print("\n[SUCCESS] All core AI logic tests passed successfully!")
    except AssertionError as e:
        print("\n[FAIL] Test failed:", e)
    except Exception as e:
        print("\n[ERROR] Error during testing:", e)
