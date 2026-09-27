import { Canvas } from '@react-three/fiber';
import { Float, Sparkles, Stars } from '@react-three/drei';
import { Suspense } from 'react';
import styles from './AppShell3D.module.css';

export function AppShell3D() {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div className={styles.canvasContainer} aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <color attach="background" args={['var(--panel-2)']} />
        
        {/* Ambient lighting */}
        <ambientLight intensity={0.2} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} color="#6366f1" />
        <directionalLight position={[-10, -10, -5]} intensity={0.8} color="var(--panel-2)" />

        <Suspense fallback={null}>
          {!prefersReducedMotion && (
            <>
              <Float speed={1} rotationIntensity={0.5} floatIntensity={0.5}>
                <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
                <Sparkles count={50} scale={10} size={2} speed={0.4} opacity={0.2} color="#6366f1" />
              </Float>
            </>
          )}
          {prefersReducedMotion && (
            <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={0} />
          )}
        </Suspense>
      </Canvas>
    </div>
  );
}
