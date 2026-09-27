import React from 'react';
import { Link } from 'react-router-dom';

const Privacy = () => {
  return (
    <div style={{ maxWidth: '800px', margin: '60px auto', padding: '40px', lineHeight: '1.6', background: 'var(--panel)', borderRadius: '8px', border: '1px solid var(--border)' }}>
      <Link to="/" style={{ color: 'var(--primary)', textDecoration: 'none', marginBottom: '20px', display: 'inline-block' }}>← Back to Home</Link>
      <h1 style={{ marginBottom: '20px' }}>Privacy Policy</h1>
      <p style={{ color: 'var(--muted)' }}>Last updated: {new Date().toLocaleDateString()}</p>
      <div style={{ marginTop: '30px', color: 'var(--text)' }}>
        <p>Your privacy is important to us. It is CreatorOS's policy to respect your privacy regarding any information we may collect from you across our website, and other sites we own and operate.</p>
        <h2 style={{ marginTop: '20px', marginBottom: '10px' }}>Information we collect</h2>
        <p>We only ask for personal information when we truly need it to provide a service to you. We collect it by fair and lawful means, with your knowledge and consent.</p>
        <h2 style={{ marginTop: '20px', marginBottom: '10px' }}>How we use information</h2>
        <p>We use the information we collect in various ways, including to provide, operate, and maintain our website.</p>
      </div>
    </div>
  );
};

export default Privacy;
