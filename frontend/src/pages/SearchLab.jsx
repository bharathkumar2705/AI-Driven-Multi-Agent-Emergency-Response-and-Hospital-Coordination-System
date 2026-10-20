import { useState, useCallback, useRef, useEffect } from 'react';
import { api } from '../services/api';

const GRID = 10;
const ALGO_INFO = {
  bfs:    { name: 'BFS', color: '#3b82f6', desc: 'Uninformed: explores level by level. Finds shortest path (hops).' },
  dfs:    { name: 'DFS', color: '#8b5cf6', desc: 'Uninformed: explores depth first. Not optimal, good for exploration.' },
  ucs:    { name: 'UCS', color: '#10b981', desc: 'Cost-based: expands lowest path cost. Optimal with varying costs.' },
  greedy: { name: 'Greedy', color: '#f59e0b', desc: 'Informed: uses heuristic h(n) only. Fast but not optimal.' },
  astar:  { name: 'A*', color: '#ef4444', desc: 'Informed: f(n)=g(n)+h(n). Optimal + efficient with admissible heuristic.' },
};
const ALGOS = Object.keys(ALGO_INFO);

const PAD = 24;

function SearchCanvas({ result, start, goal, gridSize = GRID }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const cellW = (W - PAD * 2) / (gridSize - 1);
    const cellH = (H - PAD * 2) / (gridSize - 1);
    const toXY = (r, c) => ({ x: PAD + c * cellW, y: PAD + r * cellH });

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#0a0d14';
    ctx.fillRect(0, 0, W, H);

    // Grid lines
    for (let r = 0; r < gridSize; r++) {
      for (let c = 0; c < gridSize; c++) {
        if (c < gridSize - 1) {
          const p1 = toXY(r, c); const p2 = toXY(r, c+1);
          ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = 'rgba(51,65,85,0.5)'; ctx.lineWidth = 1; ctx.stroke();
        }
        if (r < gridSize - 1) {
          const p1 = toXY(r, c); const p2 = toXY(r+1, c);
          ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = 'rgba(51,65,85,0.5)'; ctx.lineWidth = 1; ctx.stroke();
        }
      }
    }

    // Path
    if (result?.path?.length > 1) {
      const algoColor = ALGO_INFO[result.algorithm?.toLowerCase()] || ALGO_INFO.astar;
      ctx.beginPath();
      const first = toXY(result.path[0][0], result.path[0][1]);
      ctx.moveTo(first.x, first.y);
      for (let i = 1; i < result.path.length; i++) {
        const p = toXY(result.path[i][0], result.path[i][1]);
        ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = algoColor.color || '#ef4444';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Path nodes
      result.path.forEach(([r, c]) => {
        const { x, y } = toXY(r, c);
        ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = algoColor.color || '#ef4444'; ctx.fill();
      });
    }

    // All nodes
    for (let r = 0; r < gridSize; r++) {
      for (let c = 0; c < gridSize; c++) {
        const { x, y } = toXY(r, c);
        ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#1e293b'; ctx.fill();
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 1; ctx.stroke();
      }
    }

    // Start
    if (start) {
      const { x, y } = toXY(start[0], start[1]);
      ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#10b981'; ctx.fill();
      ctx.font = 'bold 10px Inter'; ctx.fillStyle = '#fff';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('S', x, y);
    }

    // Goal
    if (goal) {
      const { x, y } = toXY(goal[0], goal[1]);
      ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#f59e0b'; ctx.fill();
      ctx.font = 'bold 10px Inter'; ctx.fillStyle = '#000';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('G', x, y);
    }
  }, [result, start, goal, gridSize]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement);
    return () => ro.disconnect();
  }, []);

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />;
}

export default function SearchLab() {
  const [start, setStart] = useState([0, 0]);
  const [goal, setGoal] = useState([9, 9]);
  const [algo, setAlgo] = useState('astar');
  const [result, setResult] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const runAlgo = async () => {
    setLoading(true);
    try {
      const r = await api.runSearch(algo, start, goal);
      setResult(r);
    } catch(e) { console.error(e); }
    setLoading(false);
  };

  const runComparison = async () => {
    setLoading(true);
    try {
      const r = await api.compareSearch(start, goal);
      setComparison(r);
      setResult(r[algo] || Object.values(r)[0]);
    } catch(e) { console.error(e); }
    setLoading(false);
  };

  const inputStyle = { background: 'var(--bg-deep)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '5px 10px', fontSize: '0.82rem', width: '60px' };

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">🔍 Search Laboratory</div>
          <div className="page-subtitle">Compare BFS, DFS, UCS, Greedy, and A* on the city grid</div>
        </div>
      </div>

      <div className="page-body fade-in">
        <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 200px)' }}>
          {/* Controls */}
          <div style={{ width: 280, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card">
              <div className="card-title">Start Node</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input type="number" min={0} max={9} value={start[0]} onChange={e => setStart([+e.target.value, start[1]])} style={inputStyle} placeholder="Row" />
                <span style={{ color: 'var(--text-muted)' }}>×</span>
                <input type="number" min={0} max={9} value={start[1]} onChange={e => setStart([start[0], +e.target.value])} style={inputStyle} placeholder="Col" />
                <span className="badge badge-green">S</span>
              </div>
            </div>

            <div className="card">
              <div className="card-title">Goal Node</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input type="number" min={0} max={9} value={goal[0]} onChange={e => setGoal([+e.target.value, goal[1]])} style={inputStyle} placeholder="Row" />
                <span style={{ color: 'var(--text-muted)' }}>×</span>
                <input type="number" min={0} max={9} value={goal[1]} onChange={e => setGoal([goal[0], +e.target.value])} style={inputStyle} placeholder="Col" />
                <span className="badge badge-yellow">G</span>
              </div>
            </div>

            <div className="card">
              <div className="card-title">Algorithm</div>
              {ALGOS.map(a => (
                <div key={a} onClick={() => setAlgo(a)}
                  style={{ padding: '8px 10px', borderRadius: 6, cursor: 'pointer', marginBottom: 4,
                    background: algo === a ? `${ALGO_INFO[a].color}22` : 'transparent',
                    border: `1px solid ${algo === a ? ALGO_INFO[a].color : 'transparent'}`,
                    display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <span style={{ fontWeight: 600, fontSize: '0.83rem', color: ALGO_INFO[a].color }}>{ALGO_INFO[a].name}</span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{ALGO_INFO[a].desc}</span>
                </div>
              ))}
            </div>

            <button className="btn btn-primary w-full" onClick={runAlgo} disabled={loading}>
              {loading ? '⟳ Running...' : '▶ Run Search'}
            </button>
            <button className="btn btn-ghost w-full" onClick={runComparison} disabled={loading}>
              Compare All Algorithms
            </button>

            {result && (
              <div className="card">
                <div className="card-title">Result</div>
                <div style={{ fontSize: '0.78rem', lineHeight: 2 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Algorithm</span>
                    <strong style={{ color: ALGO_INFO[result.algorithm?.toLowerCase()]?.color || '#fff' }}>{result.algorithm}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Success</span>
                    <span>{result.success ? '✅ Yes' : '❌ No'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Path Length</span>
                    <strong>{result.path?.length || 0} nodes</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Total Cost</span>
                    <strong>{typeof result.cost === 'number' ? result.cost.toFixed(2) : '∞'}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Nodes Expanded</span>
                    <strong>{result.nodes_expanded}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Time</span>
                    <strong>{result.execution_time_ms?.toFixed(2)} ms</strong>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Canvas + Comparison */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', position: 'relative', overflow: 'hidden' }}>
              <SearchCanvas result={result} start={start} goal={goal} />
            </div>

            {comparison && (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Algorithm</th><th>Type</th><th>Optimal?</th><th>Path Length</th><th>Cost</th><th>Nodes Expanded</th><th>Time (ms)</th></tr>
                  </thead>
                  <tbody>
                    {Object.entries(comparison).map(([name, r]) => (
                      <tr key={name}>
                        <td><strong style={{ color: ALGO_INFO[name]?.color }}>{ALGO_INFO[name]?.name || name}</strong></td>
                        <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {['bfs','dfs'].includes(name) ? 'Uninformed' : name === 'ucs' ? 'Cost-Based' : 'Informed'}
                        </td>
                        <td>{['astar','ucs'].includes(name) ? '✅' : '—'}</td>
                        <td>{r.path?.length || 0}</td>
                        <td>{typeof r.cost === 'number' ? r.cost.toFixed(2) : '∞'}</td>
                        <td>{r.nodes_expanded}</td>
                        <td>{r.execution_time_ms?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
