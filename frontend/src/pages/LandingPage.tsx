import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Sparkles, Zap, Globe, Layers } from 'lucide-react';
import styles from './LandingPage.module.css';

// 3D Imports
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Stars, TorusKnot } from '@react-three/drei';
import { useRef } from 'react';

// Floating 3D Object Component
function AnimatedTorus() {
  const meshRef = useRef<any>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <TorusKnot ref={meshRef} args={[9, 2.5, 256, 32]} position={[0, 0, -10]}>
        <meshPhysicalMaterial 
          color="#6366f1"
          metalness={0.9}
          roughness={0.1}
          clearcoat={1}
          clearcoatRoughness={0.1}
          transmission={0.5}
          thickness={2}
          envMapIntensity={2}
        />
      </TorusKnot>
    </Float>
  );
}

export function LandingPage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className={styles.container}>
      
      {/* 3D WebGL Background */}
      <div className={styles.canvasContainer}>
        <Canvas camera={{ position: [0, 0, 20], fov: 45 }}>
          <color attach="background" args={['#0b1120']} />
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={2} color="#818cf8" />
          <directionalLight position={[-10, -10, -5]} intensity={1} color="#0ea5e9" />
          
          <AnimatedTorus />
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        </Canvas>
      </div>

      {/* Main UI Hero Card */}
      <Card glass className={styles.heroCard}>
        <CardContent className={styles.heroContent}>
          
          <div className={styles.badge}>
            <Sparkles size={16} className="text-warning" />
            Introducing CreatorOS AI
          </div>

          <h1 className={styles.title}>
            The 3D Engine for <br />
            <span>Content Creation</span>
          </h1>

          <p className={styles.subtitle}>
            Automate your social presence, generate stunning content with AI, and manage your entire brand workflow in one beautiful workspace.
          </p>

          <div className={styles.buttonGroup}>
            <Link to="/register">
              <Button size="lg" className="w-full">
                Get Started Free
              </Button>
            </Link>
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button size="lg" variant="secondary" className="w-full">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <Link to="/login">
                <Button size="lg" variant="secondary" className="w-full">
                  Login to Workspace
                </Button>
              </Link>
            )}
          </div>
          
        </CardContent>
      </Card>

      {/* Feature 3D Cards */}
      <div className={styles.featuresGrid}>
        
        <Card glass className={styles.featureCard}>
          <CardContent className={styles.featureContent}>
            <div className={`${styles.iconWrapper} ${styles.iconAutomation}`}>
              <Zap size={28} className={styles.icon} />
            </div>
            <h3 className={styles.featureTitle}>AI Automation</h3>
            <p className={styles.featureDesc}>Set up powerful IF-THEN triggers to automatically generate content.</p>
          </CardContent>
        </Card>

        <Card glass className={styles.featureCard}>
          <CardContent className={styles.featureContent}>
            <div className={`${styles.iconWrapper} ${styles.iconBrand}`}>
              <Layers size={28} className={styles.icon} />
            </div>
            <h3 className={styles.featureTitle}>Brand Kits</h3>
            <p className={styles.featureDesc}>Maintain perfect brand consistency with AI trained on your unique voice.</p>
          </CardContent>
        </Card>

        <Card glass className={styles.featureCard}>
          <CardContent className={styles.featureContent}>
            <div className={`${styles.iconWrapper} ${styles.iconKnowledge}`}>
              <Globe size={28} className={styles.icon} />
            </div>
            <h3 className={styles.featureTitle}>Knowledge Base</h3>
            <p className={styles.featureDesc}>Upload your documents and links to give the AI context about your business.</p>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
