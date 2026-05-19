/* =========================================================
   EchoForge — App root
   ========================================================= */

function App() {
  const [active, setActive] = useState('stt');
  const [collapsed, setCollapsed] = useState(false);
  const [vram, setVram] = useState({ used: 12.2, total: 24 });
  const [gpu] = useState({ util: 68 });
  const [status, setStatus] = useState('busy');
  const [toasts, setToasts] = useState([]);

  // ambient VRAM drift to make the meter feel alive
  useEffect(() => {
    const t = setInterval(() => {
      setVram(v => {
        const drift = (Math.random() - 0.5) * 0.6;
        const next = Math.max(8, Math.min(20, v.used + drift));
        return { ...v, used: next };
      });
    }, 1800);
    return () => clearInterval(t);
  }, []);

  const pushToast = useCallback((t) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, ...t }]);
    setTimeout(() => {
      setToasts(prev => prev.map(x => x.id === id ? { ...x, leaving: true } : x));
      setTimeout(() => setToasts(prev => prev.filter(x => x.id !== id)), 250);
    }, 3600);
  }, []);

  const modelBadges = {
    dashboard: 'whisper-large-v3',
    stt: 'whisper-large-v3',
    tts: 'XTTSv2 · Aria',
    ttt: 'llama3.1:8b',
    queue: 'mixed',
    archive: 'bge-small (idx)',
    settings: '—',
  };

  let Panel = null;
  if (active === 'dashboard') Panel = <PanelDashboard vram={vram} />;
  else if (active === 'stt') Panel = <PanelSTT pushToast={pushToast} />;
  else if (active === 'tts') Panel = <PanelTTS pushToast={pushToast} />;
  else if (active === 'ttt') Panel = <PanelTTT pushToast={pushToast} />;
  else if (active === 'queue') Panel = <PanelQueue />;
  else if (active === 'archive') Panel = <PanelArchive />;
  else if (active === 'settings') Panel = <PanelSettings />;

  return (
    <div className={`app ${collapsed ? 'collapsed' : ''}`}>
      <Sidebar
        active={active}
        onSelect={setActive}
        collapsed={collapsed}
        onCollapse={() => setCollapsed(c => !c)}
      />
      <Topbar
        active={active}
        vram={vram}
        gpu={gpu}
        status={status}
        modelBadge={modelBadges[active]}
      />
      <main className="panel" key={active}>
        {Panel}
      </main>
      <ToastStack toasts={toasts} />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
