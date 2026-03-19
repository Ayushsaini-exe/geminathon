import { useState, useEffect } from 'react';
import api from '../../api/client';

export default function FarmerList() {
  const [data, setData] = useState({ farmers: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/api/manager/farmers')
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = data.farmers.filter(f =>
    f.name?.toLowerCase().includes(search.toLowerCase()) ||
    f.phone?.includes(search) ||
    f.location?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">All Farmers 👥</div>
          <div className="page-subtitle">{data.total} registered farmers</div>
        </div>
      </div>
      <div className="page-content">
        <div style={{ marginBottom: 16 }}>
          <input
            className="form-input"
            placeholder="Search by name, phone, or location..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ maxWidth: 400, background: 'var(--white)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }}
          />
        </div>

        {loading ? (
          <div className="empty-state">
            <div className="spinner" style={{ color: 'var(--green-700)', width: 32, height: 32, borderWidth: 3 }} />
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Phone</th>
                  <th>Location</th>
                  <th>Language</th>
                  <th>Joined</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(f => (
                  <tr key={f.id}>
                    <td><strong>{f.name}</strong></td>
                    <td>{f.phone}</td>
                    <td>{f.location || '—'}</td>
                    <td><span className="badge green">{f.language || 'en'}</span></td>
                    <td style={{ color: 'var(--gray-500)', fontSize: '0.85rem' }}>
                      {f.created_at ? new Date(f.created_at).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--gray-400)', padding: 32 }}>No farmers found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
