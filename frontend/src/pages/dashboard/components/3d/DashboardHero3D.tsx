import { Canvas } from '@react-three/fiber';
import { Float, MeshDistortMaterial, RoundedBox } from '@react-three/drei';
import { Suspense } from 'react';

export function DashboardHero3D({ workspaceName }: { workspaceName: string }) {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div style={{ height: '300px', width: '100%', borderRadius: '1rem', overflow: 'hidden', position: 'relative', marginBottom: '1.5rem', background: 'var(--border)', border: '1px solid var(--border-color)' }}>
      {/* Absolute DOM overlay for accessible text */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', pointerEvents: 'none', zIndex: 10 }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 800, textShadow: '0 4px 20px var(--border-strong)', margin: 0, color: '#fff' }}>Dashboard</h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>Welcome to {workspaceName}</p>
      </div>

      <Canvas camera={{ position: [0, 0, 8], fov: 40 }} style={{ pointerEvents: 'none' }} aria-hidden="true">
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} color="#4f46e5" />
        <directionalLight position={[-10, -10, -5]} intensity={0.5} color="var(--panel-2)" />

        <Suspense fallback={null}>
          <Float speed={prefersReducedMotion ? 0 : 2} rotationIntensity={prefersReducedMotion ? 0 : 0.5} floatIntensity={prefersReducedMotion ? 0 : 1}>
            <RoundedBox args={[4, 2.5, 0.5]} radius={0.1} smoothness={4} position={[0, 0, -2]}>
              <MeshDistortMaterial color="var(--panel-2)" distort={prefersReducedMotion ? 0 : 0.2} speed={prefersReducedMotion ? 0 : 2} roughness={0.2} metalness={0.8} opacity={0.5} transparent />
            </RoundedBox>
          </Float>
          
          <Float speed={prefersReducedMotion ? 0 : 3} rotationIntensity={prefersReducedMotion ? 0 : 1.5} floatIntensity={prefersReducedMotion ? 0 : 2}>
            <mesh position={[2.5, 1, -1]}>
              <torusGeometry args={[0.5, 0.15, 16, 32]} />
              <meshStandardMaterial color="#3b82f6" roughness={0.1} metalness={1} />
            </mesh>
          </Float>
          
          <Float speed={prefersReducedMotion ? 0 : 2.5} rotationIntensity={prefersReducedMotion ? 0 : 2} floatIntensity={prefersReducedMotion ? 0 : 1.5}>
            <mesh position={[-2.5, -1, 1]}>
              <octahedronGeometry args={[0.6]} />
              <meshStandardMaterial color="#6366f1" roughness={0.1} metalness={0.8} />
            </mesh>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
