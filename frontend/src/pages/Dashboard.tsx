import React from 'react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (
    <>
      <div className="header" style={{ background: 'var(--secondary-color)', color: 'white' }}>
        <div>
          <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--accent-color)' }}>Hardware Direct</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>PO Receipt Tool</div>
        </div>
      </div>
      <div className="container">
        <div className="card">
          <h2>Welcome to Hardware Direct PO Receipt Tool!</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            🔧 Scan delivery dockets to receive stock into Cin7 Omni
          </p>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>⚡ Quick Actions</h3>
          <Link to="/capture" className="btn btn-primary btn-block mb-4">
            📦 Scan New Delivery Docket
          </Link>
          <Link to="/history" className="btn btn-outline btn-block">
            📋 View Receipt History
          </Link>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>How it works</h3>
          <ol style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>Take a photo or upload a delivery docket</li>
            <li>Review and edit extracted information</li>
            <li>Match to Purchase Order in Cin7</li>
            <li>Confirm line item quantities</li>
            <li>Submit receipt to Cin7</li>
          </ol>
        </div>
      </div>
    </>
  );
}
