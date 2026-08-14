import { ReactNode } from 'react';
import styles from './Table.module.css';

interface TableProps {
  children: ReactNode;
  className?: string;
}

export function Table({ children, className = '' }: TableProps) {
  return (
    <div className={styles.tableWrapper}>
      <table className={`${styles.table} ${className}`}>
        {children}
      </table>
    </div>
  );
}

export function TableHeader({ children }: { children: ReactNode }) {
  return <thead className={styles.header}>{children}</thead>;
}

export function TableBody({ children }: { children: ReactNode }) {
  return <tbody className={styles.body}>{children}</tbody>;
}

export function TableRow({ children, className = '' }: { children: ReactNode, className?: string }) {
  return <tr className={`${styles.row} ${className}`}>{children}</tr>;
}

export function TableHead({ children, className = '' }: { children: ReactNode, className?: string }) {
  return <th className={`${styles.head} ${className}`}>{children}</th>;
}

export function TableCell({ children, className = '' }: { children: ReactNode, className?: string }) {
  return <td className={`${styles.cell} ${className}`}>{children}</td>;
}
