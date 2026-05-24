import { useState, useEffect, useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Sphere, Environment } from '@react-three/drei';
import * as THREE from 'three';
import './VapiVoiceWidget.css';

// Animated 3D Orb component
function AnimatedOrb({ isActive, isSpeaking, isListening, volume }) {
  const meshRef = useRef();
  const materialRef = useRef();
  const smoothVolume = useRef(0);

  useFrame((state) => {
    if (!meshRef.current || !materialRef.current) return;

    const time = state.clock.elapsedTime;
    smoothVolume.current += (volume - smoothVolume.current) * 0.1;
    const v = smoothVolume.current;

    meshRef.current.rotation.y = time * 0.15;
    meshRef.current.rotation.x = Math.sin(time * 0.1) * 0.1;

    let targetScale = 1;
    if (isActive) {
      targetScale = 1 + v * 0.3;
    }
    meshRef.current.scale.lerp(
      new THREE.Vector3(targetScale, targetScale, targetScale),
      0.1
    );

    if (materialRef.current) {
      let distort = 0.2;
      let speed = 2;

      if (isSpeaking) {
        distort = 0.3 + v * 0.4;
        speed = 4 + v * 4;
      } else if (isListening) {
        distort = 0.25 + v * 0.3;
        speed = 3 + v * 3;
      } else if (!isActive) {
        distort = 0.15;
        speed = 1.5;
      }

      materialRef.current.distort = THREE.MathUtils.lerp(
        materialRef.current.distort,
        distort,
        0.1
      );
      materialRef.current.speed = THREE.MathUtils.lerp(
        materialRef.current.speed,
        speed,
        0.1
      );
    }
  });

  // Dark-theme palette — brighter blues visible on deep navy field, red for speech
  const color = useMemo(() => {
    if (isSpeaking) return '#ef4444';   // Securiva red — arterial
    if (isListening) return '#60a5fa';  // bright Securiva blue — attentive
    if (isActive) return '#3d5fa8';     // Securiva mid-blue — just-connected
    return '#4a5890';                   // lifted navy that reads on dark
  }, [isActive, isSpeaking, isListening]);

  return (
    <Sphere ref={meshRef} args={[1, 128, 128]}>
      <MeshDistortMaterial
        ref={materialRef}
        color={color}
        roughness={0.28}
        metalness={0.6}
        distort={0.2}
        speed={2}
        envMapIntensity={0.75}
      />
    </Sphere>
  );
}

// Particles background
function Particles({ count = 50 }) {
  const mesh = useRef();
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    return pos;
  }, [count]);

  useFrame((state) => {
    if (mesh.current) {
      mesh.current.rotation.y = state.clock.elapsedTime * 0.02;
      mesh.current.rotation.x = state.clock.elapsedTime * 0.01;
    }
  });

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.018}
        color="#9fb0d5"
        transparent
        opacity={0.45}
        sizeAttenuation
      />
    </points>
  );
}

function formatElapsed(ms) {
  if (!Number.isFinite(ms) || ms < 0) return '00:00';
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const ss = (s % 60).toString().padStart(2, '0');
  const mm = m.toString().padStart(2, '0');
  return `${mm}:${ss}`;
}

export default function VapiVoiceWidget() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [startedAt, setStartedAt] = useState(null);
  const [elapsed, setElapsed] = useState(0);

  const vapiRef = useRef(null);
  const vapiInitialized = useRef(false);

  // Tick elapsed while a call is live
  useEffect(() => {
    if (!startedAt) return;
    const id = setInterval(() => setElapsed(Date.now() - startedAt), 250);
    return () => clearInterval(id);
  }, [startedAt]);

  // Pre-warm the backend's semantic tool index as soon as the widget mounts.
  // Fire-and-forget — by the time the user taps to speak, the 280-tool
  // embedding index for their connected toolkits is already built, so the
  // first voice turn skips the ~3s cold-start penalty.
  useEffect(() => {
    let cancelled = false;
    fetch('/api/voice/prewarm', {
      method: 'POST',
      credentials: 'include',
    }).catch(() => {
      if (!cancelled) console.warn('[VOICE] prewarm failed (non-fatal)');
    });
    return () => { cancelled = true; };
  }, []);

  // Initialize Vapi (only once)
  useEffect(() => {
    if (vapiInitialized.current) return;
    vapiInitialized.current = true;

    const initVapi = async () => {
      try {
        const VapiModule = await import('@vapi-ai/web');
        const Vapi = VapiModule.default;
        const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY;

        if (!publicKey) {
          setError('Configure VITE_VAPI_PUBLIC_KEY');
          return;
        }

        vapiRef.current = new Vapi(publicKey);

        vapiRef.current.on('call-start', () => {
          console.log('[VAPI] call-start');
          setIsConnected(true);
          setIsConnecting(false);
          setIsListening(true);
          setStartedAt(Date.now());
          setElapsed(0);
        });

        vapiRef.current.on('call-end', () => {
          console.log('[VAPI] call-end');
          setIsConnected(false);
          setIsListening(false);
          setIsSpeaking(false);
          setVolumeLevel(0);
          setStartedAt(null);
        });

        vapiRef.current.on('speech-start', () => {
          console.log('[VAPI] speech-start (assistant is speaking)');
          setIsSpeaking(true);
          setIsListening(false);
        });

        vapiRef.current.on('speech-end', () => {
          console.log('[VAPI] speech-end (assistant stopped speaking)');
          setIsSpeaking(false);
          setIsListening(true);
        });

        vapiRef.current.on('volume-level', (level) => {
          if (level > 0.01) {
            console.log('[VAPI] volume-level:', level.toFixed(3));
          }
          setVolumeLevel(level);
        });

        // Log every message from VAPI (transcripts, function calls, etc.)
        vapiRef.current.on('message', (msg) => {
          console.log('[VAPI] message:', msg.type, msg);
          // Specifically highlight transcript messages
          if (msg.type === 'transcript') {
            console.log(`[VAPI] TRANSCRIPT (${msg.transcriptType}): "${msg.transcript}"`);
          }
          if (msg.type === 'conversation-update') {
            console.log('[VAPI] conversation-update:', JSON.stringify(msg.conversation?.slice(-2), null, 2));
          }
        });

        vapiRef.current.on('error', (err) => {
          console.error('[VAPI] error:', err);
          // Extract a string message — Vapi sometimes nests objects, so coerce safely
          const raw = err?.error?.message ?? err?.message ?? '';
          const errMsg = typeof raw === 'string' ? raw : JSON.stringify(raw);
          // Ignore Daily/Krisp cleanup errors that fire after call ends
          if (errMsg.includes('KrispInitError') || errMsg.includes('ejection')) {
            console.warn('[VAPI] Ignoring cleanup error:', errMsg);
            return;
          }
          setError(errMsg || 'Error');
          setIsConnecting(false);
        });
      } catch (err) {
        setError('Failed to load Vapi');
      }
    };

    initVapi();
    return () => vapiRef.current?.stop();
  }, []);

  // Fetch a short-lived voice session JWT from backend
  // The raw API key never leaves browser↔backend; only this JWT goes to VAPI
  const fetchVoiceSession = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/voice-session', {
        method: 'POST',
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        return data.voice_token;
      }
    } catch (e) {
      console.warn('Could not fetch voice session:', e);
    }
    return null;
  };

  const handleOrbClick = async () => {
    if (isConnected) {
      vapiRef.current?.stop();
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Request microphone permission and find the real device
      let selectedDeviceId = null;
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioTrack = stream.getAudioTracks()[0];
        selectedDeviceId = audioTrack.getSettings().deviceId;
        console.log('[MIC] Using:', audioTrack.label, 'deviceId:', selectedDeviceId);
        stream.getTracks().forEach(track => track.stop());
      } catch (micErr) {
        setError('Microphone access denied');
        setIsConnecting(false);
        return;
      }

      // Explicitly set the input device on VAPI so Daily uses the right mic
      if (selectedDeviceId && vapiRef.current.setInputDevicesAsync) {
        try {
          await vapiRef.current.setInputDevicesAsync(selectedDeviceId);
          console.log('[MIC] Set VAPI input device to:', selectedDeviceId);
        } catch (e) {
          console.warn('[MIC] setInputDevicesAsync failed, trying setInputDevice:', e);
          try {
            vapiRef.current.setInputDevice?.(selectedDeviceId);
          } catch (e2) {
            console.warn('[MIC] setInputDevice also failed:', e2);
          }
        }
      }
      const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID;
      if (assistantId) {
        await vapiRef.current.start(assistantId);
      } else {
        const serverUrl = import.meta.env.VITE_VAPI_SERVER_URL;
        if (!serverUrl) {
          setError('Set VITE_VAPI_SERVER_URL (ngrok URL)');
          setIsConnecting(false);
          return;
        }

        // Fetch a short-lived voice session JWT (raw API key stays in browser↔backend)
        const voiceToken = await fetchVoiceSession();

        const assistantConfig = {
          name: 'SECURIVA',

          // Pass voice session JWT via metadata (not in system message)
          metadata: voiceToken ? { voiceToken } : {},

          // STT: Nova-3 is faster than Nova-2
          transcriber: {
            provider: 'deepgram',
            model: 'nova-3',
            language: 'en',
          },

          // LLM: Custom endpoint with capped tokens
          model: {
            provider: 'custom-llm',
            model: 'gpt-4o-mini',
            url: `${serverUrl}/api/vapi/chat/completions`,
            messages: [{
              role: 'system',
              content: 'You are SECURIVA, a voice assistant with Gmail, Calendar, and Salesforce tools. Be brief (1-2 sentences). Prefer single tool calls when possible.'
            }],
            maxTokens: 150,
            temperature: 0.3,
          },

          // TTS: Cartesia Sonic 3 (~40-90ms TTFB vs ~100ms for VAPI built-in)
          voice: {
            provider: 'cartesia',
            voiceId: '228fca29-3a0a-435c-8728-5cb483251068', // Kiefer - clear male voice
          },

          firstMessage: 'Hi! How can I help you today?',
          serverUrl: `${serverUrl}/api/vapi/events`,
          silenceTimeoutSeconds: 20,

          // Turn detection: Aggressive settings to eliminate dead air
          // Default onNoPunctuationSeconds is 1.5s (!) - this kills latency
          startSpeakingPlan: {
            waitSeconds: 0.2,
            smartEndpointingPlan: {
              provider: 'livekit',
              waitFunction: '200 + 4000 * x',
            },
            transcriptionEndpointingPlan: {
              onPunctuationSeconds: 0.05,
              onNoPunctuationSeconds: 0.6,
              onNumberSeconds: 0.3,
            },
          },
          stopSpeakingPlan: {
            numWords: 3,
            voiceSeconds: 0.5,
            backoffSeconds: 1.0,
          },
        };

        console.log('Starting VAPI with config:', JSON.stringify(assistantConfig, null, 2));
        const startResult = await vapiRef.current.start(assistantConfig);
        console.log('[VAPI] start() returned:', startResult);
      }
    } catch (err) {
      console.error('[VAPI] start error:', err);
      console.error('[VAPI] start error detail:', JSON.stringify(err, Object.getOwnPropertyNames(err)));
      setError(err.message || 'Failed to start');
      setIsConnecting(false);
    }
  };

  // Three layers of status expression — serif display, uppercase mono sub, top chip word
  const displayText = error
    ? error
    : isConnecting
    ? 'Connecting'
    : !isConnected
    ? 'Tap to speak'
    : isSpeaking
    ? 'Speaking'
    : isListening
    ? 'Listening'
    : 'Connected';

  const subLabel = error
    ? 'error'
    : isConnecting
    ? 'securing channel'
    : !isConnected
    ? 'ready when you are'
    : isSpeaking
    ? 'the agent is responding'
    : isListening
    ? 'your turn — go ahead'
    : 'standing by';

  const chipWord = error
    ? 'Error'
    : !isConnected
    ? 'Idle'
    : isSpeaking
    ? 'Out'
    : isListening
    ? 'In'
    : 'Live';

  // Reactive halo — scale/opacity follow volume + connection state
  const haloScale = 1 + volumeLevel * 0.22 + (isConnected ? 0.08 : 0);
  const haloOpacity = error
    ? 0.35
    : isSpeaking
    ? 0.95
    : isListening
    ? 0.7
    : isConnected
    ? 0.55
    : 0.35;

  // Halo — brighter on dark to register: Securiva blue at rest, bright blue listening, RED on speech
  let haloColorA, haloColorB;
  if (error) {
    haloColorA = "rgba(239, 68, 68, 0.55)";
    haloColorB = "rgba(239, 68, 68, 0.18)";
  } else if (isSpeaking) {
    haloColorA = "rgba(239, 68, 68, 0.65)";
    haloColorB = "rgba(239, 68, 68, 0.2)";
  } else if (isListening) {
    haloColorA = "rgba(96, 165, 250, 0.55)";
    haloColorB = "rgba(96, 165, 250, 0.18)";
  } else {
    haloColorA = "rgba(37, 99, 235, 0.45)";
    haloColorB = "rgba(37, 99, 235, 0.14)";
  }

  return (
    <div className="voice-widget">
      <div className="voice-top-mark">
        <span
          className={`dot ${error ? 'error' : isConnected || isConnecting ? 'live' : ''}`}
        />
        <span>{chipWord}</span>
      </div>
      <div className="voice-timer">
        {isConnected || isConnecting ? formatElapsed(elapsed) : '00:00'}
      </div>

      <div className="voice-chamber">
        <div className="voice-orb-section">
          <div
            className="voice-halo"
            style={{
              '--halo-scale': haloScale,
              '--halo-opacity': haloOpacity,
              '--halo-color-a': haloColorA,
              '--halo-color-b': haloColorB,
            }}
          />
          <div className="voice-canvas-container" onClick={handleOrbClick}>
            <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
              <ambientLight intensity={0.35} />
              <directionalLight
                position={[6, 8, 5]}
                intensity={0.9}
                color="#cfd8ff"
              />
              <pointLight
                position={[-8, -4, -4]}
                intensity={0.7}
                color={isSpeaking ? '#ef4444' : '#60a5fa'}
              />
              <AnimatedOrb
                isActive={isConnected}
                isSpeaking={isSpeaking}
                isListening={isListening}
                volume={volumeLevel}
              />
              <Particles count={42} />
              <Environment preset="night" />
            </Canvas>

            <div className="voice-ground" />
          </div>

          <div className="voice-caption">
            <div
              className={`voice-caption-display ${
                error
                  ? 'error'
                  : isSpeaking
                  ? 'speaking'
                  : !isConnected
                  ? 'muted'
                  : ''
              }`}
            >
              {displayText}
            </div>
            {!error && (
              <div className="voice-caption-sub">{subLabel}</div>
            )}
          </div>
        </div>
      </div>

      <div className="voice-dock">
        <span className="tip">
          {isConnected
            ? 'Click the orb to end the call.'
            : 'Click the orb to begin — microphone required.'}
        </span>
        <span>Cartesia Sonic · Deepgram Nova-3</span>
      </div>

      <div className="voice-accent-line" />
    </div>
  );
}
