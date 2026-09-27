import { Canvas } from '@react-three/fiber';
import { Float, Text, Box } from '@react-three/drei';
import { Suspense, useMemo } from 'react';

interface AnalyticsChart3DProps {
  data: { date: string; engagement: number }[];
}

export function AnalyticsChart3D({ data }: AnalyticsChart3DProps) {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Ensure data fits within a manageable width (e.g. 10 bars max)
  const displayData = useMemo(() => {
    return data.slice(-10);
  }, [data]);

  const maxEngagement = useMemo(() => {
    if (displayData.length === 0) return 1;
    return Math.max(...displayData.map(d => d.engagement), 1);
  }, [displayData]);

  if (displayData.length === 0) {
    return (
      <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        Not enough historical data to display 3D trends.
      </div>
    );
  }

  return (
    <div style={{ height: '300px', width: '100%', position: 'relative' }}>
      <Canvas camera={{ position: [0, 2, 8], fov: 40 }} aria-hidden="true">
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} color="#4f46e5" />
        <directionalLight position={[-10, -10, -5]} intensity={0.5} color="var(--panel-2)" />

        <Suspense fallback={null}>
          <Float speed={prefersReducedMotion ? 0 : 1} rotationIntensity={prefersReducedMotion ? 0 : 0.1} floatIntensity={prefersReducedMotion ? 0 : 0.2}>
            <group position={[0, -1.5, 0]}>
              {displayData.map((d, index) => {
                const height = (d.engagement / maxEngagement) * 3; // Max height of 3 units
                const xOffset = (index - displayData.length / 2) * 1.2 + 0.6; // Spread bars out
                
                return (
                  <group key={index} position={[xOffset, 0, 0]}>
                    <Box args={[0.8, height, 0.8]} position={[0, height / 2, 0]}>
                      <meshStandardMaterial color="#6366f1" roughness={0.2} metalness={0.8} opacity={0.9} transparent />
                    </Box>
                    <Text
                      position={[0, -0.3, 0]}
                      fontSize={0.2}
                      color="#f8fafc"
                      anchorX="center"
                      anchorY="middle"
                    >
                      {d.date.split(',')[0]}
                    </Text>
                    <Text
                      position={[0, height + 0.3, 0]}
                      fontSize={0.25}
                      color="var(--panel-2)"
                      anchorX="center"
                      anchorY="middle"
                      fontWeight="bold"
                    >
                      {d.engagement.toFixed(1)}%
                    </Text>
                  </group>
                );
              })}
            </group>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
