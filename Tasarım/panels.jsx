/* =========================================================
   EchoForge — Other panels: Dashboard, TTS, TTT, Queue, Archive, Settings
   ========================================================= */

/* ============================================================
   Dashboard
   ============================================================ */
function PanelDashboard({ vram }) {
  const vramPct = (vram.used / vram.total) * 100;
  const ringCirc = 2 * Math.PI * 42;
  const ringOff = ringCirc * (1 - vramPct / 100);

  const ACTIVE_MODELS = [
    { name: 'whisper-large-v3', kind: 'STT', vram: '3.1 GB', state: 'loaded' },
    { name: 'XTTSv2 · multilingual', kind: 'TTS', vram: '2.4 GB', state: 'loaded' },
    { name: 'llama3.1:8b-instruct', kind: 'LLM', vram: '5.8 GB', state: 'loaded' },
    { name: 'kokoro-v0.19', kind: 'TTS', vram: '0.9 GB', state: 'idle' },
  ];

  const ACTIVITY = [
    { ico: 'mic', text: <>Transcribed <span className="a-em">kickoff_meeting.wav</span> — 12 segments</>, time: '2 min ago' },
    { ico: 'speaker', text: <>Generated TTS for <span className="a-em">welcome_narration.txt</span></>, time: '14 min ago' },
    { ico: 'chat', text: <>LLM session with <span className="a-em">llama3.1:8b</span> — 4.2k tokens</>, time: '38 min ago' },
    { ico: 'pipe', text: <>STS pipeline ran <span className="a-em">3 files</span> end-to-end</>, time: '1 hr ago' },
    { ico: 'mic', text: <>Transcribed <span className="a-em">interview_03.mp3</span> — 88 segments</>, time: '2 hr ago' },
    { ico: 'archive', text: <>Indexed <span className="a-em">7 transcripts</span> in archive</>, time: '3 hr ago' },
  ];

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Dashboard</h1>
          <p className="panel-sub">System health · active models · recent pipeline activity</p>
        </div>
        <div className="panel-actions">
          <button className="btn ghost sm"><I.refresh /> Refresh</button>
          <button className="btn primary"><I.zap /> Run pipeline</button>
        </div>
      </div>

      <div className="dash-grid">
        {/* Metrics row */}
        <div className="card card-pad col-3 metric">
          <span className="m-label">Files transcribed</span>
          <span className="m-value">1,284</span>
          <span className="m-sub"><span className="m-trend up">+18 today</span> · 38 this week</span>
        </div>
        <div className="card card-pad col-3 metric">
          <span className="m-label">TTS minutes</span>
          <span className="m-value">421<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>m</span></span>
          <span className="m-sub"><span className="m-trend up">+12.4m today</span></span>
        </div>
        <div className="card card-pad col-3 metric">
          <span className="m-label">LLM tokens</span>
          <span className="m-value">2.41<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>M</span></span>
          <span className="m-sub">in/out · all local</span>
        </div>
        <div className="card card-pad col-3 metric">
          <span className="m-label">Avg STT WER</span>
          <span className="m-value">4.2<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>%</span></span>
          <span className="m-sub"><span className="m-trend down">−0.6%</span> · large-v3</span>
        </div>

        {/* GPU card */}
        <div className="card card-pad col-7">
          <div className="card-title">GPU · RTX 4090 · 24 GB</div>
          <div className="gpu-card">
            <div className="gpu-ring">
              <svg viewBox="0 0 100 100">
                <defs>
                  <linearGradient id="gpuGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#7c3aed"/>
                    <stop offset="100%" stopColor="#06b6d4"/>
                  </linearGradient>
                </defs>
                <circle className="gp-bg" cx="50" cy="50" r="42" fill="none" strokeWidth="8"/>
                <circle className="gp-fg" cx="50" cy="50" r="42" fill="none" strokeWidth="8"
                  strokeDasharray={ringCirc} strokeDashoffset={ringOff} />
              </svg>
              <div className="gp-text">{vramPct.toFixed(0)}%</div>
            </div>
            <div className="gpu-stats">
              <div className="gs-row"><div className="l">VRAM Used</div><div className="v">{vram.used.toFixed(1)} GB</div></div>
              <div className="gs-row"><div className="l">VRAM Free</div><div className="v">{(vram.total - vram.used).toFixed(1)} GB</div></div>
              <div className="gs-row"><div className="l">GPU Util</div><div className="v">68%</div></div>
              <div className="gs-row"><div className="l">Temp</div><div className="v">62°C</div></div>
              <div className="gs-row"><div className="l">Power</div><div className="v">284 W</div></div>
              <div className="gs-row"><div className="l">CUDA</div><div className="v">12.4</div></div>
            </div>
          </div>
        </div>

        {/* Active models */}
        <div className="card col-5">
          <div className="card-pad" style={{ paddingBottom: 0 }}>
            <div className="card-title">Active models</div>
          </div>
          <div>
            {ACTIVE_MODELS.map(m => (
              <div key={m.name} className="model-row">
                <div className="m-ico">
                  {m.kind === 'STT' ? <I.mic /> : m.kind === 'TTS' ? <I.speaker /> : <I.brain />}
                </div>
                <div>
                  <div className="m-name mono">{m.name}</div>
                  <div className="m-meta">{m.kind} · {m.state === 'loaded' ? <span style={{ color: 'var(--green)' }}>loaded</span> : <span style={{ color: 'var(--text-4)' }}>idle</span>}</div>
                </div>
                <div className="m-vram">{m.vram}</div>
                <button className="icon-btn"><I.more /></button>
              </div>
            ))}
          </div>
        </div>

        {/* Recent activity */}
        <div className="card col-7">
          <div className="card-pad" style={{ paddingBottom: 0, display: 'flex', justifyContent: 'space-between' }}>
            <div className="card-title">Recent activity</div>
            <a style={{ fontSize: 11, color: 'var(--text-3)', cursor: 'pointer' }}>View all →</a>
          </div>
          <div>
            {ACTIVITY.map((a, i) => (
              <div key={i} className="activity-row">
                <div className="a-icon">
                  {a.ico === 'mic' ? <I.mic /> :
                   a.ico === 'speaker' ? <I.speaker /> :
                   a.ico === 'chat' ? <I.chat /> :
                   a.ico === 'pipe' ? <I.pipe /> :
                   <I.archive />}
                </div>
                <div className="a-text">{a.text}</div>
                <span className="badge done"><span className="dot" />ok</span>
                <span className="a-time">{a.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick start */}
        <div className="card card-pad col-5 glow" style={{
          background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, var(--surface) 60%)',
        }}>
          <div className="card-title">Quick start</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {[
              { ico: I.mic, label: 'Transcribe file', sub: 'Whisper · local' },
              { ico: I.speaker, label: 'Generate speech', sub: 'XTTSv2 · clone' },
              { ico: I.pipe, label: 'STS pipeline', sub: 'STT → TTS auto' },
              { ico: I.chat, label: 'Chat with LLM', sub: 'Ollama · stream' },
            ].map(qs => (
              <div key={qs.label} className="card" style={{ padding: 12, cursor: 'pointer', background: 'var(--surface-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <qs.ico style={{ width: 14, height: 14, color: 'var(--violet-2)' }} />
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{qs.label}</div>
                </div>
                <div style={{ fontSize: 10.5, color: 'var(--text-3)', marginTop: 4 }}>{qs.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   TTS Studio
   ============================================================ */
function PanelTTS({ pushToast }) {
  const [model, setModel] = useState('xtts');
  const [voice, setVoice] = useState('aria');
  const [lang, setLang] = useState('en-US');
  const [text, setText] = useState('In the silent observatory, the constellations whispered secrets that only the patient could hear. She tuned her instruments, and waited for the night to speak.');
  const [generated, setGenerated] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(2.4);

  const VOICES = [
    { id: 'aria', name: 'Aria', meta: 'Female · warm · en-US' },
    { id: 'kai', name: 'Kai', meta: 'Male · neutral · en-US' },
    { id: 'mei', name: 'Mei', meta: 'Female · bright · en-GB' },
    { id: 'noor', name: 'Noor', meta: 'Cloned · 12s ref · custom' },
  ];

  const dummyFile = { name: 'output_aria_xtts.wav', duration: 11.6, sampleRate: '24 kHz · mono · float' };

  const onGenerate = () => {
    pushToast({ kind: 'success', title: 'Generating speech', msg: 'XTTSv2 · 11.6s estimated · queued' });
    setGenerated(true);
  };

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">TTS Studio</h1>
          <p className="panel-sub">Generate speech from text · voice cloning · multi-language</p>
        </div>
      </div>

      <div className="tts-grid">
        {/* Left: text + output */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card card-pad">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <label className="field-label" style={{ margin: 0 }}>Text input</label>
              <span style={{ fontSize: 11, color: 'var(--text-3)' }} className="mono">{text.length} chars · ~{(text.length / 14).toFixed(1)}s</span>
            </div>
            <textarea
              className="textarea"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Type or paste text to synthesize…"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14 }}>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn ghost sm"><I.copy /> Paste</button>
                <button className="btn ghost sm"><I.file /> Load .txt</button>
                <button className="btn ghost sm"><I.brain /> Polish with LLM</button>
              </div>
              <button className="btn primary lg" onClick={onGenerate}>
                <I.zap /> Generate
              </button>
            </div>
          </div>

          {generated && (
            <div className="card">
              <div className="transcript-head">
                <div>
                  <div className="t-title">Output</div>
                  <div className="t-sub">{dummyFile.name} · {dummyFile.sampleRate}</div>
                </div>
                <div className="transcript-head-actions">
                  <span className="badge done"><span className="dot" />ready · 384ms</span>
                  <button className="btn ghost sm"><I.download /> WAV</button>
                  <button className="btn ghost sm"><I.download /> MP3</button>
                </div>
              </div>
              <div style={{ padding: 16 }}>
                <AudioPlayer
                  file={dummyFile}
                  playing={playing}
                  setPlaying={setPlaying}
                  currentTime={currentTime}
                  setCurrentTime={setCurrentTime}
                />
              </div>
            </div>
          )}
        </div>

        {/* Right: model / voice controls */}
        <div className="tts-controls">
          <div className="card card-pad">
            <label className="field-label">Engine</label>
            <div className="model-tiles">
              {[
                { id: 'xtts', name: 'XTTSv2', meta: 'Local · clone' },
                { id: 'kokoro', name: 'Kokoro', meta: 'Local · fast' },
                { id: 'hume', name: 'Hume TADA', meta: 'Cloud · emotive' },
              ].map(m => (
                <div key={m.id} className={`model-tile ${model === m.id ? 'active' : ''}`} onClick={() => setModel(m.id)}>
                  <div className="mt-name">{m.name}</div>
                  <div className="mt-meta">{m.meta}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="card card-pad">
            <label className="field-label">Language</label>
            <select className="select" value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
              <option value="es-ES">Spanish (Spain)</option>
              <option value="fr-FR">French</option>
              <option value="de-DE">German</option>
              <option value="ja-JP">Japanese</option>
              <option value="zh-CN">Chinese (Mandarin)</option>
            </select>

            <label className="field-label" style={{ marginTop: 14 }}>Voice</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {VOICES.map(v => (
                <div key={v.id} className={`voice-card ${voice === v.id ? 'active' : ''}`} onClick={() => setVoice(v.id)}>
                  <div className="va" style={
                    v.id === 'aria' ? { background: 'linear-gradient(135deg,#7c3aed,#22d3ee)' } :
                    v.id === 'kai' ? { background: 'linear-gradient(135deg,#06b6d4,#1e40af)' } :
                    v.id === 'mei' ? { background: 'linear-gradient(135deg,#ec4899,#f59e0b)' } :
                                     { background: 'linear-gradient(135deg,#22c55e,#7c3aed)' }
                  } />
                  <div style={{ flex: 1 }}>
                    <div className="v-name">{v.name}</div>
                    <div className="v-meta">{v.meta}</div>
                  </div>
                  {voice === v.id && <I.check style={{ width: 14, height: 14, color: 'var(--violet-2)' }} />}
                </div>
              ))}
            </div>
          </div>

          <div className="card card-pad">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <label className="field-label" style={{ margin: 0 }}>Reference voice</label>
              <span className="badge"><span className="dot" />6s clip ready</span>
            </div>
            <div style={{
              border: '1.5px dashed var(--border-2)',
              borderRadius: 8,
              padding: 14,
              marginTop: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              cursor: 'pointer',
            }}>
              <I.upload style={{ width: 16, height: 16, color: 'var(--text-3)' }} />
              <div style={{ flex: 1, fontSize: 12 }}>
                <div style={{ fontWeight: 500 }}>noor_reference.wav</div>
                <div style={{ color: 'var(--text-3)', fontSize: 11 }}>6.2s · clean · ready for clone</div>
              </div>
              <button className="btn ghost sm"><I.play style={{ width: 10, height: 10 }} /></button>
            </div>
          </div>

          <div className="card card-pad">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <Slider label="Speed" value={1.0} min={0.5} max={2.0} step={0.05} suffix="×" />
              <Slider label="Temperature" value={0.7} min={0} max={1} step={0.05} />
              <Slider label="Stability" value={0.85} min={0} max={1} step={0.05} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Slider({ label, value, min, max, step, suffix }) {
  const [v, setV] = useState(value);
  const pct = ((v - min) / (max - min)) * 100;
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 12, color: 'var(--text-2)' }}>{label}</span>
        <span style={{ fontSize: 12, color: 'var(--text)', fontVariantNumeric: 'tabular-nums' }} className="mono">{v.toFixed(2)}{suffix || ''}</span>
      </div>
      <div style={{ position: 'relative', height: 4, background: 'var(--surface-3)', borderRadius: 999 }}>
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${pct}%`, background: 'var(--violet)', borderRadius: 999 }} />
        <input type="range" min={min} max={max} step={step} value={v} onChange={e => setV(parseFloat(e.target.value))}
          style={{ position: 'absolute', inset: 0, opacity: 0, width: '100%', cursor: 'pointer' }} />
        <div style={{ position: 'absolute', left: `${pct}%`, top: '50%', width: 12, height: 12, borderRadius: '50%', background: 'var(--violet-2)', transform: 'translate(-50%, -50%)', boxShadow: '0 0 0 3px var(--bg), 0 0 10px var(--violet-glow)' }} />
      </div>
    </div>
  );
}

/* ============================================================
   TTT Chat
   ============================================================ */
function PanelTTT({ pushToast }) {
  const [backend, setBackend] = useState('ollama');
  const [translate, setTranslate] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'user', text: 'Summarize the architecture decisions for EchoForge v0.7 in 2 bullet points.' },
    { role: 'assistant', text: '• Whisper STT moves from CPU to local GPU node — roughly 6× faster, with the medium model loaded by default and large-v3 selectable from Settings for higher accuracy.\n• STS pipeline streams sentence-by-sentence: each segment closes on the Whisper output and is dispatched to XTTSv2 (local) or Hume TADA (cloud, throttled) without waiting for the full transcript.' },
    { role: 'user', text: 'How does the diarization layer fit in?' },
    { role: 'assistant', text: 'Diarization runs as a parallel pass on the same audio buffer using pyannote 3.1\'s diarization-3.1 pipeline. Speaker labels are joined to Whisper segments by overlap — when the toggle is off, the labels are still computed in the background but suppressed from the UI, so flipping the switch is instant with no re-run.' },
  ]);
  const msgsRef = useRef(null);

  useEffect(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
  }, [messages]);

  const send = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', text: input }]);
    setInput('');
    setTimeout(() => {
      setMessages(m => [...m, { role: 'assistant', text: 'Streaming response from ' + (backend === 'ollama' ? 'llama3.1:8b-instruct' : 'gemini-1.5-pro') + '… [demo placeholder]' }]);
    }, 800);
  };

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">TTT Chat</h1>
          <p className="panel-sub">Text-to-text · local LLM (Ollama) or cloud (Gemini) · streaming</p>
        </div>
        <div className="panel-actions">
          <Segmented
            options={[
              { value: 'ollama', label: 'Ollama', icon: I.cpu },
              { value: 'gemini', label: 'Gemini', icon: I.globe },
            ]}
            value={backend}
            onChange={setBackend}
          />
        </div>
      </div>

      <div className="card card-pad" style={{ marginBottom: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>MODEL</span>
            <span className="mono" style={{ fontSize: 12 }}>{backend === 'ollama' ? 'llama3.1:8b-instruct-q4' : 'gemini-1.5-pro'}</span>
          </div>
          <div style={{ width: 1, height: 16, background: 'var(--border)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>CONTEXT</span>
            <span className="mono" style={{ fontSize: 12 }}>2.4k / 32k</span>
          </div>
        </div>
        <Switch on={translate} onChange={setTranslate} label="Translation mode" />
      </div>

      <div className="chat">
        <div className="chat-msgs" ref={msgsRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="msg-avatar">{m.role === 'user' ? 'SO' : <I.brain style={{ width: 14, height: 14 }} />}</div>
              <div>
                <div className="msg-bubble">{m.text}</div>
                {m.role === 'assistant' && (
                  <div className="msg-actions">
                    <button className="msg-action" onClick={() => pushToast({ kind: 'success', title: 'Sent to TTS Studio' })}>
                      <I.speaker /> Send to TTS
                    </button>
                    <button className="msg-action"><I.copy /> Copy</button>
                    <button className="msg-action"><I.refresh /> Regenerate</button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="chat-input-wrap">
          <textarea
            className="chat-input"
            placeholder={`Message ${backend === 'ollama' ? 'llama3.1' : 'Gemini'}…`}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
          />
          <button className="chat-send" onClick={send}><I.send /></button>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   Queue
   ============================================================ */
const QUEUE_ROWS = [
  { name: 'podcast_ep_042.mp3', kind: 'STT', size: '38.4 MB', model: 'whisper-large-v3', state: 'processing', progress: 0.62, time: '2m 14s' },
  { name: 'narration_intro.txt', kind: 'TTS', size: '1.2 KB', model: 'XTTSv2 · Aria', state: 'processing', progress: 0.18, time: '24s' },
  { name: 'standup_2026-05-19.wav', kind: 'STT+SUM', size: '22.1 MB', model: 'large-v3 + llama3.1', state: 'waiting', progress: 0, time: '—' },
  { name: 'product_demo_es.mp4', kind: 'STT', size: '142.0 MB', model: 'whisper-medium', state: 'waiting', progress: 0, time: '—' },
  { name: 'interview_thompson.flac', kind: 'STS', size: '94.8 MB', model: 'large-v3 → Kokoro', state: 'done', progress: 1, time: '6m 02s' },
  { name: 'voiceover_chapter_3.txt', kind: 'TTS', size: '8.4 KB', model: 'XTTSv2 · Kai', state: 'done', progress: 1, time: '1m 11s' },
  { name: 'corrupt_audio_test.wav', kind: 'STT', size: '0.4 MB', model: 'whisper-base', state: 'error', progress: 0.4, time: 'failed' },
];

function PanelQueue() {
  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Job Queue</h1>
          <p className="panel-sub">7 jobs · 2 processing · 2 waiting · 2 done · 1 error</p>
        </div>
        <div className="panel-actions">
          <button className="btn ghost sm"><I.trash /> Clear done</button>
          <button className="btn ghost"><I.x /> Cancel all</button>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: '34%' }}>File</th>
              <th>Pipeline</th>
              <th>Model</th>
              <th style={{ width: '22%' }}>Progress</th>
              <th>Status</th>
              <th>Time</th>
              <th style={{ width: 50 }}></th>
            </tr>
          </thead>
          <tbody>
            {QUEUE_ROWS.map((r, i) => (
              <tr key={i}>
                <td>
                  <div className="q-file">
                    <div className="q-file-ico">
                      {r.kind.includes('TTS') && !r.kind.includes('STT') ? <I.speaker /> :
                       r.kind === 'STS' ? <I.pipe /> :
                       <I.audio />}
                    </div>
                    <div>
                      <div className="q-file-name">{r.name}</div>
                      <div className="q-file-sub">{r.size}</div>
                    </div>
                  </div>
                </td>
                <td><span className="badge" style={{
                  background: r.kind === 'STS' ? 'rgba(124,58,237,0.1)' : r.kind === 'TTS' ? 'rgba(6,182,212,0.1)' : 'var(--surface-2)',
                  color: r.kind === 'STS' ? 'var(--violet-2)' : r.kind === 'TTS' ? 'var(--cyan-2)' : 'var(--text-2)',
                  borderColor: r.kind === 'STS' ? 'rgba(124,58,237,0.25)' : r.kind === 'TTS' ? 'rgba(6,182,212,0.25)' : 'var(--border)'
                }}>{r.kind}</span></td>
                <td><span className="mono" style={{ fontSize: 12, color: 'var(--text-2)' }}>{r.model}</span></td>
                <td>
                  <div className="q-progress">
                    <div className={`q-progress-fill ${r.state === 'done' ? 'done' : r.state === 'error' ? 'error' : r.state === 'waiting' ? 'waiting' : ''}`}
                      style={{ width: `${(r.progress || 0.02) * 100}%` }} />
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4, fontVariantNumeric: 'tabular-nums' }}>
                    {r.state === 'waiting' ? 'Queued' : `${Math.round(r.progress * 100)}%`}
                  </div>
                </td>
                <td><span className={`badge ${r.state}`}><span className="dot" />{r.state}</span></td>
                <td><span className="mono" style={{ fontSize: 12, color: 'var(--text-3)' }}>{r.time}</span></td>
                <td>
                  <button className="icon-btn" style={{ width: 26, height: 26 }} title={r.state === 'done' ? 'Open' : 'Cancel'}>
                    {r.state === 'done' ? <I.arrowRight /> : <I.x />}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ============================================================
   Archive
   ============================================================ */
const ARCHIVE_DOCS = [
  { title: 'Kickoff meeting — v0.7 release planning', date: 'May 18, 2026', dur: '3:17', speakers: 3, words: 412, snippet: 'The big shift is moving Whisper inference off CPU and onto the local GPU node — should be roughly 6x faster. Both. The Settings panel exposes the model selector.' },
  { title: 'Interview · Dr. Thompson — voice cloning ethics', date: 'May 15, 2026', dur: '42:08', speakers: 2, words: 5841, snippet: 'When you train on someone\'s six seconds of audio, you\'re not just capturing their timbre — you\'re capturing prosody, emotional baseline, the small breath patterns. Consent has to scale with that.' },
  { title: 'Podcast ep 042 — local-first AI', date: 'May 12, 2026', dur: '1:18:24', speakers: 4, words: 14820, snippet: 'I think the future of voice models isn\'t in the cloud at all — it\'s on the device, with the user owning the weights. That\'s why we shipped Kokoro alongside XTTS.' },
  { title: 'Product demo — Spanish narration draft', date: 'May 10, 2026', dur: '8:42', speakers: 1, words: 1208, snippet: 'Bienvenidos a EchoForge, el estudio de voz local que pone los modelos en tus manos. Hoy vamos a recorrer las cuatro tuberías principales…' },
  { title: 'Standup · 2026-05-19', date: 'May 19, 2026', dur: '14:22', speakers: 5, words: 2104, snippet: 'Quick one from me — diarization toggle is wired up, just need to land the styling pass on the segment column collapse animation.' },
];

function PanelArchive() {
  const [q, setQ] = useState('whisper');
  const [openIdx, setOpenIdx] = useState(null);
  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Archive</h1>
          <p className="panel-sub">{ARCHIVE_DOCS.length} transcripts · indexed locally · semantic search via bge-small</p>
        </div>
      </div>

      <div className="search-row">
        <div className="search-input">
          <span className="search-ico"><I.search /></span>
          <input className="input" placeholder="Keyword search…" value={q} onChange={e => setQ(e.target.value)} />
          <span className="search-kbd">⌘K</span>
        </div>
        <div className="search-input">
          <span className="search-ico"><I.brain /></span>
          <input className="input" placeholder="Semantic search — describe what you remember…" />
        </div>
        <button className="btn ghost"><I.refresh /> Reindex</button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {ARCHIVE_DOCS.map((d, i) => {
          const open = openIdx === i;
          const snippet = q ? d.snippet.replace(new RegExp(`(${q})`, 'gi'), '<mark>$1</mark>') : d.snippet;
          return (
            <div key={i} className="card archive-card glow" onClick={() => setOpenIdx(open ? null : i)}>
              <div className="arc-head">
                <div>
                  <div className="arc-title">{d.title}</div>
                  <div className="arc-meta">
                    <span>{d.date}</span>
                    <span>·</span>
                    <span>{d.dur}</span>
                    <span>·</span>
                    <span><I.users style={{ width: 11, height: 11, verticalAlign: -2, marginRight: 3 }} />{d.speakers}</span>
                    <span>·</span>
                    <span>{d.words.toLocaleString()} words</span>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <span className="badge done"><span className="dot" />indexed</span>
                  <button className="icon-btn" style={{ width: 26, height: 26 }} onClick={e => e.stopPropagation()}><I.download /></button>
                </div>
              </div>
              <div className={`arc-snippet ${open ? 'open' : ''}`} dangerouslySetInnerHTML={{ __html: snippet }} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ============================================================
   Settings
   ============================================================ */
const SETTINGS_SECTIONS = [
  { id: 'stt', label: 'STT (Whisper)' },
  { id: 'tts', label: 'TTS Models' },
  { id: 'llm', label: 'LLM' },
  { id: 'general', label: 'General' },
];

function PanelSettings() {
  const [section, setSection] = useState('stt');
  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Settings</h1>
          <p className="panel-sub">Local configuration · changes save to <span className="mono" style={{ color: 'var(--text-2)' }}>~/.echoforge/config.toml</span></p>
        </div>
      </div>

      <div className="settings-grid">
        <div className="settings-nav">
          {SETTINGS_SECTIONS.map(s => (
            <a key={s.id} className={section === s.id ? 'active' : ''} onClick={() => setSection(s.id)}>{s.label}</a>
          ))}
        </div>
        <div>
          {section === 'stt' && (
            <div className="card card-pad">
              <SettingRow label="Whisper model" sub="Default model loaded on startup. Larger = more accurate, more VRAM.">
                <select className="select" defaultValue="large-v3" style={{ width: 240 }}>
                  <option value="tiny">tiny · 39M · 0.4 GB</option>
                  <option value="base">base · 74M · 0.6 GB</option>
                  <option value="small">small · 244M · 1.2 GB</option>
                  <option value="medium">medium · 769M · 2.4 GB</option>
                  <option value="large-v3">large-v3 · 1.55B · 3.1 GB</option>
                </select>
              </SettingRow>
              <SettingRow label="Silence threshold (dBFS)" sub="Below this, audio is treated as silence and skipped.">
                <input className="input" defaultValue="-40" style={{ width: 120, textAlign: 'right' }} />
              </SettingRow>
              <SettingRow label="Chunk size (seconds)" sub="Length of each Whisper inference chunk. 30s is the model default.">
                <input className="input" defaultValue="30" style={{ width: 120, textAlign: 'right' }} />
              </SettingRow>
              <SettingRow label="VAD filter" sub="Apply Silero VAD before transcription. Improves long-file accuracy.">
                <SwitchRow defaultOn />
              </SettingRow>
              <SettingRow label="Speaker diarization (default)" sub="Run pyannote 3.1 diarization on every transcript.">
                <SwitchRow defaultOn />
              </SettingRow>
            </div>
          )}
          {section === 'tts' && (
            <div className="card card-pad">
              <SettingRow label="Model directory" sub="Where local TTS model weights are stored.">
                <input className="input mono" defaultValue="~/EchoForge/models/tts" />
              </SettingRow>
              <SettingRow label="HuggingFace cache" sub="Shared HF cache for downloaded artifacts.">
                <input className="input mono" defaultValue="~/.cache/huggingface" />
              </SettingRow>
              <SettingRow label="Default TTS model" sub="Used when not specified per-job.">
                <select className="select" defaultValue="xtts" style={{ width: 200 }}>
                  <option value="xtts">XTTSv2 · multilingual</option>
                  <option value="kokoro">Kokoro v0.19</option>
                  <option value="hume">Hume TADA (cloud)</option>
                </select>
              </SettingRow>
              <SettingRow label="Output sample rate" sub="Forced resample of all TTS outputs.">
                <select className="select" defaultValue="24000" style={{ width: 140 }}>
                  <option value="16000">16,000 Hz</option>
                  <option value="22050">22,050 Hz</option>
                  <option value="24000">24,000 Hz</option>
                  <option value="44100">44,100 Hz</option>
                  <option value="48000">48,000 Hz</option>
                </select>
              </SettingRow>
            </div>
          )}
          {section === 'llm' && (
            <div className="card card-pad">
              <SettingRow label="Ollama base URL" sub="Local Ollama daemon. Default port 11434.">
                <input className="input mono" defaultValue="http://127.0.0.1:11434" />
              </SettingRow>
              <SettingRow label="Default Ollama model" sub="Pulled from Ollama on first use if missing.">
                <select className="select mono" defaultValue="llama3.1:8b-instruct-q4" style={{ width: 240 }}>
                  <option>llama3.1:8b-instruct-q4</option>
                  <option>llama3.1:70b-instruct-q4</option>
                  <option>qwen2.5:7b-instruct</option>
                  <option>mistral-nemo:12b-instruct</option>
                </select>
              </SettingRow>
              <SettingRow label="Gemini API key" sub="Stored in OS keychain. Never logged.">
                <input className="input mono" type="password" defaultValue="••••••••••••••••" style={{ width: 240 }} />
              </SettingRow>
              <SettingRow label="Streaming" sub="Stream tokens in TTT Chat panel.">
                <SwitchRow defaultOn />
              </SettingRow>
            </div>
          )}
          {section === 'general' && (
            <div className="card card-pad">
              <SettingRow label="Output directory" sub="Where transcripts, exports, and TTS outputs go.">
                <input className="input mono" defaultValue="~/EchoForge/output" />
              </SettingRow>
              <SettingRow label="Last mode" sub="Panel restored on app launch.">
                <select className="select" defaultValue="stt" style={{ width: 180 }}>
                  <option value="dashboard">Dashboard</option>
                  <option value="stt">STT</option>
                  <option value="tts">TTS Studio</option>
                  <option value="ttt">TTT Chat</option>
                  <option value="queue">Queue</option>
                </select>
              </SettingRow>
              <SettingRow label="Telemetry" sub="Anonymous crash reports only. Off by default.">
                <SwitchRow defaultOn={false} />
              </SettingRow>
              <SettingRow label="Theme" sub="Always dark — EchoForge is built for it.">
                <div className="segmented">
                  <div className="seg-thumb" style={{ left: 3, width: 76 }} />
                  <button className="active">Dark</button>
                  <button disabled style={{ opacity: 0.4 }}>Light</button>
                </div>
              </SettingRow>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SettingRow({ label, sub, children }) {
  return (
    <div className="setting-row">
      <div>
        <div className="sr-label">{label}</div>
        <div className="sr-sub">{sub}</div>
      </div>
      <div className="sr-control">{children}</div>
    </div>
  );
}
function SwitchRow({ defaultOn }) {
  const [on, setOn] = useState(defaultOn);
  return <Switch on={on} onChange={setOn} />;
}

Object.assign(window, {
  PanelDashboard, PanelTTS, PanelTTT, PanelQueue, PanelArchive, PanelSettings,
  AudioPlayer, PlayerViz, Slider,
});
