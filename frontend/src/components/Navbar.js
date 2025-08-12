import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false); // TODO: Replace with actual auth state
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const navigate = useNavigate();

  const handleGetAlerts = () => {
    navigate('/get-alerts');
  };

  const handleSignOut = () => {
    setIsLoggedIn(false);
    setShowUserMenu(false);
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-left">
          <Link to="/" className="nav-logo">
            <span className="logo-text">InsideX</span>
          </Link>
        </div>

        <div className="nav-center">
          <Link to="/trades" className="nav-link">Trades Database</Link>
          <Link to="/methodology" className="nav-link">Methodology</Link>
        </div>

        <div className="nav-right">
          {!isLoggedIn ? (
            <>
              <button className="nav-cta" onClick={handleGetAlerts}>
                Get Alerts
              </button>
              <Link to="/signin" className="nav-auth">Sign In</Link>
              <Link to="/signup" className="nav-auth">Sign Up</Link>
            </>
          ) : (
            <>
              <button className="nav-cta" onClick={handleGetAlerts}>
                Get Alerts
              </button>
              
              <div className="nav-notifications">
                <button 
                  className="notifications-btn"
                  onClick={() => setShowNotifications(!showNotifications)}
                >
                  🔔
                  <span className="notification-badge">3</span>
                </button>
                
                {showNotifications && (
                  <div className="notifications-dropdown">
                    <div className="notifications-header">
                      <h4>Recent Alerts</h4>
                    </div>
                    <div className="notification-item">
                      <span className="ticker">AAPL</span>
                      <span className="alert-text">CEO sold 10,000 shares</span>
                      <span className="time">2h ago</span>
                    </div>
                    <div className="notification-item">
                      <span className="ticker">TSLA</span>
                      <span className="alert-text">CFO bought 5,000 shares</span>
                      <span className="time">4h ago</span>
                    </div>
                    <div className="notification-item">
                      <span className="ticker">MSFT</span>
                      <span className="alert-text">CTO sold 15,000 shares</span>
                      <span className="time">6h ago</span>
                    </div>
                    <Link to="/notifications" className="view-all">View All</Link>
                  </div>
                )}
              </div>

              <div className="nav-user">
                <button 
                  className="user-avatar"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  👤
                </button>
                
                {showUserMenu && (
                  <div className="user-dropdown">
                    <Link to="/my-alerts" className="dropdown-item">
                      📊 My Alerts
                    </Link>
                    <Link to="/watchlists" className="dropdown-item">
                      👀 Watchlists
                    </Link>
                    <Link to="/account" className="dropdown-item">
                      ⚙️ Account
                    </Link>
                    <div className="dropdown-divider"></div>
                    <button onClick={handleSignOut} className="dropdown-item">
                      🚪 Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 