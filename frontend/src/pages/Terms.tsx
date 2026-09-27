import React from 'react';
import { Link } from 'react-router-dom';

const Terms = () => {
  return (
    <div style={{ maxWidth: '800px', margin: '60px auto', padding: '40px', lineHeight: '1.6', background: 'var(--panel)', borderRadius: '8px', border: '1px solid var(--border)' }}>
      <Link to="/" style={{ color: 'var(--primary)', textDecoration: 'none', marginBottom: '20px', display: 'inline-block' }}>← Back to Home</Link>
      <h1 style={{ marginBottom: '20px' }}>Terms & Conditions</h1>
      <p style={{ color: 'var(--muted)' }}>Last updated: {new Date().toLocaleDateString()}</p>
      <div style={{ marginTop: '30px', color: 'var(--text)' }}>
        <p>These terms and conditions outline the rules and regulations for the use of CreatorOS's Website.</p>
        <h2 style={{ marginTop: '20px', marginBottom: '10px' }}>License</h2>
        <p>Unless otherwise stated, CreatorOS and/or its licensors own the intellectual property rights for all material on CreatorOS. All intellectual property rights are reserved.</p>
        <h2 style={{ marginTop: '20px', marginBottom: '10px' }}>User Responsibilities</h2>
        <p>You must not republish material from CreatorOS or reproduce, duplicate or copy material from CreatorOS without proper authorization.</p>
      </div>
    </div>
  );
};

export default Terms;
