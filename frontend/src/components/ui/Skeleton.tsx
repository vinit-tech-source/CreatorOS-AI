import { CSSProperties } from 'react';
import './Skeleton.css';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circular' | 'rectangular';
  animation?: 'pulse' | 'wave' | 'none';
  style?: CSSProperties;
}

export function Skeleton({
  className = '',
  width,
  height,
  variant = 'text',
  animation = 'pulse',
  style,
}: SkeletonProps) {
  const baseClass = 'skeleton-base';
  const variantClass = `skeleton-${variant}`;
  const animationClass = animation !== 'none' ? `skeleton-anim-${animation}` : '';

  return (
    <div
      className={`${baseClass} ${variantClass} ${animationClass} ${className}`}
      style={{ width, height, ...style }}
    />
  );
}
