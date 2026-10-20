import { useRef, useEffect, useCallback, useState } from 'react';
import '../styles/simulation.css';

const GRID = 10;
const COLORS = {
  NORMAL: '#10b981', MODERATE: '#f59e0b', CONGESTED: '#f97316', BLOCKED: '#ef4444',
  bg: '#0f1420', node: '#1e293b', nodeBorder: '#334155',
  patient: '#ef4444', ambulance: '#3b82f6', hospital: '#8b5cf6', route: '#06b6d4'
};

const PAD = 30;

export default function CityGrid({ simState }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const cellW = (W - PAD * 2) / (GRID - 1);
    const cellH = (H - PAD * 2) / (GRID - 1);

    const toXY = (r, c) => ({ x: PAD + c * cellW, y: PAD + r * cellH });

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, W, H);

    // Draw roads (edges)
    const roads = simState?.roads || [];
    for (const road of roads) {
      const [r1, c1] = road.from_node;
      const [r2, c2] = road.to_node;
      const p1 = toXY(r1, c1);
      const p2 = toXY(r2, c2);
      const state = road.state || 'NORMAL';
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.strokeStyle = state === 'NORMAL' ? 'rgba(30,41,59,0.8)' : COLORS[state];
      ctx.lineWidth = state === 'NORMAL' ? 1.5 : 3;
      ctx.globalAlpha = state === 'NORMAL' ? 0.4 : 0.85;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // Draw active routes
    const plans = simState?.active_plans || {};
    Object.values(plans).forEach(plan => {
      if (plan.route && plan.route.length > 1 && plan.status === 'ACTIVE') {
        ctx.beginPath();
        const first = toXY(plan.route[0][0], plan.route[0][1]);
        ctx.moveTo(first.x, first.y);
        for (let i = 1; i < plan.route.length; i++) {
          const p = toXY(plan.route[i][0], plan.route[i][1]);
          ctx.lineTo(p.x, p.y);
        }
        ctx.strokeStyle = COLORS.route;
        ctx.lineWidth = 2.5;
        ctx.setLineDash([6, 4]);
        ctx.globalAlpha = 0.7;
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      }
    });

    // Draw grid nodes
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const { x, y } = toXY(r, c);
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = COLORS.nodeBorder;
        ctx.fill();
      }
    }

    // Draw hospitals
    const hospitals = simState?.hospitals || [];
    hospitals.forEach(h => {
      const loc = h.location;
      const { x, y } = toXY(loc.row, loc.col);
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, Math.PI * 2);
      const icuFull = h.icu_available === 0;
      ctx.fillStyle = icuFull ? 'rgba(239,68,68,0.25)' : 'rgba(139,92,246,0.25)';
      ctx.fill();
      ctx.strokeStyle = icuFull ? '#ef4444' : '#8b5cf6';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.font = '12px Arial';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🏥', x, y);
      // Label
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.fillStyle = '#e2e8f0';
      ctx.fillText(h.hospital_id, x, y + 18);
    });

    // Draw patients
    const patients = simState?.patients || [];
    patients.forEach(p => {
      if (p.status === 'TREATED' || p.status === 'ARRIVED') return;
      const loc = p.location;
      const { x, y } = toXY(loc.row, loc.col);
      ctx.beginPath();
      ctx.arc(x, y, 9, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(239,68,68,0.3)';
      ctx.fill();
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.font = '9px Arial';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('👤', x, y);
      ctx.font = 'bold 8px Inter';
      ctx.fillStyle = '#f87171';
      ctx.fillText(p.patient_id, x, y + 15);
    });

    // Draw ambulances
    const ambulances = simState?.ambulances || [];
    ambulances.forEach(a => {
      const loc = a.current_location;
      if (!loc) return;
      const { x, y } = toXY(loc.row, loc.col);
      const isActive = a.status !== 'IDLE';
      ctx.beginPath();
      ctx.arc(x, y, isActive ? 10 : 7, 0, Math.PI * 2);
      ctx.fillStyle = isActive ? 'rgba(59,130,246,0.4)' : 'rgba(59,130,246,0.15)';
      ctx.fill();
      ctx.strokeStyle = isActive ? '#3b82f6' : '#1e40af';
      ctx.lineWidth = isActive ? 2.5 : 1.5;
      ctx.stroke();
      ctx.font = isActive ? '10px Arial' : '8px Arial';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🚑', x, y);
      ctx.font = 'bold 8px Inter';
      ctx.fillStyle = '#93c5fd';
      ctx.fillText(a.ambulance_id, x, y + 14);
    });

    // Legend
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'left';
    const legends = [
      { color: '#10b981', label: 'Normal Road' },
      { color: '#f59e0b', label: 'Moderate' },
      { color: '#f97316', label: 'Congested' },
      { color: '#ef4444', label: 'Blocked' },
    ];
    legends.forEach((l, i) => {
      ctx.fillStyle = l.color;
      ctx.fillRect(W - 110, 8 + i * 16, 10, 10);
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(l.label, W - 96, 16 + i * 16);
    });
  }, [simState]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      draw();
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement);
    return () => ro.disconnect();
  }, [draw]);

  useEffect(() => {
    draw();
  }, [draw]);

  return <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: '100%' }} />;
}
