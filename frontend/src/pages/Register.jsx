import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '', password: '', role: 'farmer',
    name: '', phone: '', location: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="logo">
          <span className="logo-icon">🌱</span>
          <span className="logo-text">AgroFix</span>
        </div>
        <h1>Create Account</h1>
        <p className="subtitle">Join the smartest agricultural platform</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>I am a</label>
            <select
              className="form-select"
              value={form.role}
              onChange={set('role')}
            >
              <option value="farmer">🌾 Farmer</option>
              <option value="manager">📊 Manager</option>
            </select>
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={form.email}
              onChange={set('email')}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Min 6 characters"
              value={form.password}
              onChange={set('password')}
              required
              minLength={6}
            />
          </div>

          {form.role === 'farmer' && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  className="form-input"
                  placeholder="Rajesh Kumar"
                  value={form.name}
                  onChange={set('name')}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  className="form-input"
                  placeholder="9876543210"
                  value={form.phone}
                  onChange={set('phone')}
                  required
                />
              </div>
              <div className="form-group">
                <label>Location (optional)</label>
                <input
                  className="form-input"
                  placeholder="Punjab, India"
                  value={form.location}
                  onChange={set('location')}
                />
              </div>
            </>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <><span className="spinner" /> Creating account...</> : 'Create Account'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
