import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
// @ts-ignore
import * as random from 'maath/random/dist/maath-random.esm';
import { useState, useRef, Suspense } from 'react';
import { Card, CardContent } from '../../../../components/ui/Card';

function ParticleCloud() {
  const ref = useRef<any>();
  // Use maath for efficient random point generation in a sphere
  const [sphere] = useState(() => random.inSphere(new Float32Array(5000), { radius: 1.5 }));

  useFrame((_state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10;
      ref.current.rotation.y -= delta / 15;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
        <PointMaterial transparent color="#6366f1" size={0.015} sizeAttenuation={true} depthWrite={false} />
      </Points>
    </group>
  );
}

export function AIStudio3D() {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <Card glass>
      <CardContent className="p-0">
        <div style={{ position: 'relative', width: '100%', height: '350px', background: '#020617', borderRadius: 'var(--radius-xl)', overflow: 'hidden' }}>
          
          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
            <h2 className="text-xl font-bold text-white mb-2" style={{ textShadow: '0 2px 10px rgba(0,0,0,0.8)' }}>
              Synthesizing Content
            </h2>
            <p className="text-secondary" style={{ textShadow: '0 2px 5px rgba(0,0,0,0.8)' }}>
              Analyzing requirements and generating draft...
            </p>
          </div>

          <Canvas camera={{ position: [0, 0, 3] }} aria-hidden="true">
            <Suspense fallback={null}>
              {!prefersReducedMotion ? (
                <ParticleCloud />
              ) : (
                <mesh>
                  <sphereGeometry args={[1, 16, 16]} />
                  <meshBasicMaterial color="#6366f1" wireframe opacity={0.3} transparent />
                </mesh>
              )}
            </Suspense>
          </Canvas>

        </div>
      </CardContent>
    </Card>
  );
}
