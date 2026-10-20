import sys, asyncio, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'backend')
from simulation.simulator import get_simulator

sim = get_simulator()

async def run_test():
    sim.initialize('scenario_1')
    await sim.start('scenario_1')
    await asyncio.sleep(5)
    await sim.pause()
    state = sim.get_full_state()
    print('Tick:', state['tick'])
    print('Num Emergencies:', len(state['emergencies']))
    for e in state['emergencies']:
        print(f"  Emergency {e['emergency_id']}: status={e['status']}, hospital={e['assigned_hospital']}, ambulance={e['assigned_ambulance']}, replans={e['replan_count']}")
    print()
    for a in state['ambulances']:
        if a['status'] != 'IDLE':
            print(f"  Amb {a['ambulance_id']}: {a['status']} at {a['current_location']}, patient={a['assigned_patient']}")
    print('Total messages:', state.get('analytics', {}).get('total_messages', 0))
    print('Search runs:', len(state.get('analytics', {}).get('search_runs', [])))
    print()
    for pid, plan in state.get('active_plans', {}).items():
        print(f"  Plan {pid} v{plan['version']}: {plan['status']}, step={plan['current_step_index']}/11")

asyncio.run(run_test())
