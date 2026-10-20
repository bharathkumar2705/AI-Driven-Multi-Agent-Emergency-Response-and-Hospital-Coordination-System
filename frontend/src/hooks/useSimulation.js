import { useState, useEffect, useCallback, useRef } from 'react';
import { wsService } from '../services/websocket';
import { api } from '../services/api';

export function useSimulation() {
  const [simState, setSimState] = useState(null);
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState('IDLE');
  const msgRef = useRef([]);

  useEffect(() => {
    wsService.connect();

    const unsubState = wsService.on('SIM_TICK', (data) => {
      setSimState(data);
      setStatus(data?.status || 'IDLE');
      if (data?.messages?.length) {
        msgRef.current = [...data.messages, ...msgRef.current].slice(0, 200);
        setMessages([...msgRef.current]);
      }
    });

    const unsubInit = wsService.on('INITIAL_STATE', (data) => {
      setSimState(data);
      setStatus(data?.status || 'IDLE');
    });

    const unsubConn = wsService.on('connected', () => setConnected(true));
    const unsubDisc = wsService.on('disconnected', () => setConnected(false));

    return () => {
      unsubState(); unsubInit(); unsubConn(); unsubDisc();
    };
  }, []);

  const start = useCallback(async (scenario = 'scenario_1') => {
    try { await api.startSim(scenario); } catch (e) { console.error(e); }
  }, []);

  const pause = useCallback(async () => {
    try { await api.pauseSim(); } catch (e) { console.error(e); }
  }, []);

  const resume = useCallback(async () => {
    try { await api.resumeSim(); } catch (e) { console.error(e); }
  }, []);

  const reset = useCallback(async (scenario = 'scenario_1') => {
    msgRef.current = [];
    setMessages([]);
    try { await api.resetSim(scenario); } catch (e) { console.error(e); }
  }, []);

  const injectEvent = useCallback(async (eventType, data = {}) => {
    try { return await api.injectEvent(eventType, data); } catch (e) { console.error(e); }
  }, []);

  return { simState, messages, connected, status, start, pause, resume, reset, injectEvent };
}
