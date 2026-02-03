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

  const color = useMemo(() => {
    if (isSpeaking) return '#6366f1';
    if (isListening) return '#10b981';
    if (isActive) return '#8b5cf6';
    return '#71717a';
  }, [isActive, isSpeaking, isListening]);

  return (
    <Sphere ref={meshRef} args={[1, 128, 128]}>
      <MeshDistortMaterial
        ref={materialRef}
        color={color}
        roughness={0.1}
        metalness={0.8}
        distort={0.2}
        speed={2}
        envMapIntensity={1}
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
        size={0.02}
        color="#ffffff"
        transparent
        opacity={0.3}
        sizeAttenuation
      />
    </points>
  );
}

export default function VapiVoiceWidget() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const [volumeLevel, setVolumeLevel] = useState(0);

  const vapiRef = useRef(null);
  const vapiInitialized = useRef(false);

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
          setIsConnected(true);
          setIsConnecting(false);
          setIsListening(true);
        });

        vapiRef.current.on('call-end', () => {
          setIsConnected(false);
          setIsListening(false);
          setIsSpeaking(false);
          setVolumeLevel(0);
        });

        vapiRef.current.on('speech-start', () => {
          setIsSpeaking(true);
          setIsListening(false);
        });

        vapiRef.current.on('speech-end', () => {
          setIsSpeaking(false);
          setIsListening(true);
        });

        vapiRef.current.on('volume-level', setVolumeLevel);

        vapiRef.current.on('error', (err) => {
          console.error('Vapi error:', err);
          setError(err.message || 'Error');
          setIsConnecting(false);
        });
      } catch (err) {
        setError('Failed to load Vapi');
      }
    };

    initVapi();
    return () => vapiRef.current?.stop();
  }, []);

  // Helper to get cookie value
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
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

        // Get the API key from cookie if available (optional)
        const apiKey = getCookie('api_key');

        // Build system message with optional auth
        const systemContent = apiKey
          ? `You are SECURIVA, a helpful voice assistant. Keep responses brief and conversational. [AUTH:${apiKey}]`
          : 'You are SECURIVA, a helpful voice assistant. Keep responses brief and conversational.';

        const assistantConfig = {
          name: 'SECURIVA',
          transcriber: {
            provider: 'deepgram',
            model: 'nova-2',
            language: 'en'
          },
          model: {
            provider: 'custom-llm',
            model: 'gpt-4o-mini',
            url: `${serverUrl}/api/vapi/chat/completions`,
            messages: [{
              role: 'system',
              content: systemContent
            }]
          },
          voice: {
            provider: 'deepgram',
            voiceId: 'asteria'
          },
          firstMessage: 'Hi! How can I help you today?',
          serverUrl: `${serverUrl}/api/vapi/webhook`
        };

        console.log('Starting VAPI with config:', JSON.stringify(assistantConfig, null, 2));
        await vapiRef.current.start(assistantConfig);
      }
    } catch (err) {
      console.error('VAPI start error:', err);
      setError(err.message || 'Failed to start');
      setIsConnecting(false);
    }
  };

  const statusText = error
    ? error
    : isConnecting
    ? 'Connecting...'
    : !isConnected
    ? 'Tap to speak'
    : isSpeaking
    ? 'Speaking'
    : isListening
    ? 'Listening'
    : 'Connected';

  return (
    <div className="voice-widget">
      <div className="voice-orb-section">
        <div className="voice-canvas-container" onClick={handleOrbClick}>
          <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <pointLight position={[-10, -10, -5]} intensity={0.5} color="#6366f1" />
            <AnimatedOrb
              isActive={isConnected}
              isSpeaking={isSpeaking}
              isListening={isListening}
              volume={volumeLevel}
            />
            <Particles count={50} />
            <Environment preset="night" />
          </Canvas>

          {!isConnected && !isConnecting && (
            <div className="voice-hint">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z" />
              </svg>
            </div>
          )}
        </div>
        <div className={`voice-status ${error ? 'error' : ''}`}>{statusText}</div>
      </div>
    </div>
  );
}
