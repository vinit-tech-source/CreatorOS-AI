import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Float, OrbitControls, Text } from '@react-three/drei';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import styles from './PipelineProgress.module.css';

function AgentNode({ position, color, label }: { position: [number, number, number], color: string, label: string }) {
  return (
    <group position={position}>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color={color} roughness={0.2} metalness={0.8} />
        </mesh>
        <Text
          position={[0, 1.2, 0]}
          fontSize={0.3}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {label}
        </Text>
      </Float>
    </group>
  );
}

export function PipelineProgress() {
  return (
    <div className={styles.container}>
      <PageHeader 
        title="Active Agent Pipeline" 
        subtitle="Live 3D telemetry of your LangGraph content factory." 
      />
      
      <Card glass className={styles.canvasCard}>
        <div className={styles.canvasContainer}>
          <Canvas camera={{ position: [0, 3, 8], fov: 60 }}>
            <color attach="background" args={['#09090b']} />
            <ambientLight intensity={0.3} />
            <directionalLight position={[10, 10, 5]} intensity={1.5} color="#4F46E5" />
            <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#0ea5e9" />
            
            <Suspense fallback={null}>
              <AgentNode position={[-4, 0, 0]} color="#4F46E5" label="Strategy" />
              <AgentNode position={[-2, 0, -2]} color="#0ea5e9" label="Research" />
              <AgentNode position={[0, 0, 0]} color="#10b981" label="Drafting" />
              <AgentNode position={[2, 0, -2]} color="#f59e0b" label="Review" />
              <AgentNode position={[4, 0, 0]} color="#8b5cf6" label="Publish" />
              
              <OrbitControls enableZoom={true} autoRotate autoRotateSpeed={0.5} />
            </Suspense>
          </Canvas>
        </div>
      </Card>
    </div>
  );
}
