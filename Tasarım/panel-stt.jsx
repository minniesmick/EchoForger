/* =========================================================
   EchoForge — STT Panel (default view)
   ========================================================= */

const STT_SAMPLE_FILE = {
  name: 'kickoff_meeting_2026-05-18.wav',
  size: '14.8 MB',
  duration: 197.4, // seconds (3:17)
  sampleRate: '48 kHz · stereo · 16-bit',
};

const STT_SEGMENTS = [
  { t: 0.0,   end: 4.2,  spk: 1, conf: 0.98, text: 'Alright everyone, thanks for joining. Let me share the plan for the v0.7 release real quick.' },
  { t: 4.6,   end: 8.9,  spk: 1, conf: 0.96, text: 'The big shift is moving Whisper inference off CPU and onto the local GPU node — should be roughly 6x faster.' },
  { t: 9.3,   end: 13.1, spk: 2, conf: 0.94, text: 'Nice. Are we still pinning to the medium model, or are we letting users pick large-v3?' },
  { t: 13.5,  end: 18.0, spk: 1, conf: 0.97, text: 'Both. The Settings panel exposes the model selector. Default stays medium for VRAM headroom.' },
  { t: 18.4,  end: 23.2, spk: 3, conf: 0.91, text: 'Question — when STS mode is on, does the pipeline buffer the whole transcript before passing to TTS, or stream sentence-by-sentence?' },
  { t: 23.6,  end: 28.8, spk: 1, conf: 0.95, text: 'Sentence-by-sentence. We segment on the Whisper output and dispatch to XTTS as each segment closes.' },
  { t: 29.2,  end: 33.4, spk: 2, conf: 0.89, text: 'Got it. And the Hume TADA path — that\'s still queued behind the API throttle, right?' },
  { t: 33.8,  end: 38.6, spk: 1, conf: 0.93, text: 'Correct. Hume goes through the cloud throttle. XTTS and Kokoro are local, no rate limit.' },
  { t: 39.0,  end: 44.5, spk: 3, conf: 0.96, text: 'Last thing — the speaker diarization toggle. Are we using pyannote, or did we end up on Sherpa?' },
  { t: 44.9,  end: 49.7, spk: 1, conf: 0.62, text: 'Pyannote 3.1 with the diarization-3.1 pipeline. Sherpa was slower on long files.' },
  { t: 50.1,  end: 54.4, spk: 2, conf: 0.94, text: 'Cool. I\'ll start on the Settings UI tomorrow. Anything else for me?' },
  { t: 54.8,  end: 58.2, spk: 1, conf: 0.97, text: 'Just keep the Geist Mono in the transcript panel — it reads way better for long sessions.' },
];

const SPK_LABELS = { 1: 'Speaker 1', 2: 'Speaker 2', 3: 'Speaker 3' };

function fmt(t) {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
function fmtMs(t) {
  const m = Math.floor(t / 60);
  const s = (t % 60).toFixed(1);
  return `${m.toString().padStart(2, '0')}:${s.padStart(4, '0')}`;
}

/* ---------- Live waveform (recording indicator) ---------- */
function LiveWaveform({ active }) {
  const BAR_COUNT = 48;
  const [bars, setBars] = useState(() => Array(BAR_COUNT).fill(4));
  useEffect(() => {
    if (!active) {
      setBars(Array(BAR_COUNT).fill(4));
      return;
    }
    let raf;
    let phase = 0;
    const tick = () => {
      phase += 0.18;
      setBars(prev => prev.map((_, i) => {
        const base = Math.sin(phase + i * 0.32) * 0.5 + 0.5;
        const noise = Math.random() * 0.7;
        return Math.max(4, base * 24 + noise * 18);
      }));
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active]);
  return (
    <div className="live-waveform">
      {bars.map((h, i) => (
        <div key={i} className="lw-bar" style={{ height: `${h}px`, opacity: active ? 1 : 0.3 }} />
      ))}
    </div>
  );
}

/* ---------- Frequency visualizer (audio player) ---------- */
function PlayerViz({ playing }) {
  const BAR_COUNT = 56;
  const [bars, setBars] = useState(() => Array(BAR_COUNT).fill(4));
  useEffect(() => {
    if (!playing) return;
    let raf;
    let phase = 0;
    const tick = () => {
      phase += 0.22;
      // Simulate frequency-domain shape: low-bin heavy with mid/high accents
      setBars(prev => prev.map((_, i) => {
        const n = i / BAR_COUNT;
        const env = Math.exp(-n * 1.3) * 0.9 + 0.1;
        const wob = (Math.sin(phase * (1 + n * 0.3) + i * 0.4) * 0.5 + 0.5);
        const noise = Math.random();
        const v = env * (0.45 + wob * 0.35 + noise * 0.25);
        return Math.max(3, v * 34);
      }));
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing]);
  return (
    <div className={`player-viz ${playing ? 'playing' : 'paused'}`}>
      {bars.map((h, i) => (
        <div key={i} className="vb" style={{ height: `${h}px` }} />
      ))}
    </div>
  );
}

/* ---------- Audio player bar ---------- */
function AudioPlayer({ file, playing, setPlaying, currentTime, setCurrentTime }) {
  const seekRef = useRef(null);
  const dragging = useRef(false);

  useEffect(() => {
    if (!playing) return;
    let raf;
    let last = performance.now();
    const tick = (now) => {
      const dt = (now - last) / 1000;
      last = now;
      setCurrentTime(prev => {
        const next = prev + dt;
        if (next >= file.duration) { setPlaying(false); return file.duration; }
        return next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing]);

  const handleSeek = (e) => {
    const r = seekRef.current.getBoundingClientRect();
    const x = e.clientX - r.left;
    const pct = Math.max(0, Math.min(1, x / r.width));
    setCurrentTime(pct * file.duration);
  };

  const pct = (currentTime / file.duration) * 100;

  return (
    <div className="player">
      <div className="player-meta">
        <div className="pf-name mono">{file.name}</div>
        <div className="pf-sub">{file.sampleRate} · {fmt(file.duration)}</div>
      </div>
      <div className="player-controls">
        <button className="pc-btn" title="Skip back 10s" onClick={() => setCurrentTime(Math.max(0, currentTime - 10))}><I.prev /></button>
        <button className="pc-btn pc-play" onClick={() => setPlaying(!playing)}>
          {playing ? <I.pause /> : <I.play />}
        </button>
        <button className="pc-btn" title="Skip forward 10s" onClick={() => setCurrentTime(Math.min(file.duration, currentTime + 10))}><I.next /></button>
      </div>
      <div className="player-scrub">
        <span>{fmt(currentTime)}</span>
        <div className="seek" ref={seekRef} onClick={handleSeek}>
          <div className="seek-fill" style={{ width: `${pct}%` }} />
          <div className="seek-thumb" style={{ left: `${pct}%` }} />
        </div>
        <span>{fmt(file.duration)}</span>
      </div>
      <PlayerViz playing={playing} />
      <div className="player-vol">
        <I.vol style={{ width: 14, height: 14 }} />
        <div className="vol-track">
          <div className="vol-fill" style={{ width: '72%' }} />
        </div>
      </div>
    </div>
  );
}

/* ---------- Drop / mic header ---------- */
function FileIntake({ file, onSwap, recording, setRecording }) {
  const [drag, setDrag] = useState(false);
  return (
    <div
      className={`dropzone ${drag ? 'drag' : ''}`}
      onDragOver={e => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={e => { e.preventDefault(); setDrag(false); }}
    >
      <div className="dropzone-icon">
        <I.audio />
      </div>
      <div className="dropzone-meta">
        {file ? (
          <>
            <div className="dropzone-title">{file.name}</div>
            <div className="dropzone-sub">
              {file.size} · {file.sampleRate} · {fmt(file.duration)} duration
              &nbsp;·&nbsp;<span style={{ color: 'var(--violet-2)' }}>Click to replace</span>
            </div>
          </>
        ) : (
          <>
            <div className="dropzone-title">Drop audio file, or click to browse</div>
            <div className="dropzone-sub">WAV, MP3, FLAC, M4A, OGG · up to 2 GB · drag from Finder</div>
          </>
        )}
      </div>
      <div className="dropzone-divider" />
      {recording ? (
        <div style={{ flex: 1, maxWidth: 360 }}>
          <LiveWaveform active={recording} />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4, fontSize: 11, color: 'var(--text-3)' }}>
            <span className="mono" style={{ color: 'var(--red)' }}>● REC&nbsp;&nbsp;00:14.3</span>
            <span>48kHz · Built-in Mic</span>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div className="dropzone-sub" style={{ marginBottom: 8 }}>or capture live</div>
          <button className="mic-btn" onClick={() => setRecording(true)} title="Record from mic">
            <I.mic />
          </button>
        </div>
      )}
      {recording && (
        <button className="btn ghost sm" onClick={() => setRecording(false)}>
          <I.x /> Stop
        </button>
      )}
    </div>
  );
}

/* ---------- Transcript segments ---------- */
function TranscriptList({ segments, diarize, activeIdx, onJump }) {
  return (
    <div className={`transcript-list ${diarize ? '' : 'no-diarize'}`}>
      {segments.map((s, i) => {
        const spkClass = `s${s.spk}`;
        const isActive = activeIdx === i;
        return (
          <div
            key={i}
            className={`seg ${isActive ? 'active' : ''}`}
            style={{ animationDelay: `${i * 38}ms` }}
            onClick={() => onJump(s.t)}
          >
            <div className="seg-time mono">{fmtMs(s.t)}</div>
            <div className={`seg-speaker ${spkClass}`}>
              <span className="sp-dot" />
              {SPK_LABELS[s.spk]}
            </div>
            <div className="seg-text">{s.text}</div>
            <div className={`seg-conf mono ${s.conf < 0.8 ? 'low' : ''}`}>
              {(s.conf * 100).toFixed(0)}%
            </div>
          </div>
        );
      })}
      <div className="transcript-typing">
        <span /><span /><span />
        <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-3)' }}>Whisper large-v3 · processing chunk 13/14</span>
      </div>
    </div>
  );
}

/* ---------- STT Panel root ---------- */
function PanelSTT({ pushToast }) {
  const [mode, setMode] = useState('transcribe'); // 'transcribe' | 'sts'
  const [diarize, setDiarize] = useState(true);
  const [file, setFile] = useState(STT_SAMPLE_FILE);
  const [recording, setRecording] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(11.3);
  const [model, setModel] = useState('large-v3');
  const [lang, setLang] = useState('auto');

  // Active segment = whichever contains currentTime
  const activeIdx = useMemo(() => {
    return STT_SEGMENTS.findIndex(s => currentTime >= s.t && currentTime <= s.end);
  }, [currentTime]);

  const handleJump = (t) => setCurrentTime(t);

  const handleExport = (fmt) => {
    pushToast({ kind: 'success', title: `Exported ${fmt.toUpperCase()}`, msg: `${file.name.replace(/\.[^.]+$/, '')}.${fmt} saved to ~/EchoForge/exports` });
  };

  const onStsToggle = (next) => {
    setMode(next);
    if (next === 'sts') {
      pushToast({ title: 'STS Mode active', msg: 'Transcript output will auto-pipe to TTS Studio when ready.' });
    }
  };

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Speech to Text</h1>
          <p className="panel-sub">Whisper local inference · transcribe files or stream from mic</p>
        </div>
        <div className="panel-actions">
          <Segmented
            options={[
              { value: 'transcribe', label: 'Transcribe', icon: I.mic },
              { value: 'sts', label: 'STS Mode', icon: I.pipe },
            ]}
            value={mode}
            onChange={onStsToggle}
            stsAccent
          />
        </div>
      </div>

      {/* Settings bar */}
      <div className="stt-toolbar">
        <div className="row gap-2">
          <span className="field-label" style={{ margin: 0 }}>Model</span>
          <select className="select" style={{ width: 160 }} value={model} onChange={e => setModel(e.target.value)}>
            <option value="tiny">whisper-tiny · 39M</option>
            <option value="base">whisper-base · 74M</option>
            <option value="small">whisper-small · 244M</option>
            <option value="medium">whisper-medium · 769M</option>
            <option value="large-v3">whisper-large-v3 · 1.55B</option>
          </select>
        </div>
        <div className="row gap-2">
          <span className="field-label" style={{ margin: 0 }}>Language</span>
          <select className="select" style={{ width: 140 }} value={lang} onChange={e => setLang(e.target.value)}>
            <option value="auto">Auto-detect</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="ja">Japanese</option>
          </select>
        </div>
        <div style={{ flex: 1 }} />
        <Switch on={diarize} onChange={setDiarize} label="Speaker diarization" />
        <button className="btn primary">
          <I.play style={{ width: 12, height: 12 }} /> Transcribe
        </button>
      </div>

      {/* STS pipe banner when active */}
      {mode === 'sts' && (
        <div className="card glow" style={{
          padding: '12px 16px',
          marginBottom: 16,
          display: 'flex', alignItems: 'center', gap: 12,
          background: 'linear-gradient(90deg, rgba(124, 58, 237, 0.08), rgba(6, 182, 212, 0.05))',
          borderColor: 'rgba(124, 58, 237, 0.3)',
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--violet), var(--cyan))',
            display: 'grid', placeItems: 'center', color: 'white', flexShrink: 0,
          }}>
            <I.pipe style={{ width: 16, height: 16 }} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, fontWeight: 500 }}>STS pipeline active</div>
            <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
              Transcribed segments will stream to <span style={{ color: 'var(--cyan-2)' }}>TTS Studio</span> as each sentence closes. Output voice:&nbsp;
              <span style={{ color: 'var(--text-2)' }}>XTTSv2 · Aria (en-US)</span>
            </div>
          </div>
          <button className="btn ghost sm"><I.settings style={{ width: 12, height: 12 }} /> Configure</button>
        </div>
      )}

      {/* Intake */}
      <div style={{ marginBottom: 16 }}>
        <FileIntake file={file} recording={recording} setRecording={setRecording} />
      </div>

      {/* Transcript card */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="transcript-head">
          <div>
            <div className="t-title">Transcript</div>
            <div className="t-sub">
              {STT_SEGMENTS.length} segments · 92.4% avg confidence · {fmt(file.duration)} · en (auto-detected)
            </div>
          </div>
          <div className="transcript-head-actions">
            <span className="badge processing"><span className="dot" />Streaming</span>
            <button className="btn ghost sm" onClick={() => handleExport('srt')}><I.download /> SRT</button>
            <button className="btn ghost sm" onClick={() => handleExport('vtt')}><I.download /> VTT</button>
            <button className="btn ghost sm" onClick={() => handleExport('txt')}><I.download /> TXT</button>
          </div>
        </div>
        <TranscriptList
          segments={STT_SEGMENTS}
          diarize={diarize}
          activeIdx={activeIdx}
          onJump={handleJump}
        />
      </div>

      {/* Audio player */}
      <AudioPlayer
        file={file}
        playing={playing}
        setPlaying={setPlaying}
        currentTime={currentTime}
        setCurrentTime={setCurrentTime}
      />
    </div>
  );
}

Object.assign(window, { PanelSTT, AudioPlayer, PlayerViz, LiveWaveform });
