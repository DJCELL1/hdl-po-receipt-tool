// This file contains stub implementations for the remaining pages
// In production, each would be in its own file with full implementation

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../services/api';

// Review Extraction Page
export function ReviewExtraction() {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(location.state?.extractedData || {});

  return (
    <>
      <div className="header">
        <h1>Review Extraction</h1>
      </div>
      <div className="container">
        <div className="card">
          <h3>Extracted Information</h3>
          <div className="form-group">
            <label>Supplier</label>
            <input className="input" value={data.supplierName || ''} onChange={(e) => setData({...data, supplierName: e.target.value})} />
          </div>
          <div className="form-group">
            <label>PO Reference</label>
            <input className="input" value={data.poReference || ''} onChange={(e) => setData({...data, poReference: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Docket Number</label>
            <input className="input" value={data.docketNumber || ''} onChange={(e) => setData({...data, docketNumber: e.target.value})} />
          </div>
          <button className="btn btn-primary btn-block" onClick={() => navigate('/match-po', { state: { extractedData: data } })}>
            Continue to PO Matching
          </button>
        </div>
      </div>
    </>
  );
}

// Match PO Page
export function MatchPo() {
  const location = useLocation();
  const navigate = useNavigate();
  const [data] = useState(location.state?.extractedData || {});
  const [matches, setMatches] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPo, setSelectedPo] = useState<any>(null);

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const result = await api.matchPo({
        poReference: data.poReference,
        supplierName: data.supplierName,
        lineItems: data.lineItems
      });
      setMatches(result);
      if (result.bestMatch) {
        setSelectedPo(result.bestMatch.po);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    if (data.poReference) {
      handleSearch();
    }
  }, []);

  return (
    <>
      <div className="header">
        <h1>Match Purchase Order</h1>
      </div>
      <div className="container">
        {isLoading && <div className="loading-spinner" />}
        {matches && (
          <div className="card">
            {matches.bestMatch ? (
              <>
                <h3>Best Match Found</h3>
                <div className="badge badge-success">{matches.bestMatch.matchType} match</div>
                <p><strong>Reference:</strong> {matches.bestMatch.po.Reference}</p>
                <p><strong>Supplier:</strong> {matches.bestMatch.po.Supplier}</p>
                <p><strong>Confidence:</strong> {(matches.bestMatch.confidence * 100).toFixed(0)}%</p>
                <button
                  className="btn btn-primary btn-block mt-4"
                  onClick={() => navigate('/match-lines', { state: { po: selectedPo, extractedData: data } })}
                >
                  Continue to Line Matching
                </button>
              </>
            ) : (
              <div className="alert alert-error">No matching PO found</div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

// Match Lines Page
export function MatchLines() {
  const location = useLocation();
  const navigate = useNavigate();
  const [po] = useState(location.state?.po || {});
  const [data] = useState(location.state?.extractedData || {});
  const [lineMatches, setLineMatches] = useState<any[]>([]);

  React.useEffect(() => {
    const fetchMatches = async () => {
      try {
        const result = await api.matchLines({
          poId: po.Id,
          docketLines: data.lineItems
        });
        setLineMatches(result.lineMatches);
      } catch (err) {
        console.error(err);
      }
    };
    if (po.Id) {
      fetchMatches();
    }
  }, []);

  return (
    <>
      <div className="header">
        <h1>Match Line Items</h1>
      </div>
      <div className="container">
        <div className="card">
          <h3>Line Item Matching</h3>
          {lineMatches.map((match, idx) => (
            <div key={idx} style={{ padding: '12px', borderBottom: '1px solid var(--border-color)' }}>
              <div className="badge badge-success">{match.matchType}</div>
              <p><strong>Docket:</strong> {match.docketLine.description} (Qty: {match.docketLine.qty})</p>
              {match.poLine && (
                <p><strong>PO Line:</strong> {match.poLine.ProductDescription} (Remaining: {match.poLine.OrderedQty - match.poLine.ReceivedQty})</p>
              )}
              {match.issues.length > 0 && (
                <div className="alert alert-warning" style={{ marginTop: '8px' }}>
                  {match.issues.join(', ')}
                </div>
              )}
            </div>
          ))}
          <button
            className="btn btn-primary btn-block mt-4"
            onClick={() => navigate('/confirm', { state: { po, extractedData: data, lineMatches } })}
          >
            Continue to Confirm
          </button>
        </div>
      </div>
    </>
  );
}

// Confirm Receipt Page
export function ConfirmReceipt() {
  const location = useLocation();
  const navigate = useNavigate();
  const [po] = useState(location.state?.po || {});
  const [data] = useState(location.state?.extractedData || {});
  const [lineMatches] = useState(location.state?.lineMatches || []);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    try {
      const lineItems = lineMatches.map((match: any) => ({
        sku: match.docketLine.sku,
        description: match.docketLine.description,
        qtyDelivered: match.docketLine.qty,
        qtyReceipted: match.docketLine.qty,
        matchType: match.matchType,
        cin7LineId: match.poLine?.Id,
        cin7ProductId: match.poLine?.ProductId
      }));

      const result = await api.createReceipt({
        poId: po.Id,
        poReference: po.Reference,
        docketNumber: data.docketNumber,
        supplierName: data.supplierName,
        deliveryDate: data.deliveryDate,
        lineItems
      });

      navigate('/result', { state: { success: true, receiptId: result.receiptId } });
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('Duplicate docket detected. Do you want to proceed anyway?');
      } else {
        setError(err.response?.data?.error || 'Failed to create receipt');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="header">
        <h1>Confirm Receipt</h1>
      </div>
      <div className="container">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="card">
          <h3>Receipt Summary</h3>
          <p><strong>PO:</strong> {po.Reference}</p>
          <p><strong>Supplier:</strong> {data.supplierName}</p>
          <p><strong>Docket:</strong> {data.docketNumber}</p>
          <p><strong>Lines:</strong> {lineMatches.length}</p>
          <button
            className="btn btn-success btn-block mt-4"
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Receipt to Cin7'}
          </button>
        </div>
      </div>
    </>
  );
}

// Receipt Result Page
export function ReceiptResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const success = location.state?.success;
  const receiptId = location.state?.receiptId;

  return (
    <>
      <div className="header">
        <h1>Receipt Result</h1>
      </div>
      <div className="container">
        <div className="card text-center">
          {success ? (
            <>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>✅</div>
              <h2>Receipt Created Successfully!</h2>
              <p style={{ color: 'var(--text-secondary)', margin: '12px 0' }}>
                Receipt ID: {receiptId}
              </p>
              <button className="btn btn-primary btn-block mt-4" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </button>
              <button className="btn btn-outline btn-block mt-4" onClick={() => navigate('/history')}>
                View Receipt History
              </button>
            </>
          ) : (
            <>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>❌</div>
              <h2>Receipt Failed</h2>
              <button className="btn btn-primary btn-block mt-4" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
}

// Receipt History Page
export function ReceiptHistory() {
  const navigate = useNavigate();
  const [receipts, setReceipts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    const fetchReceipts = async () => {
      try {
        const result = await api.getReceipts();
        setReceipts(result.receipts);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReceipts();
  }, []);

  return (
    <>
      <div className="header">
        <h1>Receipt History</h1>
        <button onClick={() => navigate('/dashboard')} className="btn btn-outline">Back</button>
      </div>
      <div className="container">
        {isLoading && <div className="loading-spinner" />}
        {receipts.map((receipt) => (
          <div key={receipt.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3>{receipt.cin7_po_reference}</h3>
                <p style={{ color: 'var(--text-secondary)' }}>{receipt.supplier_name}</p>
                <p style={{ fontSize: '0.875rem' }}>
                  {new Date(receipt.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className={`badge badge-${receipt.status === 'completed' ? 'success' : 'warning'}`}>
                {receipt.status}
              </div>
            </div>
          </div>
        ))}
        {receipts.length === 0 && !isLoading && (
          <div className="card text-center">
            <p>No receipts yet</p>
          </div>
        )}
      </div>
    </>
  );
}
