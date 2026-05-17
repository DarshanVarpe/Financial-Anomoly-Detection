// frontend/src/components/TransactionRow.jsx
import React from 'react'
import { scoreClass, modelLabel } from '../utils/score'

export default function TransactionRow({ tx, onAction, cols = 9, showActions = true }) {
  const high = parseFloat(tx.ensemble_score) >= 0.9

  function ScorePill({ v }) {
    return <span className={`score-pill ${scoreClass(v)}`}>{parseFloat(v).toFixed(2)}</span>
  }

  function StatusBadge({ s }) {
    return <span className={`status-badge ${s}`}>{s.charAt(0).toUpperCase() + s.slice(1)}</span>
  }

  return (
    <tr id={`tx-row-${tx.id}`} style={high ? { background: 'rgba(220,38,38,0.04)' } : {}}>
      <td><span className="tx-id">{tx.transaction_ref}</span></td>
      <td><span className="tx-amount">${parseFloat(tx.amount).toLocaleString()}</span></td>
      <td style={{ fontSize: '11px' }}>{tx.location || '—'}</td>
      {cols >= 11 && <td style={{ fontSize: '11px' }}>{tx.merchant || '—'}</td>}
      {cols >= 11 && <td style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{tx.device || '—'}</td>}
      <td><span className={`model-tag ${tx.model_source}`}>{modelLabel(tx.model_source)}</span></td>
      <td><ScorePill v={tx.if_score} /></td>
      <td><ScorePill v={tx.lstm_score} /></td>
      <td><ScorePill v={tx.ensemble_score} /></td>
      {cols >= 11 && (
        <td style={{ maxWidth: 180, fontSize: '11px', color: 'var(--text-secondary)' }}
            title={tx.ai_explanation || ''}>
          {(tx.ai_explanation || '—').substring(0, 80)}{(tx.ai_explanation || '').length > 80 ? '…' : ''}
        </td>
      )}
      <td><StatusBadge s={tx.status} /></td>
      {showActions && (
        <td>
          <div style={{ display: 'flex', gap: 3 }}>
            <button id={`tx-${tx.id}-fraud-btn`}    className="act-btn fraud"    onClick={() => onAction(tx.id, 'fraud')}>Fraud</button>
            <button id={`tx-${tx.id}-clear-btn`}    className="act-btn clear"    onClick={() => onAction(tx.id, 'cleared')}>Clear</button>
            <button id={`tx-${tx.id}-escalate-btn`} className="act-btn escalate" onClick={() => onAction(tx.id, 'escalated')}>↑</button>
          </div>
        </td>
      )}
    </tr>
  )
}
